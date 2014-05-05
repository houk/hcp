# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('HCP'),XML('&trade;&nbsp;'),
                  _class="brand",_href="http://www.web2py.com/")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

sites_highlighted = False
hosts_highlighted = False
users_highlighted = False
accounts_highlighted = False
activity_highlighted = False
settings_highlighted = False

if request.controller == 'sites':
    sites_highlighted = True
elif request.controller == 'hosts':
    hosts_highlighted = True
elif request.controller == 'users':
    users_highlighted = True
elif request.controller == 'accounts':
    accounts_highlighted = True
elif request.controller == 'activity':
    activity_highlighted = True
elif request.controller == 'settings':
    settings_highlighted = True
    
### create menu
# sites
response.menu = [ (T('Sites'), sites_highlighted, URL('sites', 'index'), []) ]
# hosts
if auth.has_membership('admin'):
    response.menu.append((T('Hosts'), hosts_highlighted, URL('hosts', 'index'), []))
# users
response.menu.append((T('Users'), users_highlighted, URL('users', 'index'), []))
#accounts
if auth.has_membership('admin'):
    response.menu.append((T('Accounts'), accounts_highlighted, URL('accounts', 'index'), []))
# activity
response.menu.append((T('Activity'), activity_highlighted, URL('activity', 'index'), []))
# settings
if auth.has_membership('admin'):
    response.menu.append((T('Settings'), settings_highlighted, URL('settings', 'index'), []))


