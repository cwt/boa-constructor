## Script (Python) "SQLMethod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=SQLMethod
##
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
