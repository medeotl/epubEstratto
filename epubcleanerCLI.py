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

    for file_corrente in lista_file:
        print( f"\n--- OPERO SU {file_corrente} ---" )
        zuppa = BeautifulSoup( open( working_dir + file_corrente ), "html.parser" )

        # controllo paragrafi monchi in file corrente
        for p_tag in zuppa.find_all( "p" ):
            paragrafo = p_tag.text.rstrip()
            # check paragrafo monco
            if paragrafo == "" :
                continue
            if re.match( r"[^.…!?:»”]", paragrafo[-1], re.U ):
                next_p_tag = p_tag.findNextSibling()
                if (next_p_tag == None) or (next_p_tag.text.rstrip() == ""):
                    continue
                print( "\n@@@ trovata paragrafo errato: \n{}".format( repr(paragrafo) ))
                print( repr( next_p_tag.text.rstrip() ))
                unificare = input( "unifico i paragrafri? [S|n]: ")
                if unificare != 'n':
                    # unisco i due paragrafi
                    print( "---DEBUG: Unifico i paragrafi ---" )
                    while next_p_tag.contents != []:
                        p_tag.append( next_p_tag.contents[0] )
                    # elimino secondo paragrafo e pulisco
                    next_p_tag.decompose()
                    p_tag.smooth()

        # salvo eventuali modifiche
        zuppa_originale = BeautifulSoup( open( working_dir + file_corrente ),
                                         "html.parser" )
        if zuppa != zuppa_originale:
            salvaModifiche( zuppa, working_dir+file_corrente)

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
                print( "Correggo la sillabata corrente? [Sì|no|whitelist] ")
                fix_sillabata = input( "Scelta: [S|n|w]: ")
                match fix_sillabata:
                    case "n": # keeplist!
                        keeplist.append( sillabata.lower() )
                        print (f"{sillabata} aggiunta alla lista delle sillabate da mantenere nell'ebook")
                    case "w": # whitelist!
                        whitelist.append( sillabata.lower() )
                        print (f"{sillabata} aggiunta alla whitelist")
                    case _:
                        # correggo la sillabata
                        print( "---DEBUG: prima o poi la correggo ---" )
                

def salvaModifiche( zuppa, file_html ):
    # salva le modifiche apportate nel file html
    with open( file_html, "wt" ) as f:
        f.write( str( zuppa ) )
        print( f"--- SALVATO {file_html} \n" )

def ricreaEpub():
    # ricreo il file ePub
    print( "--- MODIFICHE TERMINATE --- \n" )
    # ricreo il file epub
    shutil.make_archive("ebook_MODIFICATO", "zip", ".epubunzipped")
    os.rename("ebook_MODIFICATO.zip", "ebook_MODIFICATO.epub")
    print("File ripulito salvato in: ebook_MODIFICATO.epub")

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
# ~ check_paragrafi = input( "Eseguo controllo su paragrafi monchi? [S|n]: ")
# ~ if check_paragrafi != 'n':
    # ~ unisciParagrafi()

# controllo sillabate errate?
check_sillabate = input( "Eseguo controllo su sillabate errate? [S|n]: ")
if check_sillabate != 'n':
    # carico lista delle sillabate consentite
    try:
        with open( "../whitelist.txt" ) as f: #FIXME poi riportarlo a ./
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

ricreaEpub()

# TODO: se ho due p monchi consecutivi, l'unione dei due sarò ancora monco.
