# -*- coding: utf-8 -*-

import datetime

from general_helpers import get_group_id

### helper functions begin ###

@auth.requires_login()
def get_users_dict():
    rows = db().select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name)
    d = dict()
    for row in rows:
        d[row.id] = row.first_name + " " + row.last_name
    d[None] = ""
    return d

@auth.requires_login()
def get_groups_dict():
    rows = db().select(db.auth_group.id, db.auth_group.role)
    d = dict()
    for row in rows:
        d[row.id] = row.role
    d[None] = ""
    return d

@auth.requires_login()
def get_hosts_dict():
    rows = db().select(db.hosts.id, db.hosts.name)
    d = dict()
    for row in rows:
        d[row.id] = row.name
    d[None] = ""
    return d

### helper functions end ###

def set_fields_auth_tables():
    '''
        The auth tables are created in the db.py file. 
        However, as all other tables are defined here, modifications to the
        web2py auth_ tables will be made here when possible.
    '''
    db.auth_group.role.unique = True

def set_date_format():
    session.date_formats = [('%Y-%m-%d','yyyy-mm-dd'),('%m-%d-%Y','mm-dd-yyyy'),('%d-%m-%Y','dd-mm-yyyy')]
    if db.hcp_properties(Property='date_format'):
        date_format = db.hcp_properties(Property='date_format').PropertyValue
    else:
        date_format = None
    if date_format == None:
        session.date_format = '%Y-%m-%d'
    else:
        session.date_format = date_format
    session.time_format = '%H:%M'
    session.datetime_format = session.date_format + ' ' + session.time_format

def define_sites():
    group_id = get_group_id()
    dev_query = (db.hosts.dev == True) & (db.hosts.id == db.hosts_accounts.hosts_id) & (db.hosts_accounts.group_id == group_id)
    live_query = (db.hosts.live == True) & (db.hosts.id == db.hosts_accounts.hosts_id) & (db.hosts_accounts.group_id == group_id)
    test_query = (db.hosts.test == True) & (db.hosts.id == db.hosts_accounts.hosts_id) & (db.hosts_accounts.group_id == group_id)
    
    db.define_table('sites',
        Field('group_id', db.auth_group, 
              requires=IS_IN_DB(db(db.auth_group.id > 1),'auth_group.id','%(role)s',zero=(T('Please select...'))), 
              represent=lambda value, row: groups_dict.get(value, None),
              label=T("Account")),
        Field('name', requires=IS_NOT_EMPTY(), label=T('Display name')),
        Field('dev_url', 
            requires=IS_EMPTY_OR([IS_URL(), IS_NOT_IN_DB(db, 'sites.dev_url', error_message=T("URL already exists"))]), 
            label=T("Dev URL")),
        Field('dev_host', db.hosts, 
            requires=IS_EMPTY_OR(IS_IN_DB(db(dev_query),'hosts.id','%(name)s')), 
            represent=lambda value, row: hosts_dict.get(value, None), 
            label=T("Dev Host")),
        Field('live_url', 
            requires=IS_EMPTY_OR([IS_URL(), IS_NOT_IN_DB(db, 'sites.live_url', error_message=T("URL already exists"))]), 
            label=T("Live URL")),
        Field('live_host', db.hosts, 
            requires=IS_EMPTY_OR(IS_IN_DB(db(live_query),'hosts.id','%(name)s')), 
            represent=lambda value, row: hosts_dict.get(value, None), 
            label=T("Live Host")),
        Field('test_url', 
            requires=IS_EMPTY_OR([IS_URL(), IS_NOT_IN_DB(db, 'sites.test_url', error_message=T("URL already exists"))]), 
            label=T("Test URL")),
        Field('test_host', db.hosts, 
            requires=IS_EMPTY_OR(IS_IN_DB(db(test_query),'hosts.id','%(name)s')), 
            represent=lambda value, row: hosts_dict.get(value, None), 
            label=T("Test Host")),
        )
        
def define_sites_users():
    db.define_table('sites_users',
        Field('site_id', db.sites, readable=False, writable=False),
        Field('user_id', db.auth_user,
            label=T("Managed by"))
        )
        
def define_hosts():
    db.define_table('hosts',
        Field('name', requires=IS_NOT_IN_DB(db, 'hosts.name'), label=T("Display name")),
        Field('hostname', requires=IS_NOT_IN_DB(db, 'hosts.hostname'),
                label=T("Hostname"),
                comment=T("eg. www.example.com")),
        Field('host_ip', requires=IS_IPV4(),
                label=T("IP address"),
                comment=T("eg. 198.25.125.234")),
        Field('dev', 'boolean', label=T("Hosts development sites")),
        Field('live', 'boolean', label=T("Hosts live sites")),
        Field('test', 'boolean', label=T("Hosts test sites")),
        )
        
def define_hosts_accounts():
    db.define_table('hosts_accounts',
        Field('hosts_id', db.hosts),
        Field('group_id', db.auth_group),
        )
        
def define_activity():
    db.define_table('activity',
        Field('activity_date', 'date', requires=IS_DATE(format=session.date_format), default=datetime.date.today(), label=T("Date")),
        Field('activity_time', 'time', requires=IS_TIME(), default=datetime.datetime.now().strftime('%H:%M:%S'), label=T("Time")),
        Field('group_id', db.auth_group, represent=lambda value, row: groups_dict.get(value, None), label=T("Account")),
        Field('user_id', db.auth_user, represent=lambda value, row: users_dict.get(value, None), label=T("User")),
        Field('hcp_action', label=T("Action")),
        Field('hcp_object', label=T("Object")),
        Field('description', label=T("Description")))
        
def define_hcp_properties():
    db.define_table('hcp_properties',
        Field('Property', required=True, requires=IS_NOT_EMPTY(), label=T("Property")),
        Field('PropertyValue', 'text', required=True, requires=IS_NOT_EMPTY(), label=T("Value")),
        format='%(Property)s') 
    
def create_admin_user_and_group():
    row = db.auth_user(1)
    if row is None:
        password = db.auth_user.password.validate('admin')[0]
        db.auth_user.insert(id=1, first_name='hcp', last_name='admin', email='admin@hcp.com', password=password, group_id=1) 
    row = db.auth_group(1)
    if row is None:
        db.auth_group.insert(id=1, role='Admin', description='This group has full access')
    auth.add_membership(1, 1) # add the admin user to the admins group
    set_permissions_for_admin_group()
        
def set_permissions_for_admin_group():
    permissions = ['create', 'read', 'update', 'delete', 'select']
    for table in db.tables:
        for permission in permissions:
            auth.add_permission(1, permission, table, 0)
            
            
def set_account_name():
    response.account_name = ""
    if auth.user:
        user_id = auth.user.id # this is the id of the current logged in user
        if user_id == long(1):
            response.account_name = db.auth_group(1).role
        else:
            query = (db.auth_membership.user_id == user_id)
            rows = db(query).select(db.auth_group.ALL,
                                    db.auth_membership.ALL,
                                    left= [ db.auth_group.on(db.auth_group.id == db.auth_membership.group_id) ])
            for row in rows:
                role = row.auth_group.role
                if 'user' not in role:
                    response.account_name = role

'''
Call the functions to define tables and set global values
'''
set_fields_auth_tables()
define_hcp_properties()
set_date_format()

if auth.user:
    define_hosts()
    define_hosts_accounts()
    define_activity()
    define_sites()
    define_sites_users()

    users_dict = get_users_dict()
    groups_dict = get_groups_dict()
    hosts_dict = get_hosts_dict()

create_admin_user_and_group()
#set_account_name()