l=[]
if function == 'getvalues':
    if self.meta_type == 'Z Class':
        return self.objectMap()
    elif self.meta_type in ('Local File System', 'Local Directory'):
        #return self.manage_options
        for f in self.fileValues():
            l.append(f.type) 
    else:
        for f in self.objectValues():
            l.append(f.meta_type)
    return l
elif function == 'objectids':
    if self.meta_type == 'Local File System' or self.meta_type == 'Local Directory':
        for f in self.fileIds():
            l.append(f)
        return l
    else:
        return self.objectIds()
elif function == 'items':
    return [script(self, 'getvalues'), script(self, 'objectids')]
elif function == '_getObject':
    for obj in self.objectValues():
        try:
            name = obj.id()
        except TypeError:
            name = obj.id
        if name == args:
            return obj
    raise 'Method not found'    
elif function == 'document_src':
    return self.document_src()
elif function == 'meta':
    return self.meta_type
elif function == 'all_meta_types':
    return self.all_meta_types()
elif function == 'undo':        
    return str(self.undoable_transactions(0,1000000))
elif function == 'undoM':        
    obj = script(self, '_getObject', args)
    return str(obj.undoable_transactions(0,1000000))
elif function[:5] == "undoR": #Root Directory
    path=function[5:]
    t=_.string.split(path, '/')
    all=self.undoable_transactions(0,1000000)
    tmp=[]
    for u in all:
        if t==_.string.split(u['description'], '/')[:-1]:
            tmp.append(u)
    return str(tmp)
elif function == 'SQLMethod_Props':
    return {'connection_id': context.connection_id,
            'title':         context.title,
            'arguments':     context.arguments_src,
            'template':      context.src,
            'max_rows':      context.max_rows_,
            'max_cache':     context.max_cache_,
            'cache_time':    context.cache_time_,
            'class_file':    context.class_file_,
            'class_name':    context.class_name_}
    # to return available connections: context.SQLConnectionIDs())
    # Available ZClasses: context.manage_product_zclass_info(), 
elif function == 'DBAdapter_Props':
    return {'title': context.title, 
            'connection_string': context.connection_string}
elif function == 'ExtMethod_Props':
    extMeth = script(self, '_getObject', args)
    return {'title':    extMeth.title, 
            'function': extMeth.function(), 
            'module':   extMeth.module()}
elif function == 'DTMLMethod_Props':
    dtmlMeth = script(self, '_getObject', args)
    return {'title': dtmlMeth.title}
elif function == 'MailHost_Props':
    return {'title': context.title, 
            'smtp_host': context.smtp_host,
            'smtp_port': context.smtp_port}
elif function == 'PageTemplate_Props':
    pageTempl = script(self, '_getObject', args)
    return {'title': pageTempl.title, 
            'content_type': pageTempl.content_type,
            'expand': pageTempl.expand}
elif function == 'images':
    return self.icon
elif function == 'subobj_images':
    return script(self, '_getObject', args).icon
elif function == 'filtered_meta_types':
    return context.filtered_meta_types()
else:
    raise 'Unsupported function'
   