- Boa Constructor -

Thanks for checking out Boa Constructor.

Boa is supposed to be a simple Delphi for wxPython.
It is an IDE for Python development including visual wxPython frame
design, object browsers, documentation genaration, debugging,
source control (CVS) and more.
The Boa IDE also integrates with other Python technologies like Zope.
Eventually I would also like to aid Extension development and
deployment support with distutils.

If you are new to Boa and wxPython, work through the new Getting Started Guide
and Tutorial.

Look at Changes.txt for the latest improvements.
Look at Bugs.txt for important info about problems & bugs.

NB: Please unzip Boa to an empty directory

Licence:
GPL

Version:
0.0.5
Use with wxPython 2.2.5

Copyright:
Riaan Booysen 1999, 2000, 2001
riaan@e.co.za

Release history:

2000-08-30 - Boa Constructor 0.0.4

2000-02-29 - Boa Constructor 0.0.3

1999-12-25 - Pygasm 0.0.1 & 0.0.2


IMPORTANT

The following scenarios lead to Core Dumps:
* Closing Boa after debugging (sorry, but at least you don't lose your work)
* On wxGTK/Linux
    Creating Columns of wxListCtrl when it does not have the wxLC_REPORT style
    Note that the control must already have this style, as it is a constructor
    argument, the control should be Recreated or the Designer should be closed
    and reopened before defining your columns in the collection editor.
