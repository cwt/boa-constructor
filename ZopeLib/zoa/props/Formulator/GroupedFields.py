## Script (Python) "GroupedFields"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=GroupFields
##
ctx = context.aq_parent.aq_parent.aq_parent
result = []
for group in ctx.get_groups():
    fields = []
    for field in ctx.get_fields_in_group(group):
        fields.append( (field.id, field.meta_type) )
    result.append( (group, fields) )
return result
