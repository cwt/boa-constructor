print 'Importing all wxPython libraries',

from wxPython.wx import *
print '.',

try: from wxPython.grid import *
except ImportError: pass
else: print '.',

try: from wxPython.html import *
except ImportError: pass
else: print '.',

try: from wxPython.ogl import *
except ImportError: pass
else: print '.',

try: from wxPython.stc import *
except ImportError: pass
else: print '.',

try: from wxPython.calendar import *
except ImportError: pass
else: print '.',

try: from wxPython.glcanvas import *
except ImportError: pass
else: print '.',

# Rebind original namespace to catch any name added to wx by other libraries
from wxPython.wx import *
print '.',

print
