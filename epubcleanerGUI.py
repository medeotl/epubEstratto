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
                print( "FILE PRESENTE" )
                self.whitelist = f.read().splitlines()
                self.original_lenght = len(self.whitelist)
        except:
            print( "FILE NON PRESENTE" )
            self.whitelist = []
            self.original_lenght = 0
            #creo il file
            f = open( "whitelist.txt", "w")
            f.close()
            
        print( "whitelist: %s" % self.whitelist )

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
        # passo alla prossima sillabata
        self.aggiorna_GUI()
        
    def on_whitelist_clicked( self, button ):
        # aggiungo la sillabata alla whitelist
        print( "WHITELIST: aggiunta %s " % self.sillabata_corrente )
        self.whitelist.append( self.sillabata_corrente )
        self.aggiorna_GUI( *next(self.elenco_sillabate) )
        
    def on_correggi_clicked( self, button ):
        # correggo la sillabata
        cambiata = self.sillabata_corrente.replace( '-', '' )
        print("cambiata: %s ---> %s\n" % ( self.sillabata_corrente, 
                                           cambiata) )
        # aggiorno il paragrafo
        paragrafo = self.tag_paragrafi[self.idx_par_corrente].string 
        paragrafo_corretto = paragrafo.replace( self.sillabata_corrente, 
                                                cambiata )
        self.tag_paragrafi[self.idx_par_corrente].string = \
            paragrafo_corretto                                       
        # proseguo 
        print( "paragrafo_corretto: %s\n" % paragrafo_corretto )
        self.aggiorna_GUI( *next(self.elenco_sillabate) )
        
    def on_start_clicked( self, button ):
        # apro il file HTML di epub
        self.zuppa = BeautifulSoup(
            open( "./epubs/JurassicPark/index_split_003.html"), 
            "lxml" )
        
        self.tag_paragrafi = self.zuppa.find_all("p")
        self.offset = 0
        self.tag_sillabata = self.builder.get_object( 
            "bold red underlined" )
        self.trova_sillabate()
        
    def trova_prox_sillabata( self ):
        while self.offset < len(self.tag_paragrafi):
            print( self.offset )
            paragrafo = self.tag_paragrafi[self.offset].string
            if paragrafo != None:  # paragrafo non vuoto, procedo
                l = re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U)
                if l != []: # paragrafo contiene una o più sillabate
                    if l[0] in self.whitelist:
                        print( "saltato %s\n" %l[0] )
                    else:
                        self.sillabata = l[0]
                        self.aggiorna_GUI( paragrafo )
                        self.offset += 1
                        break
            self.offset +=1
        if self.offset == len(self.tag_paragrafi):
            print( "Fine file raggiunto" )
            # salvo le modifiche
            with open("JurassicParkModificato.html", "wt") as file:
                file.write( self.zuppa.prettify(
                                self.zuppa.original_encoding) )

    def trova_sillabate( self ):
        # trova tutte le sillabate del file 00x.html
        # le pone in un dizionario del tipo { "sillabata", [14,21] }
        diz_sillabate = {}
        for index, tag_paragrafo in enumerate( self.tag_paragrafi ):
            paragrafo = tag_paragrafo.string
            if paragrafo != None:  # paragrafo non vuoto, procedo
                l = re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U)
                if l != []: # paragrafo contiene una o più sillabate
                    # whitelist check
                    for sillabata in l:
                        if sillabata in self.whitelist:
                            print( "saltato %s\n" %sillabata )
                            l.remove(sillabata)
                    # memorizzo "ritrovamento"
                    if l != []:
                    	for sillabata in l:
                            if sillabata in diz_sillabate:
                                diz_sillabate[sillabata].append(
                                    index)
                            else:
                                diz_sillabate[sillabata] = [ index ]
                                
        # ordino il dizionario per index paragrafo
        lista_sillabate = sorted(diz_sillabate.items(), 
                                 key = lambda t: t[1]
                                 )
        for sillabata, indexes in lista_sillabate:
            print( sillabata, indexes )
        # creo iterator per il risultato ottenuto
        self.elenco_sillabate = iter( lista_sillabate )
        # aggiorno la GUI con la prima sillabata trovata
        self.aggiorna_GUI()


    def aggiorna_GUI( self ):
        # isolo la frase contente la PROSSIMA sillabata dal paragrafo e 
        # la pongo nella text box
        
        print( "\n--- funzione aggiorna_GUI ---\n" )
        self.sillabata_corrente, self.index_paragrafi = \
            next(self.elenco_sillabate)
        sillabata = self.sillabata_corrente
        index_paragrafo = self.index_paragrafi[0]
        
        txtbuffer = self.builder.get_object( "txtbfrFrase" )
        
        paragrafo = self.tag_paragrafi[ index_paragrafo ].string
        
        # ricerco la frase del paragrafo contenente la sillabata
        # e la evidenzio con tag apposito
        frasi = paragrafo.split(".")
        for frase in frasi:
            if frase.find( sillabata ) != -1: # frase contiene sillabata
                txtbuffer.set_text( frase )
                # evidenzio in grassetto sottolineato rosso la sillabata
                start = frase.find( sillabata )
                end = start + len( sillabata )
                start = txtbuffer.get_iter_at_offset( start )
                end = txtbuffer.get_iter_at_offset( end )
                txtbuffer.apply_tag( self.tag_sillabata, start, end )
                break
        # aggiorno la label parola
        lbl_sillabata = self.builder.get_object( "sillabata" )
        lbl_sillabata.set_text( "Parola: " + sillabata )

    def shutdown( self, app ):
        if self.whitelist != []:
            # salvo la whitelist su file
            try:
                with open("whitelist.txt", 'a') as f:
                    for parola in self.whitelist[self.original_lenght:]:
                        f.write("%s\n" % parola)
            except:
                print( "CHI HA CANCELLATO IL FILE?!?!!?" )
        
if __name__ == '__main__':
    app = EpubCleaner()
    app.run(sys.argv)
