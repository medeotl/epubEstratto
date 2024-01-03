#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup # browse del file HTML

import re

def listaSillabate( paragrafo ):
    # ritorna lista sillabate (anche vuota) presenti nel paragrafo
    return re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U )

def correggiSillabateCLI( paragrafo, lista_sillabate ):
    if lista_sillabate != []:
        print( "\n" + "PARAGRAFO" + paragrafo + "\n" )
        for i, sillabata in enumerate( lista_sillabate ):
            print( sillabata + "\n" )
            cambiare = input( "cambiare? [S|n]: " )
            if cambiare != 'n':
                cambiata = sillabata.replace( '-', '' )
                print( "cambiata: " + cambiata )
                paragrafo = paragrafo.replace( sillabata, cambiata )
                tag_paragrafo.string = paragrafo
                print( "\n--- CAMBIATA ---\n" )

# ---- MAIN ----

zuppa = BeautifulSoup( open("./epubs/JurassicPark/index_split_000.html"),
                      "html.parser" )

for tag_paragrafo in zuppa.find_all( "p" ):
    paragrafo = tag_paragrafo.text
    if paragrafo != "":
        l = listaSillabate( paragrafo )
        if l != []:
            # trovato paragrafo con una o più sillabate
            correggiSillabateCLI( paragrafo, l )

# salvo i risultati
with open( "epubModificato.html", "wt" ) as file:
    file.write( zuppa.prettify(zuppa.original_encoding) )

# Riferimenti:
# http://www.crummy.com/software/BeautifulSoup/bs4/doc/#modifying-the-tree
# http://stackoverflow.com/questions/3276040/how-can-i-use-the-python-htmlparser-library-to-extract-data-from-a-specific-div
