## Script (Python) "properties"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=properties
##
obj = context.aq_parent
return [obj.propertyItems(), obj.propertyMap()]
