## Script (Python) "Form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Form
##
ctx = context.aq_parent.aq_parent.aq_parent
enctype = ctx.enctype or ''
return {'title': ctx.title,
        'row_length': ctx.row_length,
        'action': ctx.action,
        'method': ctx.method,
        'enctype': enctype,
        'Groups': ctx.get_groups(),}
