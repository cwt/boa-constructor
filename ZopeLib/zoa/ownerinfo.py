## Script (Python) "ownerinfo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name=None
##title=ownerinfo
##
if name: obj = context.aq_parent.zoa.subobj_(name)
else:    obj = context.aq_parent

try: return obj.owner_info()
except: return {}
