## Script (Python) "subobj_"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objname
##title=subobj_
##
obj = context.aq_parent
for subobj in obj.objectValues():
    try:
        name = subobj.id()
    except TypeError:
        name = subobj.id
    if name == objname:
        return subobj
raise 'Method not found in %s'%obj.id
