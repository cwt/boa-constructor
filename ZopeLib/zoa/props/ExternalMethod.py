## Script (Python) "ExternalMethod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name
##title=ExternalMethod
##
obj = context.aq_parent.aq_parent
meth = obj.zoa.subobj_(name)
return {'title':    meth.title,
        'function': meth.function(),
        'module':   meth.module()}
