## Script (Python) "DBAdapter"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=DBAdapter
##
return {'title': context.title,
        'connection_string': context.connection_string}
