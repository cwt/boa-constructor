## Script (Python) "filteredmetatypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=filteredmetatypes
##
return context.aq_parent.filtered_meta_types()
