## Script (Python) "objectids"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=objectids
##
obj = context.aq_parent
if obj.meta_type == 'Local File System' or obj.meta_type == 'Local Directory':
    l = []
    for f in obj.fileIds():
        l.append(f)
    return l
elif obj.meta_type == 'User Folder':
    usernames = obj.getUserNames()
    if usernames:
        # dict or string ? (for exUserFolder)
        try: name = usernames[0]['username']
        except: pass
        else:
            userdicts = usernames
            usernames = []
            for dct in userdicts:
                usernames.append(dct['username'])
    return usernames
else:
    return obj.objectIds()
