# -*- coding: utf-8 -*-

from general_helpers import get_button
from general_helpers import get_group_id
from general_helpers import none_to_value
from general_helpers import log_activity

### helper functions begin ###

@auth.requires_login()
def log_create(form):
    '''
        This function creates an entry n the activity table when a site is created
        It's called from a crud form and takes form as an agrument.
    '''
    action = T("Create")
    object = T("Site")
    description = form.vars.name
    log_activity(action, object, description)
    
@auth.requires_login()
def assign_to_user(form):
    '''
        This function assigns a user as the manager of a site
        It's called from a crud form and takes form as an argument.
    '''
    user_id = auth.user.id
    check = db.sites_users(user_id=user_id, site_id=form.vars.id)
    if not check:
        db.sites_users.insert(user_id=user_id, site_id=form.vars.id)
        
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
    site_id = form.vars.id
    auth.add_permission(group_id, 'update', 'sites', site_id)
    
    # now remove old permissions
    query = (db.auth_permission.table_name == 'sites') & \
            (db.auth_permission.record_id == site_id) & \
            (db.auth_permission.group_id != 1) & \
            (db.auth_permission.group_id != group_id)
    db(query).delete()
    
@auth.requires_login()
def log_update(form):
    '''
        This function creates an entry n the activity table when a site is created
        It's called from a crud form and takes form as an agrument.
    '''
    if form.vars.delete_this_record == 'on':
        action = T("Delete")
    else:
        action = T("Update")
    object = T("Site")
    description = form.vars.name
    log_activity(action, object, description)
    
@auth.requires_login()
def get_user_quota(user_id):
    '''
        This function returns the user quota
    '''
    return int(none_to_value(db.auth_user(user_id).site_quota, 0))


### helper functions end ###

@auth.requires_login()
def index():
    '''
        This page displays a list of sites
    '''
    def get_url(link):
        '''
            This helper turns the text of a link into a clickable link
        '''
        return A(link, _href=link)
    def get_edit_link(site_id, site_name):
        '''
            This function returns a settings button for a site to edit it's properties
        '''
        return A(site_name, _href=URL('edit', args=[site_id]), _class='sites_settings_icon')
    def get_quota_count():
        '''
            This function returns a count of the site quota by account
            and by user.
        '''
        user_id = auth.user.id
        if user_id == 1:
            return B(T('Admin: No site creation limit.'))
        else:
            group_id = get_group_id()
            quota_account = unicode(db.auth_group(group_id).site_quota)
            quota_user = unicode(get_user_quota(user_id))
            
            used_account = db(db.sites.group_id == group_id).count()
            used_account = unicode(none_to_value(used_account, 0))
            used_user = db(db.sites_users.user_id == user_id).count()
            used_user = unicode(none_to_value(used_user, 0))
            
            account_name = db.auth_group(group_id).role
            user = db.auth_user(user_id)
            user_name = user.first_name + ' ' + user.last_name
            title = B(T("Sites created") + ': ')
            stats = TABLE(TR(
                    TD(title),
                    ),
                TR(
                    TD(B(account_name)),
                    TD(used_account + '/' + quota_account),
                    TD(B(user_name)),
                    TD(used_user + '/' + quota_user)
                )
            )
            return stats
    def get_search_form(search_string='', search_user_id=0, search_group_id=None):
        '''
            This function returns a search form for sites
        '''
        if auth.has_membership('Admin'): 
            users_query = (db.auth_user.id > 0)
            if not search_group_id is None and not search_group_id == '':
                users_query = (db.auth_user.group_id == search_group_id)
        else:
            users_query = (db.auth_user.group_id == get_group_id())
        form = SQLFORM.factory(
            Field('search_group_id', db.auth_group, default=search_group_id, 
                requires=IS_IN_DB(db, 'auth_group.id', '%(role)s', zero=T("All accounts"))), 
            Field('search_user_id', db.auth_user, default=search_user_id,
                requires=IS_IN_DB(db(users_query), 'auth_user.id', '%(first_name)s %(last_name)s', zero=T("All users"))), 
            Field('search', default=search_string), label=T(''),
            submit_button = T("Find")
        )
        show_all = A(T("Show all"), _href=URL('show_all'))
        
        # sumbit form on change
        selects = form.elements('select')
        for select in selects:
            select.attributes['_onchange'] = "this.form.submit();"
        
        if auth.has_membership('Admin'):
            account = form.custom.widget.search_group_id
        else:
            account = ''
        
        form = DIV(
            form.custom.begin,
            account,
            form.custom.widget.search_user_id,
            form.custom.widget.search,
            form.custom.submit,
            show_all,
            form.custom.end,
            _class='hcp-sites_search right'
            )
        
        return form
        
        
    response.title = T("Sites")
    response.view = 'general/only_content.html'
    response.subtitle = T("Showing all sites")
    
    query = (db.sites.id > 0) # show all sites
    if 'search' in request.vars:
        search = request.vars.search
        session.sites_search = search
        if len(search) > 0:
            search_name = '%' + search.strip() + '%'
            query &= (db.sites.name.like(search_name))
            
        search_user_id = request.vars.search_user_id
        session.sites_user_id = search_user_id
        if len(search_user_id) > 0:
            query &= (db.sites_users.user_id == search_user_id)
            
        
        search_group_id = request.vars.search_group_id
        if not search_group_id is None: # this value can only be set when logged in as the admin user
            session.sites_group_id = search_group_id
            if len(search_group_id) > 0:
                query &= (db.sites.group_id == search_group_id)
            
        response.subtitle = T("Showing search results")
    elif (not session.sites_search == None and len(session.sites_search) > 0) or \
         not session.sites_user_id == None or \
         not session.sites_group_id == None: 
        if len(session.sites_search) > 0:
            search_name = '%' + session.sites_search.strip() + '%'
            query &= (db.sites.name.like(search_name))
        
        if len(session.sites_user_id) > 0:
            query &= (db.sites_users.user_id == session.sites_user_id)
            
        if not session.sites_group_id == None: # this value can only be set when logged in as the admin user
            if len(session.sites_group_id) > 0:
                query &= (db.sites.group_id == search_group_id)
        
        response.subtitle = T("Showing search results")

    if len(request.args): 
        page = int(request.args[0])
    else: 
        page = 0
    items_per_page = 20
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    
    sites = TABLE(TR(TH(T("Site")), 
                     TH(T("Dev")), 
                     TH(T("Push")), 
                     TH(T("Live")),
                     TH(T("Push")), 
                     TH(T("Test")),
                     TH(T("Edit")),
                     TH(T("Actions")),
                     ), _class='hcp-sites_table')
                     
    group_id = get_group_id()
    if group_id > 1:
        query &= (db.sites.group_id==get_group_id())
        
    rows = db(query).select(db.sites.ALL, 
                            left=[db.sites_users.on(db.sites.id==db.sites_users.site_id),
                                  db.auth_group.on(db.sites.group_id==db.auth_group.id)],
                            orderby=db.auth_group.role|db.sites.name,
                            limitby=limitby)
    i = 0
    for row in rows.render():
        if i == items_per_page:
            break
        site = TR(
                TD(SPAN(row.name, _class='site_name'), BR(), row.group_id),
                TD(get_url(row.dev_url), BR(), row.dev_host),
                TD(get_button('push', URL('index'))),
                TD(get_url(row.live_url), BR(), row.live_host),
                TD(get_button('push', URL('index'))),
                TD(get_url(row.test_url), BR(), row.test_host),
                TD(get_button('edit', URL('edit', args=[row.id]))),
                TD(get_button('actions', URL('actions', args=[row.id]))))
        
        sites.append(site)
        i += 1
    
    if not auth.has_membership('admin'):
        add = get_button('add', URL('add')) 
    else:
        add = '' # we don't allow the super user(s) to create sites, as the managed by user_id in sites_users wouldn't be set correctly
    search = get_search_form(session.sites_search, session.sites_user_id, session.sites_group_id)
    
    previous = ''
    next = ''
    if page > 0:
        previous = A(T("Previous"), _href=URL(args=[page - 1]))
    if len(rows) > items_per_page:
        next = A(T("Next"), _href=URL(args=[page + 1]))
        
    page_controls = DIV(previous, " ", next, _class='right')
    quota_count = get_quota_count()
    
    content = DIV(add, " ", search, BR(), sites, quota_count, page_controls)
    
    return dict(content=content)

@auth.requires_login()
def show_all():
    '''
        This function clears all searches.
    '''
    session.sites_search = None
    session.sites_user_id = None
    session.sites_group_id = None
    redirect(URL('index'))
    
@auth.requires_login()
def add():
    '''
        This function shows a page that allows adding of a new site
    '''
            
    response.title = T("New site")
    response.view = 'general/only_content.html'
    
    user_id = auth.user.id
    group_id = get_group_id()
    
    if not auth.has_membership('admin'): # just in case we'll allow the admin to create sites in the future
        db.sites.group_id.readable = False
        db.sites.group_id.writable = False
        db.sites.group_id.default = get_group_id()
    
    return_url = URL('index')
    
    crud.messages.submit_button = T("Add")
    crud.messages.record_created = T("Added site")
    crud.settings.create_next = return_url
    crud.settings.create_onaccept = [ log_create, assign_to_user, set_update_permission ]
    form = crud.create(db.sites)
    
    content = form
    if user_id > 1: # check quotas for not admin users
        account_count = db(db.sites.group_id == group_id).count()
        account_quota = db.auth_group(group_id).site_quota
        user_count = db(db.sites_users.user_id == user_id).count() 
        user_quota = get_user_quota(user_id)
    
        if account_count >= account_quota:
            content = DIV(BR(), B(T("Unable to create a new site, maximum allowed sites reached for this account.")))
        elif user_count >= user_quota :
            content = DIV(BR(), B(T("Unable to create a new site, you've reached your maximum allowed sites.")))
    
    back = get_button('back', return_url)
    
    return dict(content=content, back=back)
    
    

@auth.requires_login()
def edit():
    """
        This function shows an edit page for a site
        request.args[0] is expected to be the site id
    """
    site_id = request.args[0]
    response.title = T("Edit site")
    response.view = 'general/only_content.html'
    
    if not auth.has_membership('admin'):
        db.sites.group_id.readable = False
        db.sites.group_id.writable = False
        db.sites.group_id.default = get_group_id()
    
    return_url = URL('index')
    
    crud.messages.submit_button = T("Update")
    crud.messages.record_updated = T("Updated site")
    crud.settings.update_next = return_url
    crud.settings.update_onaccept = [ log_update, set_update_permission ]
    crud.settings.update_deletable = True
    form = crud.update(db.sites, site_id)
    
    back = get_button('back', return_url)
    
    return dict(content=form, back=back)
    
@auth.requires_login()
def actions():
    '''
        This function returns a page with actions for a site
        request.args[0] is expected to be the site id
    '''
    site_id = request.args[0]
    response.title = T("Actions")
    row = db.sites(site_id)
    response.subtitle = row.name
    response.view = 'general/only_content.html'
    
    return_url = URL('index')
    
    if auth.has_membership('Admin') or auth.has_permission('update','sites',site_id):
        content = DIV()
        edit_manager = LOAD('sites', 'edit_manager.load/' + site_id, ajax=True, vars=request.vars, _class='right')
        content.append(edit_manager)
    else:    
        content = ""
        redirect(URL('default', 'user', args=['not_authorized']))
    
    back = get_button('back', return_url)
    
    return dict(content=content, back=back)
    
@auth.requires_login()
def edit_manager():
    '''
        This function shows a page that allows to change the manager of the page
        (the owning user).
        request.args[0] is expected to be the site id
    '''
    site_id = request.args[0]
    site = db.sites(site_id)
    group_id = site.group_id
    message = ''

    if 'user_id' in request.vars:
        user_id = request.vars.user_id
        quota_user = get_user_quota(user_id)
        used_user = db(db.sites_users.user_id == user_id).count()
        
        if used_user >= quota_user or quota_user == 0:
            row = db.auth_user(user_id)
            message = T("Quota reached for") + ' ' + row.first_name + ' ' + row.last_name
        else:
            row = db.sites_users(site_id=site_id)
            if not row is None:
                row.user_id = user_id
                row.update_record()
            else:
                db.sites_users.insert(user_id=user_id, site_id=site_id)
    
    db.sites_users.id.readable = False
        
    query = (db.auth_user.group_id == group_id) # allow only users from the same account to take over
    db.sites_users.user_id.requires=IS_IN_DB(db(query), 'auth_user.id', '%(first_name)s %(last_name)s', 
                                             zero=T("Please select..."), 
                                             error_message=T("Please select a user"))
    
    record = db.sites_users(site_id=site_id)
    form = SQLFORM(db.sites_users, record,
                   buttons=[])
    
    selects = form.elements('select')
    for select in selects:
        select.attributes['_onchange'] = "this.form.submit();"    
    
    form = DIV(
        form.custom.begin,
        B(form.custom.label.user_id, _class='left'),
        BR(),
        form.custom.widget.user_id,
        BR(), message,
        form.custom.end
        )
    
    return dict(content=form)