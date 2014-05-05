# -*- coding: utf-8 -*-

from general_helpers import get_button
from general_helpers import get_group_id
from general_helpers import log_activity

### helper functions begin ###
@auth.requires(auth.has_membership('admin'))
def get_account_filter_form(account=''):
    '''
        This function returns a form that's used to filter accounts
    '''
    form = SQLFORM.factory(
        Field('account', db.auth_group, default=account,
              requires=IS_IN_DB(db(db.auth_group.id > 1),'auth_group.id','%(role)s',zero=(T('All accounts'))),
              label=''),
        submit_button=T("Find")
    )
    
    # make the form submit on change when js is supported
    form.element('select').attributes['_onchange'] = "this.form.submit();"
    
    # remodel the form horizontally in a div and add classes for formatting
    filter_form = DIV(form.custom.begin,
                      form.custom.widget.account,
                      form.custom.submit,
                      form.custom.end,
                      _class="hcp-account_filter_form right")

    return filter_form


@auth.requires_login()
def set_auth_group_id_requires():
    '''
        This function returns the validator for the auth_user.group_id field
    '''
    return IS_IN_DB(db(db.auth_group.id > 1),'auth_group.id','%(role)s',zero=(T('Select account...')))
    
@auth.requires_login()
def user_update_membership(form):
    '''
        This function adds the user to the selected group in the group_id field (account)
        It's called from a crud form and takes form as an agrument.
    '''
    if auth.user.id == 1: # only admin can move users from account to account
        user_id = form.vars.id
        group_id = form.vars.group_id
        
        if not auth.has_membership(group_id, user_id):
            # add new membership
            auth.add_membership(group_id, user_id)
            # remove all previous registrations
            query = (db.auth_membership.user_id == user_id) & ((db.auth_membership.group_id != group_id) | (db.auth_membership.group_id == None))
            db(query).delete()
        

@auth.requires_login()
def log_create(form):
    '''
        This function creates an entry n the activity table when a user is created
        It's called from a crud form and takes form as an agrument.
    '''
    action = T("Create")
    object = T("User")
    description = form.vars.first_name + ' ' + form.vars.last_name + ' (' + form.vars.email + ')'
    log_activity(action, object, description)

@auth.requires_login()
def log_update(form):
    '''
        This function creates an entry n the activity table when a user is created
        It's called from a crud form and takes form as an agrument.
    '''
    action = T("Update")
    object = T("User")
    description = form.vars.first_name + ' ' + form.vars.last_name + ' (' + form.vars.email + ')'
    log_activity(action, object, description)
    
@auth.requires_login()
def log_delete(table, record_id):
    '''
        This function is executed when an account is deleted
    '''
    action = T("Delete")
    object = T("User")
    row = db.auth_user(record_id)
    description = row.first_name + ' ' + row.last_name
    log_activity(action, object, description)
    
@auth.requires_login()
def set_update_permission(form):
    '''
        This function grant update permission of the site to the users 
        in the account it's linked to.
    '''
    if auth.has_membership('Admin'):
        group_id = form.vars.group_id    
    else:
        group_id = get_group_id()
    user_id = form.vars.id
    auth.add_permission(group_id, 'update', 'auth_user', user_id)
    
    # now remove old permissions
    query = (db.auth_permission.table_name == 'auth_user') & \
            (db.auth_permission.record_id == user_id) & \
            (db.auth_permission.group_id != 1) & \
            (db.auth_permission.group_id != group_id)
    db(query).delete()
    
@auth.requires_login()
def check_account_change(form):
    '''
        This function checks whether the user is being transferred from one account to another
    '''
    if auth.has_membership('Admin'):
        user_id = form.vars.id
        rows = db(db.sites_users.user_id == user_id).select(db.sites_users.ALL)
        for row in rows:
            site_group_id = db.sites(row.site_id).group_id
            user_group_id = db.auth_membership(user_id = user_id).group_id
            if site_group_id != user_group_id:
                db(db.sites_users.id == row.id).delete()

        
        
        
    
    
### helper functions end ###

@auth.requires_login()
def index():
    '''
        This function shows a page which lists the user accounts
    '''
    response.title = T("Users")
    response.view = 'general/only_content.html'
    db.auth_user.id.readable = False
    db.auth_group.role.label = T("Account")
    db.auth_group.role.represent = lambda value, row: value or ""
    
    query = (db.auth_user.id > 1)
    account = ""
    
    if 'account' in request.vars:
        account = request.vars['account']
        session.users_account = account
    elif session.users_account != None:
        account = session.users_account
    if not account is None and not account == '':
        query &= (db.auth_user.group_id == account)
    
    if not auth.has_membership('admin'):
        group_id = get_group_id()
        query &= (db.auth_user.group_id == group_id)
    
    fields = [ db.auth_user.first_name,
               db.auth_user.last_name,
               db.auth_user.email,
               db.auth_user.site_quota,
               db.auth_group.role ]
    
    maxtextlengths = {'auth_user.email' : 30}
    links = [ lambda row: get_button('edit', URL('edit', args=[row.auth_user.id])) ]
    grid = SQLFORM.grid(query,
        fields=fields,
        links=links,
        details=False,
        create=False,
        editable=False,
        searchable=False,
        csv=False,
        maxtextlengths=maxtextlengths,
        left=[db.auth_group.on(db.auth_group.id==db.auth_user.group_id)],
        ondelete=log_delete,
        orderby=db.auth_group.role|db.auth_user.first_name)
        
    # Add back button to web2py_console div at top of the grid
    add = get_button('add', URL('add'), T("Add a new user"))
    console = grid.element('.web2py_console')
    console.insert(0, add)
    if auth.has_membership('admin'):
        console.append(get_account_filter_form(account))
    
    grid.element('.web2py_counter', replace=None) # remove the counter
    
    return dict(content=grid)
    
@auth.requires_login()
def add():
    '''
        This function shows a page to add a new user
    '''
    response.title = T("New hcp user")
    response.view = 'general/only_content.html'
    
    return_url = URL('index')
    
    db.auth_user.group_id.requires = set_auth_group_id_requires()
    
    if not auth.has_membership('admin'):
        group_id = get_group_id
        db.auth_user.group_id.readable = False
        db.auth_user.group_id.writable = False
        db.auth_user.group_id.default = group_id
    
    crud.messages.submit_button = T("Add user")
    crud.messages.record_created = T("Added user")
    crud.settings.create_next = return_url
    crud.settings.create_onaccept = [ user_update_membership, log_create, set_update_permission ]
    form = crud.create(db.auth_user)
        
    back = get_button('back', return_url)
    
    return dict(content=form, back=back)
    
@auth.requires_login()
def edit():
    '''
        This function shows a page to edit a user account
        request.args[0] is expected to be the user ID
    '''
    user_id = request.args[0]
    response.title = T("Edit hcp user")
    response.view = 'general/only_content.html'
    
    return_url = URL('index')
    
    db.auth_user.group_id.requires = set_auth_group_id_requires()
    if not auth.has_membership('admin'):
        db.auth_user.group_id.readable = False
        db.auth_user.group_id.writable = False
    
    crud.messages.submit_button = T("Update user")
    crud.messages.record_updated = T("Updated user")
    crud.settings.update_next = return_url
    crud.settings.update_onaccept = [ user_update_membership, log_update, set_update_permission, check_account_change ]
    crud.settings.update_deletable = False
    form = crud.update(db.auth_user, user_id)
    
    back = get_button('back', return_url)
    
    return dict(content=form, back=back)