## Script (Python) "version"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj_ids=(), obj_metatypes=None, obj_searchterm=None, search_sub=1
##title=find
##

# silly xml-rpc restrictions
if obj_ids==(): obj_ids=None
if obj_metatypes==0: obj_metatypes=None
if obj_searchterm==0: obj_searchterm=None

results = context.ZopeFind(context.aq_parent, obj_ids=obj_ids,
          obj_metatypes=obj_metatypes, obj_searchterm=obj_searchterm,
          search_sub=search_sub)
##, obj_expr=None, obj_mtime=None,
##obj_mspec=None, obj_permission=None, obj_roles=None, search_sub=1,
##REQUEST=REQUEST))
return [(obj.meta_type, id) for id, obj in results]
