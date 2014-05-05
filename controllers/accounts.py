# -*- coding: utf-8 -*-

from general_helpers import get_button
from general_helpers import log_activity

### helper functions begin ###
@auth.requires(auth.has_membership(group_id='admin'))
def log_create(form):
    '''
        This function creates an entry n the activity table when a user is created
    '''
    action = T("Create")
    object = T("Account")
    description = form.vars.role
    log_activity(action, object, description)

@auth.requires(auth.has_membership(group_id='admin'))
def log_update(form):
    '''
        This function creates an entry n the activity table when a user is created
    '''
    action = T("Update")
    object = T("Account")
    description = form.vars.role
    log_activity(action, object, description)

@auth.requires(auth.has_membership(group_id='admin'))
def set_account_permissions(form):
    '''
        This function sets up the default permissions for a newly created account.
        These permissions apply to all users in this account(group)
        It's called from a crud form and takes form as an agrument.
    '''
    group_id = form.vars.id
    tables = [ 'auth_user', 'sites' ]
    permissions = [ 'create' ]
    for table in tables:
        for permission in permissions:
            auth.add_permission(group_id, permission, table, 0)
    
@auth.requires(auth.has_membership(group_id='admin'))
def on_delete_account(table, record_id):
    '''
        This function is executed when an account is deleted
    '''
    action = T("Delete")
    object = T("Account")
    description = db.auth_group(record_id).role
    log_activity(action, object, description)
    db(db.auth_user.group_id == record_id).update(group_id = None)
    

### helper functions end ###

@auth.requires(auth.has_membership(group_id='admin'))
def index():
    '''
        This function displays a page which lists auth.group 
        auth.group is used for accounts in this app.
    '''
    response.title = T("Accounts")
    response.view = 'general/only_content.html'
    
    db.auth_group.id.readable = False
    db.auth_group.role.label = T("Account name")
    
    maxtextlengths = {'auth_group.role' : 30, 'auth_group.description' : 50}
    links = [ lambda row: get_button('edit', URL('edit', args=[row.id])) ]
    query = (db.auth_group.id > 1)
    grid = SQLFORM.grid(query,
        links=links,
        details=False,
        create=False,
        editable=False,
        searchable=False,
        csv=False,
        maxtextlengths=maxtextlengths,
        ondelete=on_delete_account)
        
    # Add back button to web2py_console div at top of the grid
    add = get_button('add', URL('add'), T("Add a new account"))
    console = grid.element('.web2py_console')
    console.insert(0, add)
    
    grid.element('.web2py_counter', replace=None) # remove the counter
    
    return dict(content=grid)
    
@auth.requires(auth.has_membership(group_id='admin'))
def add():
    '''
        This function shows a page to add a new user
    '''
    response.title = T("New account")
    response.view = 'general/only_content.html'
    
    db.auth_group.role.label = T("Account name")
    
    return_url = URL('index')
    
    crud.messages.submit_button = T("Add account")
    crud.messages.record_created = T("Added account")
    crud.settings.create_next = return_url
    crud.settings.create_onaccept = [ log_create, set_account_permissions ]
    form = crud.create(db.auth_group)
    
    back = get_button('back', return_url)
    
    return dict(content=form, back=back)
    
@auth.requires(auth.has_membership(group_id='admin'))  
def edit():
    '''
        This function shows a page to edit a user account
        request.args[0] is expected to be the group ID (Account)
    '''
    group_id = request.args[0]
    response.title = T("Edit account")
    response.view = 'general/only_content.html'
    
    db.auth_group.role.label = T("Account name")
    
    return_url = URL('index')
    
    crud.messages.submit_button = T("Update account")
    crud.messages.record_updated = T("Updated account")
    crud.settings.update_next = return_url
    crud.settings.update_onaccept = [ log_update, set_account_permissions ]
    crud.settings.update_deletable = False
    form = crud.update(db.auth_group, group_id)
    
    back = get_button('back', return_url)
    
    return dict(content=form, back=back)