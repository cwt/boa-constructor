## Script (Python) "MailHost"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=MailHost
##
ctx = context.aq_parent.aq_parent
return {'title': ctx.title,
        'smtp_host': ctx.smtp_host,
        'smtp_port': ctx.smtp_port}
