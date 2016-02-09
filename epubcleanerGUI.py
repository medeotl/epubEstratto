import gi
gi.require_version( 'Gtk', '3.0')
from gi.repository import Gtk

class Handler:
    
    l = [] # lista delle sillabate
    
    def onDeleteWindow( self, *args ):
        Gtk.main_quit( *args )

    def whitelist( self, button ):
        # aggiungo la sillabata alla whitelist
        self.l.append( "Nico" )
        
    def mantieni( self, button ):
        print( self.l )

builder = Gtk.Builder()
builder.add_from_file( "correzione.glade" )
builder.connect_signals( Handler() )

window = builder.get_object( "window" )
window.show_all()

Gtk.main()
