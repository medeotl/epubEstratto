#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version( 'Gtk', '3.0')
from gi.repository import Gtk

from bs4 import BeautifulSoup # browse del file HTML
import re # ricerca parole in testo 
from time import sleep # per ritardare eventi 

import sys

from gi.repository import Gio, Gtk


class EpubCleaner( Gtk.Application ):

    def __init__( self ):
        Gtk.Application.__init__(
            self,
            application_id="com.wordpress.laconcoide.epubcleaner",
            flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.builder = Gtk.Builder()
        self.builder.add_from_file( "correzione.glade" )
        self.builder.connect_signals( self )
        self.window = self.builder.get_object( "window" )
        
        self.connect("activate", self.activate)

    def activate( self, app ):
        self.window.show_all()
        Gtk.main()

    def onDeleteWindow( self, *args ):
        Gtk.main_quit( *args )

    def open( self, app ):
        # gestione apertura da file browser
        pass
        
    def startup( self, app):
        pass
    
    def mantieni( self, button ):
        pass
        
    def whitelist( self, button ):
        pass
        
    def correggi( self, button ):
        pass
        
    def start( self, button ):
        pass

if __name__ == '__main__':
    app = EpubCleaner()
    app.run(sys.argv)
