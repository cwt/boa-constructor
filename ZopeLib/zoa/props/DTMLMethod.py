## Script (Python) "DTMLMethod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name
##title=DTMLMethod
##
obj = context.aq_parent.aq_parent
meth = obj.zoa.subobj_(name)
return {'title': meth.title,
        'proxy': obj.zoa.proxyroles(name),
        'owner': obj.zoa.ownerinfo(name)}
