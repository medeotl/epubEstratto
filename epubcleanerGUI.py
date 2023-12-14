#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version( 'Gtk', '3.0')
from gi.repository import Gio, Gtk, Gdk

from bs4 import BeautifulSoup # browse del file HTML
import re # ricerca parole in testo

import os
import sys
import zipfile

class EpubCleaner( Gtk.Application ):

    def __init__( self ):
        Gtk.Application.__init__(
            self,
            application_id="com.wordpress.laconcoide.epubcleaner",
            flags=Gio.ApplicationFlags.FLAGS_NONE )

        self.connect( "startup", self.startup )
        self.connect( "activate", self.activate )
        self.connect( "shutdown", self.shutdown )

        self.set_accels_for_action( "win.show-help-overlay", ["<primary>question"] )

        self.working_dir = "./.epubunzipped/"

        try:
            with open( "./whitelist.txt" ) as f:
                self.whitelist = f.read().splitlines()
                self.original_lenght = len( self.whitelist )
        except:
            print( "FILE WHITELIST NON PRESENTE" )
            self.whitelist = []
            self.original_lenght = 0
            #creo il file
            f = open( "whitelist.txt", "w" )
            f.close()

        print( "whitelist: %s" % self.whitelist )

        self.keeplist = [] # lista delle sillabate da mantenere

    def startup( self, app ):
        # primo ad essere eseguito dopo __init__
        # poi activate() o open(), dipende da come lancio il programma
        self.builder = Gtk.Builder()
        self.builder.add_from_file( "correzione.ui" )
        self.builder.connect_signals( self )
        self.window = self.builder.get_object( "window" )
        self.builder.add_from_file( "shortcuts.ui" )
        shortcuts = self.builder.get_object( "shortcuts" )
        self.window.set_help_overlay( shortcuts )
        self.tag_sillabata = self.builder.get_object( "bold red underlined" )

    def activate( self, app ):
        # app lanciata da SO (non da file manager)
        app.add_window( self.window )
        
        # aggiungo accelleratore per Ctrl+Q --> Quit
        accel_group = Gtk.AccelGroup()
        accel_group.connect(
            Gdk.keyval_from_name( 'Q' ),
            Gdk.ModifierType.CONTROL_MASK,
            0,
            lambda acc_group,app_win,q,ctrl: app.quit()
        )
        self.window.add_accel_group( accel_group )
        
        self.window.show_all()

    def open( self, app ):
        # gestione apertura da file manager
        pass

    def on_epub_file_selected( self, file ):
        # ho selezionato il file tramite GtkFileChooserButton

        # riabilito i pulsanti
        btnMantieni = self.builder.get_object( "btnMantieni" )
        btnWhitelist = self.builder.get_object( "btnWhitelist" )
        btnCorreggi = self.builder.get_object( "btnCorreggi" )
        btnMantieni.set_sensitive( True )
        btnWhitelist.set_sensitive( True )
        btnCorreggi.set_sensitive( True )

        libro = file.get_filename()
        print( "Libro: %s \n" % libro )

        # rimuovo vecchia directory working_dir
        import shutil
        shutil.rmtree( self.working_dir, ignore_errors=True )

        # scompatto il libro (la directory è creata automaticamente)
        with zipfile.ZipFile( libro, 'r' ) as epub:
            epub.extractall( self.working_dir )

        possible_files_dir = ["OEBPS/Text",
                              "OEBPS/text",
                              "OEBPS",
                              "text"]
        # ricerco directory contenente i file html da controllare
        for directory in possible_files_dir:
            if os.path.exists( self.working_dir + directory):
                self.working_dir = f"{self.working_dir}{directory}/"
                break

        print( "files_dir: %s \n" % self.working_dir )
        # creo lista file html da controllare
        lista_file = []
        for file in os.listdir( self.working_dir ):
            if file.endswith( "html" ) or file.endswith( "htm" ):
                lista_file.append( file )

        lista_file.sort()
        print( "lista file: %s \n" % lista_file )
        self.lista_file = iter( lista_file )
        self.trova_sillabate()

    def on_mantieni_clicked( self, button ):
        self.keeplist.append( self.sillabata_corrente.lower() )
        print( "KEEPLIST: %s \n" % self.keeplist )
        # passo alla prossima sillabata
        self.aggiorna_GUI()

    def on_whitelist_clicked( self, button ):
        # aggiungo la sillabata alla whitelist
        self.whitelist.append( self.sillabata_corrente.lower() )
        print( "WHITELIST: %s \n" % self.whitelist )
        self.aggiorna_GUI()

    def on_correggi_clicked( self, button ):
        # correggo la sillabata
        cambiata = self.sillabata_corrente.replace( '-', '' )
        print( "cambiata: %s ---> %s \n" % (self.sillabata_corrente, cambiata) )

        # aggiorno i paragrafi
        for idx_par in self.index_paragrafi:
            paragrafo = self.tag_paragrafi[idx_par]
            for item in paragrafo.contents:
                if self.sillabata_corrente in item:
                    paragrafo_corretto = item.replace(self.sillabata_corrente,
                                                      cambiata)
                    print ("_---_ paragrafo corretto: \n%s\n" % (paragrafo_corretto) )
                    break
            self.tag_paragrafi[idx_par].string = paragrafo_corretto
        # proseguo
        self.aggiorna_GUI()

    def trova_sillabate( self ):
        # trova tutte le sillabate presenti nei file html
        # le pone in un dizionario del tipo { "sillabata", [14,21] }
        # dove 14 e 21 sono i paragrafi in cui è presente la parola sillabata

        # apro il file html
        try:
            self.file_corrente = next( self.lista_file )
        except StopIteration: # FINE FILE EPUB!
            print( " --- MODIFICHE TERMINATE --- \n" )
            # ricreo il file epub
            import shutil
            shutil.make_archive("ebook MODIFICATO", "zip", ".epubunzipped")
            os.rename("ebook MODIFICATO.zip", "ebook MODIFICATO.epub")

            app.window.destroy()
            return

        print( "--- OPERO SU %s --- \n" % self.file_corrente )
        headerbar = self.builder.get_object( "headerbar" )
        headerbar.set_subtitle( self.file_corrente )

        self.zuppa = BeautifulSoup(
            open( self.working_dir + self.file_corrente ), "html.parser" )

        self.tag_paragrafi = self.zuppa.find_all( "p" )

        diz_sillabate = {}
        for index, tag_paragrafo in enumerate( self.tag_paragrafi ):
            print( "DEBUG ---\n" + tag_paragrafo.text + "\n---------\n")
            # --------- DEBUG -----------
            paragrafo = tag_paragrafo.text
            if paragrafo != "":  # paragrafo non vuoto, procedo
                l = re.findall( r"\w+(?:-[\w]+)+", paragrafo, re.U )
                if l != []: # paragrafo contiene una o più sillabate
                    for sillabata in l:
                        # whitelist check
                        if sillabata.lower() in self.whitelist:
                            print( "whitelist ignorata: %s \n" %sillabata )
                        # keeplist check
                        elif sillabata.lower() in self.keeplist:
                            print( "*************************" )
                            print( "*************************" )
                            print( "keeplist ignorata: %s" %sillabata )
                            print( "*************************" )
                            print( "************************* \n" )
                        # sillabata da gestire
                        else:
                            if sillabata in diz_sillabate:
                                diz_sillabate[sillabata].append( index )
                            else:
                                diz_sillabate[sillabata] = [ index ]

        if len( diz_sillabate ) == 0:
            # il file corrente non contiene sillabate
            # passo al prossimo
            self.trova_sillabate ()
            return

        # ordino il dizionario per index paragrafo
        lista_sillabate = sorted( diz_sillabate.items(),
                                  key = lambda t: t[1]
                                  )
        # ~ for sillabata, indexes in lista_sillabate:
            # ~ print( sillabata, indexes, "\n")

        # creo iterator per il risultato ottenuto
        self.elenco_sillabate = iter( lista_sillabate )
        # aggiorno la GUI con la prima sillabata trovata
        self.aggiorna_GUI()

    def aggiorna_GUI( self ):
        # isolo la frase contente la PROSSIMA sillabata dal paragrafo e
        # la pongo nella text box

        try:
            self.sillabata_corrente, self.index_paragrafi = \
                next( self.elenco_sillabate )
        except StopIteration: # ho gestito tutte le sillabate
            self.salva_file()
            return

        sillabata = self.sillabata_corrente
        print ("DEBUG --- sillabata corrente: %s \n" % self.sillabata_corrente)
        index_paragrafo = self.index_paragrafi[0]

        txtbuffer = self.builder.get_object( "txtbfrFrase" )

        paragrafo = self.tag_paragrafi[ index_paragrafo ].text

        # ricerco la frase del paragrafo contenente la sillabata
        # e la evidenzio con tag apposito
        frasi = paragrafo.split( "." )
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
        # salvo le modifiche apportate
        with open( self.working_dir + self.file_corrente, "wt" ) as file:
            file.write( str(self.zuppa) )
        print( "--- SALVATO " + self.file_corrente + "\n")
        self.trova_sillabate()

    def mostra_preferenze( self, modalBtnPreferenze ):
        print( "@@@ preferenze" )
        print( """
        @@@ Abbiamo parlato delle nostre preferenze e dei nostri gusti e
        abbiamo scoperto che ci piacciono gli stessi batteri.  W. Allen""" )

    def mostra_about( self, modalBtnAbout ):
        self.builder.add_from_file( "about.ui" )
        about_dialog = self.builder.get_object( "dlgAbout" )
        about_dialog.set_transient_for( self.window )
        about_dialog.connect( "close", lambda: about_dialog.destroy() )
        about_dialog.show_all()

    def shutdown( self, app ):
        """ chiusura programma """
        # aggiungo le nuove parole whitelist nel file apposito
        if self.whitelist != []:
            try:
                with open( "whitelist.txt", 'a' ) as f:
                    for parola in self.whitelist[self.original_lenght:]:
                        f.write( "%s\n" % parola )
            except:
                print( "CHI HA CANCELLATO IL FILE?!?!!? \n" )
        app.quit()

if __name__ == '__main__':
    app = EpubCleaner()
    app.run( sys.argv )
