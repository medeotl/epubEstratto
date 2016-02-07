#!/usr/bin/python3
# -*- coding: utf-8 -*-
#fonte: https://docs.python.org/3.5/howto/argparse.html

import gi
gi.require_version( 'Gtk', '3.0')
from gi.repository import Gtk

# gestione degli argomenti passati via CLI

import argparse
parser = argparse.ArgumentParser( 
    description="Ricrea la finestra dal GUI_file specificato" )
parser.add_argument( "GUI_file", 
                     help="file di interfaccia gradica da aprire" )
args = parser.parse_args()
GUI_file = args.GUI_file
print( GUI_file )

# costruzione della finestra

builder = Gtk.Builder()
builder.add_from_file( GUI_file )

handlers = {
    "onDeleteWindow": Gtk.main_quit
}

builder.connect_signals( handlers )

try:
    window = builder.get_object( "window" )
    window.show_all()
    Gtk.main()
except:
    print( "ERRORE! la GtkWindow deve avere id 'window'" )
    


# add_argument può specificare type=int come parametro aggiuntivo
# parametri opzionali: ° nome breve (una lettera) preceduta da -
#                      ° nome lungo preceduto da --
#                      ° action="store_true" se uso tipo flag
#                      ° type=  per parametri normali ma opzionali
#                      ° choiches=[,,] per limitare valori possibili
#
#vedi link sopra per altre opzioni  
