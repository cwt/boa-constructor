## Script (Python) "undo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start=0, end=1000
##title=undo
##
return str(context.aq_parent.undoable_transactions(start, end))
