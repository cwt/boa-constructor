## Script (Python) "move_field"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dir, group, field, togroup=''
##title=move_field
##
ctx = context.aq_parent.aq_parent.aq_parent
REQ = ctx.REQUEST
REQ.form[field] = 1
if dir == 'up':
    return ctx.manage_move_field_up(group, REQ)
elif dir == 'down':
    return ctx.manage_move_field_down(group, REQ)
elif dir == 'group':
    return ctx.manage_move_group(group, togroup, REQ)
