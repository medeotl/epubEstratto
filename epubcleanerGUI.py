#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version( 'Gtk', '3.0')
from gi.repository import Gtk

from bs4 import BeautifulSoup # browse del file HTML
import re # ricerca parole in testo 
from time import sleep # per ritardare eventi 

class Handler:
    
    def onDeleteWindow( self, *args ):
        Gtk.main_quit( *args )
        
    def mantieni( self, button ):
        self.trova_prox_sillabata()
    
    def whitelist( self, button ):
        # aggiungo la sillabata alla whitelist
        self.trova_prox_sillabata()
        
    def correggi( self, button ):
        self.trova_prox_sillabata()
    
    def start( self, button ):
        # apro il file HTML di epub
        zuppa = BeautifulSoup(
            open( "./epubs/JurassicPark/index_split_003.html"), "lxml" )
        
        self.tag_paragrafi = zuppa.find_all("p")
        self.offset = 0
        self.tag_sillabata = builder.get_object( "bold red underlined" )
        self.trova_prox_sillabata()
        
    def trova_prox_sillabata( self ):
        while self.offset < len(self.tag_paragrafi):
            print( self.offset )
            paragrafo = self.tag_paragrafi[self.offset].string
            if paragrafo != None:  # paragrafo non vuoto, procedo
                l = re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U)
                if l != []:  # paragrafo contiene una o più sillabate
                    self.imposta_frase(paragrafo, l)
                    # aggiorno la label parola
                    lbl_sillabata = builder.get_object( "sillabata" )
                    lbl_sillabata.set_text( "Parola: " + l[0] )
                    self.offset += 1
                    break
            self.offset +=1
        if self.offset == len(self.tag_paragrafi):
            print( "Fine file raggiunto" )
                    
    def imposta_frase( self, paragrafo, l ):
        # isolo la frase contente la sillabata dal paragrafo e la 
        # pongo nella text box
        txtbuffer = builder.get_object( "txtbfrFrase" )
        
        frasi = paragrafo.split(".")
        for frase in frasi:
            if frase.find( l[0] ) != -1:
                txtbuffer.set_text( frase )
                # evidenzio in grassetto sottolineato rosso la sillabata
                start = frase.find( l[0] )
                end = start + len( l[0] )
                start = txtbuffer.get_iter_at_offset( start )
                end = txtbuffer.get_iter_at_offset( end )
                txtbuffer.apply_tag( self.tag_sillabata, start, end )
                break
    
builder = Gtk.Builder()
builder.add_from_file( "correzione.glade" )
builder.connect_signals( Handler() )

window = builder.get_object( "window" )
window.show_all()

Gtk.main()
