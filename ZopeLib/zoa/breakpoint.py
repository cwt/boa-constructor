## Script (Python) "breakpoint"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
import sys

try:
    sys.breakpoint()
except AttributeError:
    print 'Please install the Breakpoint product in the ZopeLib directory and run Zope in the Debugger'
else:
    print 'breakpoint'

return printed

