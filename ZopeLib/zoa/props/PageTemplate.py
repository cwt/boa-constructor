## Script (Python) "PageTemplate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name
##title=PageTemplates
##
ctx = context.aq_parent.aq_parent
pt = ctx.zoa.subobj_(name)
return {'title': pt.title,
        'content_type': pt.content_type,
        'expand': pt.expand}
