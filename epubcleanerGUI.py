#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version( 'Gtk', '3.0')
from gi.repository import Gio, Gtk

from bs4 import BeautifulSoup # browse del file HTML
import re # ricerca parole in testo 
from time import sleep # per ritardare eventi 

import os
import sys
import zipfile

class EpubCleaner( Gtk.Application ):

    def __init__( self ):
        Gtk.Application.__init__(
            self,
            application_id="com.wordpress.laconcoide.epubcleaner",
            flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.connect("startup", self.startup)
        self.connect("activate", self.activate)
        self.connect("shutdown", self.shutdown)
        
        self.working_dir = "./.epubunzipped/"
        
        try:
            with open("./whitelist.txt") as f:
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
        
        self.keeplist = [] # lista delle sillabate da mantenere
        

    def startup( self, app ):
        # primo ad essere eseguito dopo __init__
        # poi startup() o activate(), dipende da come lancio il progr.
        self.builder = Gtk.Builder()
        self.builder.add_from_file( "correzione.glade" )
        self.builder.connect_signals( self )
        self.window = self.builder.get_object( "window" )
        self.tag_sillabata = self.builder.get_object( 
            "bold red underlined" )
    
    def activate( self, app ):
        # app lanciata da SO (non da browser)
        app.add_window( self.window )
        self.window.show_all()

    def open( self, app ):
        # gestione apertura da file browser
        pass

    def on_epub_file_selected( self, a):
        print( type(a) )
        print( a.get_filename() )

    def on_start_clicked( self, button ):
        # creo elenco file html contenenti i capitoli dell'epub
        # TODO: il file va selezionato e unzippato in dir apposita
        
        libro = "/home/medeo/Documents/ebook/sfumature.epub"
        
        #estraggo il libro
        with zipfile.ZipFile( libro, 'r' ) as epub:
            epub.extractall( self.working_dir )
            
        lista_file = []
        
        for file in os.listdir( self.working_dir ):
            if file.endswith(".html"):
                lista_file.append( file)
        lista_file.sort()
        print( lista_file )
        self.lista_file = iter( lista_file )
        self.trova_sillabate()
        
    def on_mantieni_clicked( self, button ):
        self.keeplist.append( self.sillabata_corrente.lower() )
        print( "KEEPLIST: %s" % self.keeplist )
        # passo alla prossima sillabata
        self.aggiorna_GUI()
        
    def on_whitelist_clicked( self, button ):
        # aggiungo la sillabata alla whitelist
        self.whitelist.append( self.sillabata_corrente.lower() )
        print( "WHITELIST: %s " % self.whitelist )
        self.aggiorna_GUI()
        
    def on_correggi_clicked( self, button ):
        # correggo la sillabata
        cambiata = self.sillabata_corrente.replace( '-', '' )
        print("cambiata: %s ---> %s\n" % ( self.sillabata_corrente, 
                                           cambiata) )
        # aggiorno i paragrafi
        for idx_par in self.index_paragrafi:
            paragrafo = self.tag_paragrafi[idx_par].string 
            paragrafo_corretto = paragrafo.replace( 
                                                self.sillabata_corrente, 
                                                cambiata 
                                                )
            self.tag_paragrafi[idx_par].string = paragrafo_corretto                                       
        # proseguo 
        #~ print( "paragrafo_corretto: %s\n" % paragrafo_corretto )
        self.aggiorna_GUI()
        
    def trova_sillabate( self ):
        # trova tutte le sillabate del file index_split_00x.html
        # le pone in un dizionario del tipo { "sillabata", [14,21] }
        
        # apro il file index_split_00x.html
        try:
            self.file_corrente = next( self.lista_file )
        except StopIteration: # FINE FILE EPUB!
            print( " --- MODIFICHE TERMINATE ---" )
            app.window.destroy()
            return
           
        print( "--- OPERO SU %s ---" % self.file_corrente )
        self.window.set_title(self.file_corrente)
        
        self.zuppa = BeautifulSoup( 
            open( self.working_dir + self.file_corrente ), "lxml" )
            
        self.tag_paragrafi = self.zuppa.find_all("p")
        
        diz_sillabate = {}
        for index, tag_paragrafo in enumerate( self.tag_paragrafi ):
            paragrafo = tag_paragrafo.string
            if paragrafo != None:  # paragrafo non vuoto, procedo
                l = re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U)
                if l != []: # paragrafo contiene una o più sillabate
                    for sillabata in l:
                        # whitelist check
                        if sillabata.lower() in self.whitelist:
                            print("whitelist ignorata: %s\n" %sillabata)
                        # keeplist check
                        elif sillabata.lower() in self.keeplist:
                            print( "*************************" )
                            print( "*************************" )
                            print("keeplist ignorata: %s\n" %sillabata)
                            print( "*************************" )
                            print( "*************************" )
                        # sillabata da gestire
                        else:
                            if sillabata in diz_sillabate:
                                diz_sillabate[sillabata].append(
                                    index)
                            else:
                                diz_sillabate[sillabata] = [ index ]
                                
        # ordino il dizionario per index paragrafo
        lista_sillabate = sorted(diz_sillabate.items(), 
                                 key = lambda t: t[1]
                                 )
        #~ for sillabata, indexes in lista_sillabate:
            #~ print( sillabata, indexes )
        # creo iterator per il risultato ottenuto
        self.elenco_sillabate = iter( lista_sillabate )
        # aggiorno la GUI con la prima sillabata trovata
        self.aggiorna_GUI()

    def aggiorna_GUI( self ):
        # isolo la frase contente la PROSSIMA sillabata dal paragrafo e 
        # la pongo nella text box
        
        try:
            self.sillabata_corrente, self.index_paragrafi = \
                next(self.elenco_sillabate)
        except StopIteration: # ho gestito tutte le sillabate
            self.salva_file()
            return
            
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

    def salva_file( self ):
        # salvo le modifiche apportate in "nome_fileModificato.html"
        nuovo_file_name = self.file_corrente[:-5] + "Modificato.html"
        with open( nuovo_file_name, "wt") as file:
            file.write( str(self.zuppa) ) 
        print("--- SALVATO " + nuovo_file_name )
        self.trova_sillabate()
        
    def shutdown( self, app ):
        print( app )
        if self.whitelist != []:
            # salvo la whitelist su file
            try:
                with open("whitelist.txt", 'a') as f:
                    for parola in self.whitelist[self.original_lenght:]:
                        f.write("%s\n" % parola)
            except:
                print( "CHI HA CANCELLATO IL FILE?!?!!?" )
        app.quit()
        
if __name__ == '__main__':
    app = EpubCleaner()
    app.run(sys.argv)
