# Rimuove i paragrafi incompleti derivanti da una conversione da PDF a EPub
#
# I paragrafi che si estendono su due pagine nel pdf vengono trattati come due
# paragrafi separati, creando nell'epub un "a capo" inutile.
#
# Inoltre corregge le sillabate sbagliate (da rivedere)
#
# es. sillaba-ta  --> sillabata

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import zipfile
import shutil
import re
from bs4 import BeautifulSoup

def getListaSillabate(paragrafo):
    """ 'cattura' la lista di sillabate da controllare in paragrafo """

    lista_sillabate = re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U )
    for sillabata in lista_sillabate:
        if sillabata.lower() in whitelist:
            print( f"sillabata presente nella WHITELIST: {sillabata} \n" )
            lista_sillabate.remove(sillabata)
        if sillabata.lower() in keeplist:
            print( f"sillabata presente nella KEEPLIST: {sillabata} \n")
            lista_sillabate.remove(sillabata)
    return lista_sillabate

def gestisciSillabata( p_tag, sillabata):
    """ gestisce la sillabata in base all'indicazione dell'utente """

    print( f"Correggo la sillabata corrente ({sillabata})? [Sì|no|whitelist] ")
    scelta_utente = input( "Scelta: [S|n|w]: " )

    match scelta_utente:
        case "n": # keeplist!
            keeplist.append( sillabata.lower() )
            print (f"{sillabata} aggiunta alla lista delle sillabate da mantenere nell'ebook")
        case "w": # whitelist!
            whitelist.append( sillabata.lower() )
            print (f"{sillabata} aggiunta alla whitelist")
        case _: # correggo la sillabata
            cambiata = sillabata.replace( '-', '' )
            for stringa in p_tag.strings:
                if sillabata in stringa:
                    nuova_stringa = stringa.replace( sillabata, cambiata )
                    stringa.replace_with( nuova_stringa )
                    break

def isParagrafoMonco( paragrafo ):
    """ controlla se il paragrafo è 'monco' """

    if paragrafo == "" :
        return False

    if re.match( r"[^.…!?:»”]", paragrafo[-1], re.U ):
        return True
    else:
        return False

def fixParagrafoMonco( p_tag, p_tag_next ):
    """ corregge il paragrafo monco """

    print( "---DEBUG: Unifico i paragrafi ---" )
    while p_tag_next.contents != []:
        p_tag.append( p_tag_next.contents[0] )

    # elimino secondo paragrafo e pulisco
    p_tag_next.decompose()
    p_tag.smooth()

def fixParagrafoMoncoSillabato( p_tag, p_tag_next ):
    """ corregge il paragrafo monco terminante con una sillabata """

    # prevede un paragrafo del tipo
    # <p class="calibre2">
    #   <span class="koboSpan" id="kobo.244.1">Dietro al banco, a sinistra dello specchio, c'era un braciere in cui si con-</span>
    # </p>
    # <p class="calibre2">
    # </p>
    # <p class="calibre2">
    #   <span class="koboSpan" id="kobo.246.1">
    #   </span>
    #   <span class="koboSpan" id="kobo.246.2">sumava lentamente della carbonella.</span>
    # </p>

    for stringa in p_tag.strings:
        if stringa.endswith( "-" ):
            # elimino eventuale "a capo" successivo
            if p_tag_next.text == "":
                # paragrafo vuoto
                p_tag_next.decompose()
                p_tag_next = p_tag.findNextSibling()
            # unisco il testo
            for item in p_tag_next.contents:
                if item.get_text() == "\n":
                    continue
                else:
                    nuova_stringa = stringa[:-1]
                    nuova_stringa += item.get_text()
                    stringa.replace_with(nuova_stringa)
                    item.extract()
                    break
            break

def unisciParagrafi( zuppa ):
    # unisce i paragrafi monchi del file html
    # i paragrafi finiscono solitamente con "." o "?" o":" o "»" o "”" o "…" o "!"
        # es. <p>Sto programmando. </p>
        # es. <p>Hai notato gli spazi finali?   </p>
        # es. <p>Paragrafi terminanti correttamente:</p>
        # es. <p>«questo è un dialogo»        </p>
        # es. <p>“anche questo è un dialogo”    </p>
        # es. <p>immagino tu stia iniziando a capire…  </p>
        # es. <p>grande giove!</p>
    # i paragrafi non dovrebbero finire con "-"
        # es. <p>corregeva le sillaba-</p><p>te e i paragrafi monchi.</p>

    # controllo paragrafi monchi in file corrente
    lista_p = zuppa.find_all( "p" )
    for p_tag, p_tag_next in zip( lista_p[:-1], lista_p[1:] ):
        paragrafo = p_tag.text.rstrip()
        # check paragrafo monco
        if isParagrafoMonco( paragrafo ):
            # check paragrafo monco sillabato
            if paragrafo.endswith( "-" ):
                # NB do per scontato che il paragrafo vada corretto
                print(f"Correggo paragrafo \n {paragrafo}\n")
                fixParagrafoMoncoSillabato( p_tag, p_tag_next )
                return

            if p_tag_next.text.rstrip() == "" :
                # TODO controllare utilità di questo passaggio
                continue

            # richiedo valutazione dell'utente
            print( "\n@@@ trovato paragrafo errato: " )
            print( repr(paragrafo) )
            print( repr( p_tag_next.text.rstrip() ))
            unificare = input( "unifico i paragrafri? [S|n]: ")
            if unificare != 'n':
                fixParagrafoMonco( p_tag, p_tag_next )


def correggiSillabate( zuppa ):
    """ cerca e corregge sillabate errate """

    # aggiusta sillabate classiche e sillabate monche
    #
    # sillabata classica: <p>Si divertiva mol-to a scrivere</p>
    #
    # sillabata monca: <p> Saltava nel cor-<span>\n</span>tile.</p>

    # controllo paragrafi contenenti le sillabate
    for p_tag in zuppa.find_all( "p" ):
        paragrafo = p_tag.text
        # controllo sillabate classiche
        for sillabata in getListaSillabate( paragrafo ):
            # isolo frase del paragrafo
            for frase in paragrafo.split( "." ):
                if sillabata in frase:
                    print( f"FRASE: {frase.lstrip()}." )
                    break
            gestisciSillabata( p_tag, sillabata )
        # controllo sillabate monche
        if "-\n" in paragrafo:
            # DEBUG
            print( f"---DEBUG: {paragrafo} ---" )
            stringa = p_tag.strings
            while True:
                stringa_corrente = next(stringa)
                if stringa_corrente != "" and stringa_corrente[-1] == "-":
                    stringa_successiva = next(stringa)
                    # tolgo il trattino finale
                    stringa_corrente.replace_with( stringa_corrente[:-1] )
                    # tolgo l'a capo
                    stringa_successiva.replace_with( "" )
                    break


def salvaModifiche( zuppa, file_html ):
    # salva le modifiche apportate nel file html
    
    with open( working_dir + file_html, "wt" ) as f:
        f.write( str( zuppa ) )
        print( f"--- SALVATO {file_html} \n" )

def salvaWhitelist():
    """ salva la whitelist aggiornata su HD """
    
    if whitelist != []:
        try:
            with open( "whitelist.txt", 'a' ) as f:
                for parola in whitelist[original_lenght:]:
                    f.write( f"{parola}\n" )
        except:
            print( "CHI HA CANCELLATO IL FILE?!?!!? \n" )

def ricreaEpub():
    print( "--- MODIFICHE TERMINATE --- \n" )
    # ricreo il file epub
    shutil.make_archive("ebook MODIFICATO", "zip", ".epubunzipped")
    os.rename("ebook MODIFICATO.zip", "ebook MODIFICATO.epub")
    print("File ripulito salvato in: ebook MODIFICATO.epub")

######----------                          MAIN                          ----------######
try:
    ePub = sys.argv[1]
except IndexError:
    print( "ERRORE - Indicare il file da 'pulire'" )
    print( "Utilizzo:" )
    print( "python epubcleanerCLI.py file_da_pulire.epub" )
    raise SystemExit()

if os.path.splitext(ePub)[1].lower() != ".epub":
    print( "ERRORE - Il file da 'pulire' deve avere estensione .epub" )
    print( "Utilizzo:" )
    print( "python epubcleanerCLI.py file_da_pulire.epub" )
    raise SystemExit()

working_dir = "./.epubunzipped/"
# rimuovo vecchia directory working_dir

shutil.rmtree( working_dir, ignore_errors=True )

# scompatto il libro (la directory è creata automaticamente)
try:
    with zipfile.ZipFile( ePub, 'r' ) as f:
        f.extractall( working_dir )
except FileNotFoundError:
    print( "ERRORE - Impossibile trovare il file indicato" )
    print( "Utilizzo:" )
    print( "python epubcleanerCLI.py file_da_pulire.epub" )
    print( "file_da_pulire.epub deve trovarsi nella stessa cartella di epubcleanerCLI.py" )
    raise SystemExit()

# ricerco directory contenente i file html da controllare
possible_files_dir = ["OEBPS/Text",
                      "OEBPS/text",
                      "OEBPS",
                      "text"]
for directory in possible_files_dir:
    if os.path.exists( working_dir + directory):
        working_dir = f"{working_dir}{directory}/"
        break

# creo lista file html da controllare
lista_file = []
for file in os.listdir( working_dir ):
    if file.endswith( "html" ) or file.endswith( "htm" ):
        lista_file.append( file )

lista_file.sort()
print( "lista file: {}\n".format( lista_file ))

# controllo paragrafi monchi?
check_paragrafi = input( "Eseguo controllo su paragrafi monchi? [S|n]: ")
if check_paragrafi != 'n':
    for file_corrente in lista_file:
        print( f"\n--- OPERO SU {file_corrente} ---" )
        zuppa = BeautifulSoup( open( working_dir + file_corrente ), "html.parser" )
        unisciParagrafi( zuppa )
        # salvo eventuali modifiche
        zuppa_originale = BeautifulSoup( open( working_dir + file_corrente ),
                                         "html.parser" )
        if zuppa != zuppa_originale:
            salvaModifiche( zuppa, file_corrente)

# controllo sillabate errate?
check_sillabate = input( "Eseguo controllo su sillabate errate? [S|n]: ")
if check_sillabate != 'n':
    # carico lista delle sillabate consentite
    try:
        with open( "./whitelist.txt" ) as f:
            whitelist = f.read().splitlines()
            original_lenght = len( whitelist )
    except:
        print( "FILE WHITELIST NON PRESENTE" )
        whitelist = []
        original_lenght = 0
        #creo il file
        f = open( "whitelist.txt", "w" )
        f.close()
        
    # creo lista (vuota per ora) delle sillabate da lasciare per l'epub corrente
    keeplist = [] 
    
    # eseguo il controllo
    for file_corrente in lista_file:
        print( f"--------              OPERO SU {file_corrente}            --------\n" )
        zuppa = BeautifulSoup( open( working_dir + file_corrente ), "html.parser" )
        correggiSillabate( zuppa )
        # salvo eventuali modifiche
        zuppa_originale = BeautifulSoup( open( working_dir + file_corrente ),
                                         "html.parser" )
        if zuppa != zuppa_originale:
            salvaModifiche( zuppa, file_corrente)
    salvaWhitelist()

ricreaEpub()


# TODO: se ho due p monchi consecutivi, l'unione dei due sarò ancora monco.


