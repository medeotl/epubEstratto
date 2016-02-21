#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version( 'Gtk', '3.0')
from gi.repository import Gtk

from bs4 import BeautifulSoup # browse del file HTML

import re
import time

def listaSillabate( paragrafo ):
    #indica se nel paragrafo è presente una o più sillabate
    return re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U)

def correggiSillabateCLI( paragrafo ):
    lista_sillabate = re.findall( r"\w+(?:-[\w]+)+",
                                  paragrafo,
                                  re.U)
    if lista_sillabate != []:
        print( '\n' + 'PARAGRAFO' + paragrafo + '\n' )
        for i, sillabata in enumerate( lista_sillabate ):
            print( sillabata + "\n" )
            cambiare = input( "cambiare? [S|n]: " )
            if cambiare != 'n':
                cambiata = sillabata.replace( '-', '' )
                print("cambiata: " + cambiata)
                paragrafo = paragrafo.replace( sillabata, cambiata )
                print( "\n--- CAMBIATA ---\n")

def correggiSillabateGUI( paragrafo, lista ):
    builder = Gtk.Builder()
    builder.add_from_file( "correzione.glade" )

    handlers = {
        "onDeleteWindow": Gtk.main_quit
    }

    builder.connect_signals( handlers )

    txtbuffer = builder.get_object( "txtbfrParagrafo" )
    txtbuffer.set_text( paragrafo )
    # evidenzio in grassetto la sillabata
    start = paragrafo.find( lista[0] )
    end = start + len( lista[0] )
    start = txtbuffer.get_iter_at_offset( start )
    end = txtbuffer.get_iter_at_offset( end )
    tag_bold = builder.get_object( "bold" )
    txtbuffer.apply_tag( tag_bold, start, end )

    lbl_sillabata = builder.get_object( "sillabata" )
    lbl_sillabata.set_text( "Parola: " + lista[0] )

    window = builder.get_object( "window" )
    window.show_all()
    Gtk.main()

# ---- MAIN ----

zuppa = BeautifulSoup( open("./epubs/JurassicPark/index_split_000.html"),
                       "lxml" )

for tag_paragrafo in zuppa.find_all("p"):
    paragrafo = tag_paragrafo.string
    if paragrafo != None:
        l = listaSillabate(paragrafo)
        if l != []:
            # trovato paragrafo con una o più sillabate
            correggiSillabateCLI( paragrafo )

# salvo i risultati
with open("JurassicPark000Modificato.html", "wb") as file:
    file.write( zuppa.prettify(zuppa.original_encoding) )

# Riferimenti:
# http://www.crummy.com/software/BeautifulSoup/bs4/doc/#modifying-the-tree
# http://stackoverflow.com/questions/3276040/how-can-i-use-the-python-htmlparser-library-to-extract-data-from-a-specific-div      
