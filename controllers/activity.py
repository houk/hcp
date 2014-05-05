# -*- coding: utf-8 -*-

from general_helpers import get_button
from general_helpers import get_group_id

### helper functions begin ###

@auth.requires_login()
def get_activity_filter(group_id, user_id, action, object, description):
    '''
        This function returns the activity filter
    '''
    actions = [ ('create','Create'), ('update','Update'), ('delete','Delete') ]
    objects = [ ('site','Site'), ('user','User') ]
    
    if auth.has_membership('Admin'): 
        users_query = (db.auth_user.id > 0)
        if not group_id is None and not group_id == '':
            users_query = (db.auth_user.group_id == group_id)
        objects.insert(0, ('account','Account'))
        objects.insert(1, ('host','Host'))
        objects.insert(2, ('host permissions','Host permissions'))
    else:
        users_query = (db.auth_user.group_id == get_group_id())
    form = SQLFORM.factory(
        Field('group_id', db.auth_group, default=group_id, 
            requires=IS_IN_DB(db, 'auth_group.id', '%(role)s', zero=T("All accounts"))), 
        Field('user_id', db.auth_user, default=user_id,
            requires=IS_IN_DB(db(users_query), 'auth_user.id', '%(first_name)s %(last_name)s', zero=T("All users"))), 
        Field('action', requires=IS_IN_SET(actions, zero=T("All actions")), default=action),
        Field('object', requires=IS_IN_SET(objects, zero=T("All objects")), default=object),
        Field('description', default=description),
        submit_button=T("Find"),
        )
        
    show_all = A(T("Show all"), _href=URL('show_all'))
        
    # sumbit form on change
    selects = form.elements('select')
    for select in selects:
        select.attributes['_onchange'] = "this.form.submit();"
        
    account = ''
    if auth.has_membership('Admin'):
        account = form.custom.widget.group_id
        
    form = DIV(
        form.custom.begin,
        account,
        form.custom.widget.user_id,
        form.custom.widget.action,
        form.custom.widget.object,
        form.custom.widget.description,
        form.custom.submit,
        show_all,
        form.custom.end,
        _class='hcp-activity_search right')
        
    return form

### helper functions end ###

@auth.requires_login()
def index():
    '''
        This function shows a page which lists the activity of users
    '''
    response.title = T("Activity")
    response.view = 'general/only_content.html'
    db.activity.id.readable = False
    
    query = (db.activity.id > 0)
    if not auth.has_membership('admin'):
        group_id = get_group_id()
        query &= (db.activity.group_id == group_id)
        
    if 'user_id' in request.vars:
        # account
        if auth.has_membership('Admin'):
            group_id = request.vars['group_id']
            session.activity_group_id = group_id
            if len(group_id) > 0:
                query &= (db.activity.group_id == group_id)
        # user
        user_id = request.vars['user_id']
        session.activity_user_id = user_id
        if len(user_id) > 0:
            query &= (db.activity.user_id == user_id)
        # action
        action = request.vars['action']
        session.activity_action = action
        if len(action) > 0:
            query &= (db.activity.hcp_action == action)
        # object
        object = request.vars['object']
        session.activity_object = object
        if len(object) > 0:
            query &= (db.activity.hcp_object == object)        
        # description
        description = request.vars['description']
        session.activity_description = description
        if len(description) > 0:
            query &= (db.activity.description == description)
        
        response.subtitle = T("Showing search results")
    elif not session.activity_group_id is None or \
         not session.activity_user_id is None or \
         not session.activity_action is None or \
         not session.activity_object is None or \
         not session.activity_description is None:
        # account
        if (not session.activity_group_id is None and session.activity_group_id == ''):
            query &= (db.activity.group_id == session.activity_group_id)
        # user
        if (not session.activity_user_id is None and session.activity_user_id == ''):
            query &= (db.activity.user_id == session.activity_user_id)
        # action
        if (not session.activity_action is None and session.activity_action == ''):
            query &= (db.activity.hcp_action == session.activity_action)        
        # object
        if (not session.activity_object is None and session.activity_object == ''):
            query &= (db.activity.hcp_object == session.activity_object)        
        # description
        if (not session.activity_description is None and session.activity_description == ''):
            query &= (db.activity.description == session.activity_description)
    else:
        response.subtitle = T("Showing all records")
        
        
    
    fields = [ db.activity.activity_date,
               db.activity.activity_time,
               db.activity.group_id,
               db.activity.user_id,
               db.activity.hcp_action,
               db.activity.hcp_object,
               db.activity.description ]
               
    
    maxtextlengths = {'activity.description' : 30}
    grid = SQLFORM.grid(query,
        fields=fields,
        create=False,
        editable=False,
        deletable=False,
        searchable=False,
        csv=False,
        maxtextlengths=maxtextlengths,
        left=[ db.auth_group.on(db.auth_group.id==db.activity.group_id),
               db.auth_user.on(db.auth_user.id==db.activity.user_id) ],
        orderby=~db.activity.activity_date|~db.activity.activity_time)
        
    form = get_activity_filter(session.activity_group_id, 
                               session.activity_user_id, 
                               session.activity_action,
                               session.activity_object,
                               session.activity_description)
    content = DIV(form, grid)
    
    return dict(content=content)
    
    
@auth.requires_login()
def show_all():
    '''
        This function resets the filter completelys
    '''
    session.activity_group_id = None
    session.activity_user_id = None
    session.activity_action = None
    session.activity_object = None
    session.activity_description = None
    redirect(URL('index'))