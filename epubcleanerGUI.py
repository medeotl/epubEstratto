#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version( 'Gtk', '3.0')
from gi.repository import Gio, Gtk

from bs4 import BeautifulSoup # browse del file HTML
import re # ricerca parole in testo 
from time import sleep # per ritardare eventi 

import sys

class EpubCleaner( Gtk.Application ):

    def __init__( self ):
        Gtk.Application.__init__(
            self,
            application_id="com.wordpress.laconcoide.epubcleaner",
            flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.connect("startup", self.startup)
        self.connect("activate", self.activate)
        self.connect("shutdown", self.shutdown)
        
        try:
            with open("./whitelist.txt") as f:
                self.whitelist = f.read().splitlines()
                self.original_lenght = len(self.whitelist)
        except:
            self.whitelist = []
            self.original_lenght = 0
        print( self.whitelist )

    def startup( self, app):
        # primo ad essere eseguito dopo __init__
        self.builder = Gtk.Builder()
        self.builder.add_from_file( "correzione.glade" )
        self.builder.connect_signals( self )
        self.window = self.builder.get_object( "window" )
    
    def activate( self, app ):
        # app lanciata da SO (non da browser)
        app.add_window( self.window )
        self.window.show_all()

    def open( self, app ):
        # gestione apertura da file browser
        pass
        
    def on_mantieni_clicked( self, button ):
        self.trova_prox_sillabata()
        
    def on_whitelist_clicked( self, button ):
        # aggiungo la sillabata alla whitelist
        print( self.sillabata )
        self.whitelist.append( self.sillabata )
        self.trova_prox_sillabata()
        
    def on_correggi_clicked( self, button ):
        self.trova_prox_sillabata()
        
    def on_start_clicked( self, button ):
        # apro il file HTML di epub
        pass
        zuppa = BeautifulSoup(
            open( "./epubs/JurassicPark/index_split_002.html"), "lxml" )
        
        self.tag_paragrafi = zuppa.find_all("p")
        self.offset = 0
        self.tag_sillabata = self.builder.get_object( 
            "bold red underlined" )
        self.trova_prox_sillabata()
        
    def trova_prox_sillabata( self ):
        while self.offset < len(self.tag_paragrafi):
            #~ print( self.offset )
            paragrafo = self.tag_paragrafi[self.offset].string
            if paragrafo != None:  # paragrafo non vuoto, procedo
                l = re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U)
                if l != []:  # paragrafo contiene una o più sillabate
                    self.sillabata = l[0]
                    self.imposta_frase(paragrafo)
                    # aggiorno la label parola
                    lbl_sillabata = self.builder.get_object( 
                        "sillabata" )
                    lbl_sillabata.set_text( "Parola: " + l[0] )
                    self.offset += 1
                    break
            self.offset +=1
        if self.offset == len(self.tag_paragrafi):
            print( "Fine file raggiunto" )
                    
    def imposta_frase( self, paragrafo):
        # isolo la frase contente la sillabata dal paragrafo e la 
        # pongo nella text box
        txtbuffer = self.builder.get_object( "txtbfrFrase" )
        
        frasi = paragrafo.split(".")
        for frase in frasi:
            if frase.find( self.sillabata ) != -1:
                txtbuffer.set_text( frase )
                # evidenzio in grassetto sottolineato rosso la sillabata
                start = frase.find( self.sillabata )
                end = start + len( self.sillabata )
                start = txtbuffer.get_iter_at_offset( start )
                end = txtbuffer.get_iter_at_offset( end )
                txtbuffer.apply_tag( self.tag_sillabata, start, end )
                break

    def shutdown( self, app ):
        if self.whitelist != []:
            # salvo la whitelist su file
            try:
                with open("whitelist.txt", 'w') as f:
                    f.seek( self.original_lenght )
                    for parola in self.whitelist:
                        f.write("%s\n" % parola)
            except:
                print( "CHI HA CANCELLATO IL FILE?!?!!?" )
        
if __name__ == '__main__':
    app = EpubCleaner()
    app.run(sys.argv)
