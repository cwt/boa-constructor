## Script (Python) "User"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name
##title=User
##
acl_users = context.aq_parent.aq_parent
user = acl_users.getUser(name)
return {'id': user.getId(),
        'roles': user.getRoles(),
        'domains': user.getDomains(),
        'passwd': ''}
