Boa Constructor (was Pygasm)
----------------------------

Thanks for checking out Boa Constructor.
Boa is supposed to be a simple Delphi for wxPython.
One of the philosophies I try to keep with is to purely be a time/effort saving
code generator, not a library/framework. This is the principle behind storing
object data as source code code as opposed to some pickled datastructure or
fileformat or something.

Look at Changes.txt for the latest improvements.

NB: Please unzip Boa to an empty directory

Licence:
GPL

Copyright:
Riaan Booysen 1999, 2000

-

CVS Release 0.0.3.5

-

Second release: Boa Constructor 0.0.3 - Yet Another Preview Version
Built with wxPython 2.1.13

This is definately still a pre alpha version. Anything may change and
a lot of things are missing or incomplete.


Changes of note:
* wxGTK compliant :)
* Window identifiers
* Buggy Debugger
* Explorer
* Framework for utility objects (wxImageList)
  Not useful yet, but it's a start
`* Funky dynamic toolbar
* Searchable help
* Find in module
  I've been avoiding all work on the source editor until there is a better 
  editor available, but I could not function without 'find'
* Dialogs
  Quick and dirty implementation, clicking on the dialog template
  inserts the standard idiom of usage at the current position in the
  source


Tings to tinker with:
If your sizing isn't right or files aren't being found, please
check out Preferences.py, Prefs*.py, Explorer.*.cfg
It might help.

To define your own explorer filesystem (drives/shares/volumes) or 
workspaces edit Explorer.*.cfg

Note to GTK users, by default transparency for wxGenBitmapButtons is 
off under GTK. If you think your wxGenBitmapButtons work fine you
should try turning transparency on in PrefsGTK.py.



Existing code:
If you actually did something useful with Pygasm and you want to open
previously generated modules, change the following in the code (before
you open it in Boa):
* replace #Pygasm:?:? with #Boa:?:?
  this is the module identifier and would be near the top of the module
* replace _init_create with _init_ctrls
* add method this method
def _init_utils(self): 
    pass
and call it in __init__ before _init_ctrls
e.g.
def __init__(self, parent): 
    self._init_utils()
    self._init_ctrls(parent)

-

First release: Preview Version
Built with wxPython 2.1.11

This is still a pre alpha release. Even tho I believe a project has to have some level of
maturity before it can be opened up, there are various reasons I decided to release now:
* Hopefully someone can get it wxGTK compatible
* Pygasm has progressed beyond proof of concept (I hope)
* It's christmas
* Big personal milestone (this should have been alpha, but oh well)
* I need feedback
* Find out who's interested

-

What you should be able to do:
	* Create new modules (Clicking a button from the 'New' page on the Palette)
	* Open/close/save python/pygasm modules and packages (Toolbar on the Editor or Explorer)
	* Check out the various views on the source code (Pages on the module's page)
	* Interact with views (Right click on a view for options)
	* Open the Designer (On a frame module, click the button with the cursor image)
	* Visually add/size/move controls
	* Inspect/edit object selection/properties/events/constructor with the Inspector
	* Generate/update source code (By closing the Designer or clicking Post in the inspector)
        * View Help (On the Palette, select a object on the palette before clicking on help)
        * Debug simple scripts

What isn't working:
	* Keyboard shortcuts for Editor & Inspector. (not implemented)
        * Inspector pages sometimes resize wrong, if a button is missing,
	  resize the inspector a bit to fix it
	* Sub-properties, a few bugs
        * Debugger
	* Many other things if you're interested see Bugs.txt
        * Text modules are semi-broken
	* Not prompted when overwriting a file
 

Planned:
	* Not nearly enough Property editors are implemented yet
	* Cut, Copy & Paste
	* Multiple selection
	* Collection editors, for controls hosting lists of objects.
	* Visual sizer creation/maintenance
	* Integration of a syntax highlighting editor! I cannot live without this
	  and many other editor features. I currently use IDLE.
	* Preferences for some configurability



Riaan Booysen
riaan@e.co.za