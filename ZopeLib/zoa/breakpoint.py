## Script (Python) "breakpoint"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try:
    import sys
except ImportError:
    raise Exception('Please install the Breakpoint product in the ZopeLib directory')

try:
    sys.breakpoint()
except AttributeError:
    raise Exception('Zope must be running in the Debugger')
