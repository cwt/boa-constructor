## Script (Python) "proxyroles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name=None
##title=proxyroles
##
if name: obj = context.aq_parent.zoa.subobj_(name)
else: obj = context.aq_parent

res = []
for role in obj.valid_roles():
    res.append( (role, obj.manage_haveProxy(role)) )
return res
