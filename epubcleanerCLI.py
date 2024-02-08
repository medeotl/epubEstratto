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

def unisciParagrafi():
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

    for file_corrente in lista_file:
        print( f"\n--- OPERO SU {file_corrente} ---" )
        zuppa = BeautifulSoup( open( working_dir + file_corrente ), "html.parser" )

        # controllo paragrafi monchi in file corrente
        lista_p = zuppa.find_all( "p" )
        for p_tag, p_tag_next in zip( lista_p[:-1], lista_p[1:] ):
            paragrafo = p_tag.text.rstrip()
            if paragrafo == "" :
                continue
            # check paragrafo monco
            if re.match( r"[^.…!?:»”]", paragrafo[-1], re.U ):
                # check paragrafo monco sillabato
                if paragrafo.endswith( "-" ):
                    # cancello l'a capo
                    p_tag_next.decompose()
                    # imposto p_tag_next al valore corretto
                    p_tag_next = p_tag.findNextSibling()

                if p_tag_next.text.rstrip() == "" :
                    continue

                # richiedo valutazione dell'utente        
                print( "\n@@@ trovata paragrafo errato: \n{}".format( repr(paragrafo) ))
                print( repr( p_tag_next.text.rstrip() ))
                unificare = input( "unifico i paragrafri? [S|n]: ")
                if unificare != 'n':
                    # unisco i due paragrafi
                    print( "---DEBUG: Unifico i paragrafi ---" )
                    while p_tag_next.contents != []:
                        p_tag.append( p_tag_next.contents[0] )
                    # elimino secondo paragrafo e pulisco
                    p_tag_next.decompose()
                    p_tag.smooth()

        # salvo eventuali modifiche
        zuppa_originale = BeautifulSoup( open( working_dir + file_corrente ),
                                         "html.parser" )
        if zuppa != zuppa_originale:
            salvaModifiche( zuppa, file_corrente)

def correggiSillabate():
    # check sillabata sbagliata

    for file_corrente in lista_file:
        print( f"--------              OPERO SU {file_corrente}            --------\n" )
        zuppa = BeautifulSoup( open( working_dir + file_corrente ), "html.parser" )

        # controllo paragrafi contenenti le sillabate
        for p_tag in zuppa.find_all( "p" ):
            paragrafo = p_tag.text
            for sillabata in re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U ):
                # whitelist?
                if sillabata.lower() in whitelist:
                    print( f"sillabata nella WHITELIST: {sillabata} \n" )
                    continue
                # keeplist?
                if sillabata.lower() in keeplist:
                    print( f"sillabata nella KEEPLIST: {sillabata} \n")
                    continue
                # sillabata da gestire
                for frase in paragrafo.split( "." ):
                    if sillabata in frase:
                        print( "FRASE: " + frase.lstrip() + "." )
                        break
                print( f"Correggo la sillabata corrente ({sillabata})? [Sì|no|whitelist] ")
                fix_sillabata = input( "Scelta: [S|n|w]: ")
                match fix_sillabata:
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
        # fine controllo paragrafi, salvo il file
        # TODO non bisogna salvare un file html che non ha subito modifiche (Cinema Speculation)
        salvaModifiche( zuppa, file_corrente )
    # fine elaborazione

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
    # ricreo il file ePub
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
    unisciParagrafi()

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
    
    # correggo le sillabate
    correggiSillabate()
    salvaWhitelist()

ricreaEpub()


# TODO: se ho due p monchi consecutivi, l'unione dei due sarò ancora monco.
