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

# apro il file HTML di epub
zuppa = BeautifulSoup(open("./epubs/JurassicPark/index_split_000.html"),
                      "lxml" )

for tag_paragrafo in zuppa.find_all("p"):
    paragrafo = tag_paragrafo.string
    if paragrafo != None:
        l = listaSillabate(paragrafo)
        if l != []:
            # trovato paragrafo con una o più sillabate
            correggiSillabateGUI( paragrafo, l )

builder = Gtk.Builder()
builder.add_from_file( "correzione.glade" )
builder.connect_signals( Handler() )

window = builder.get_object( "window" )
window.show_all()

Gtk.main()

print( "commit di prova" )
