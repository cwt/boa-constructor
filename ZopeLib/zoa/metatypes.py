## Script (Python) "metatypes"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=metatypes
##
obj = context.aq_parent
l=[]
if obj.meta_type == 'Z Class':
    return obj.objectMap()
elif obj.meta_type in ('Local File System', 'Local Directory'):
    for f in obj.fileValues():
        if f.type == 'directory':
            l.append('LocalFS::directory')
        else:
            l.append('LocalFS::file')
# pretend that users are subobjects with meta_types
elif obj.meta_type == 'User Folder':
    return ['User'] * _.len(obj.getUserNames())
else:
    for f in obj.objectValues():
        try: l.append(f.meta_type)
        except: l.append('Broken Because Product is Gone')
return l
