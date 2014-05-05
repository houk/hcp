# -*- coding: utf-8 -*-

from general_helpers import get_button
from general_helpers import get_group_id
from general_helpers import log_activity

### helper functions begin ###

@auth.requires(auth.has_membership('admin'))
def log_create(form):
    '''
        This function creates an entry in the activity table when a host is created
        It's called from a crud form and takes form as an agrument.
    '''
    action = T("Create")
    object = T("Host")
    description = form.vars.hostname
    log_activity(action, object, description)

@auth.requires(auth.has_membership('admin'))
def log_update(form):
    '''
        This function creates an entry in the activity table when a host is created
        It's called from a crud form and takes form as an agrument.
    '''
    action = T("Update")
    object = T("Host")
    description = form.vars.hostname
    log_activity(action, object, description)
    
@auth.requires(auth.has_membership(group_id='admin'))
def log_delete(table, record_id):
    '''
        This function is executed when an account is deleted
    '''
    action = T("Delete")
    object = T("Host")
    description = db.hosts(record_id).hostname
    log_activity(action, object, description)
    
@auth.requires(auth.has_membership('admin'))
def log_update_permissions(host_id):
    '''
        This function creates an entry in the activity table when the permissions for a host are modified
    '''
    action = T("Update")
    object = T("Host Permissions")
    description = db.hosts(host_id).hostname
    log_activity(action, object, description)
    

@auth.requires(auth.has_membership('admin'))
def admin_hosts_account(form):
    '''
        This function makes sure the admin user gets permission to use all hosts
    '''
    check = db.hosts_accounts(group_id=1, hosts_id=form.vars.id)
    if not check:
        db.hosts_accounts.insert(group_id=1, hosts_id=form.vars.id)

### helper functions end ###

@auth.requires(auth.has_membership('admin'))
def index():
    '''
        This function returns a list of currently configured hosts
    '''
    response.title = T("Hosts")
    response.view = 'general/only_content.html'
    
    db.hosts.id.readable = False
    
    query = (db.hosts.id > 0)
    
    maxtextlengths = {'hosts.name':40, 'hosts.hostname':40, }
    links = [ lambda row: A(T("Accounts"), _href=URL('host_permissions', args=[row.id])),
              lambda row: get_button('edit', URL('edit', args=[row.id])) ]
    grid = SQLFORM.grid(query,
                        links=links,
                        details=False,
                        create=False,
                        editable=False,
                        searchable=False,
                        csv=False,
                        maxtextlengths=maxtextlengths,
                        ondelete=log_delete,
                        orderby=db.hosts.hostname)
                        
    grid.element('.web2py_counter', replace=None) # remove the counter
    
    # Add back button to web2py_console div at top of the grid
    add = get_button('add', URL('add'), T("Add a new host"))
    console = grid.element('.web2py_console')
    console.insert(0, add)
    
    return dict(content=grid)
    
   
@auth.requires(auth.has_membership('admin'))
def add():
    '''
        This function shows a page to add a new host
    '''
    response.title = T("New host")
    response.view = 'general/only_content.html'
    
    return_url = URL('index')
    after_create_url = ('host_permissions/[id]')
    
    crud.messages.submit_button = T("Add host")
    crud.messages.record_created = T("Added host")
    crud.settings.create_next = after_create_url
    crud.settings.create_onaccept = [ log_create, admin_hosts_account ]
    form = crud.create(db.hosts)
        
    back = get_button('back', return_url)
    
    return dict(content=form, back=back)
    
@auth.requires(auth.has_membership('admin'))
def edit():
    '''
        This function shows a page to edit a host
        request.args[0] is expected to be the host ID
    '''
    host_id = request.args[0]
    response.title = T("Edit host")
    response.view = 'general/only_content.html'
    
    return_url = URL('index')
       
    crud.messages.submit_button = T("Update host")
    crud.messages.record_updated = T("Updated host")
    crud.settings.update_next = return_url
    crud.settings.update_onaccept = [ log_update, admin_hosts_account ]
    crud.settings.update_deletable = False
    form = crud.update(db.hosts, host_id)
    
    back = get_button('back', return_url)
    
    return dict(content=form, back=back)
    
@auth.requires(auth.has_membership('admin'))
def host_permissions():
    '''
        This functions allows the admin user to specify which accounts can access which hosts
        request.args[0] is expected to be the hosts id
    '''
    host_id = request.args[0]
    response.title = T("Host permissions")
    row = db.hosts(host_id)
    response.subtitle = row.name
    response.view = 'general/only_content.html'
    
    description = B(T("Which accounts have permission to deploy sites to this host?"))
    
    return_url = URL('index')
    
    rows = db(db.auth_group.id > 1).select(db.auth_group.ALL)
    
    form = FORM()
    for row in rows:
        selected = False
        check = db.hosts_accounts(hosts_id=host_id, group_id=row.id)
        if check:
            selected=True
            
        form.append(LABEL(INPUT(_name=row.id, _type="checkbox", _value=row.id, value=selected), " ", row.role))
    form.append(BR())
    form.append(INPUT(_type="submit", _value=T("Update")))
    
    content = DIV(BR(), description, BR(), BR(), form)
    
    if form.process().accepted:
        query = (db.hosts_accounts.hosts_id == host_id)
        db(query).delete()
        for group_id in form.vars:
            if form.vars[group_id]:
                db.hosts_accounts.insert(group_id=group_id, hosts_id=host_id)
        log_update_permissions(host_id)
        
        redirect(return_url)
    
    back = get_button('back', return_url)
    
    return dict(content=content, back=back)
    
    