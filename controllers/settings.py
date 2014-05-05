# -*- coding: utf-8 -*-

from general_helpers import get_button

### helper functions begin ###

@auth.requires(auth.has_membership('admin'))
def get_settings():
    '''
        This function returns a dict of settings from the database.
    '''
    general_settings = dict()
    
    if db.hcp_properties(Property='date_format'):
        date_format = db.hcp_properties(Property='date_format').PropertyValue
        for f in session.date_formats:
            if date_format == f[0]:
                date_format = f[1]
    else:
        date_format = 'yyyy-mm-dd'
    general_settings['date_format'] = [ date_format, T("Date format") ]
    
    return general_settings

### helper functions end ###

@auth.requires(auth.has_membership('admin'))
def index():
    '''
        This function shows a page with an overview of current hcp settings
    '''
    
    response.title = T("Settings")
    response.view = 'general/only_content.html'
    
    edit = get_button('edit', URL('edit'))
    
    settings = get_settings()
    settings_keys = sorted(settings, key=lambda key: settings[key])
    
    content = DIV()
    settings_table = TABLE()
    for key in settings_keys:
        settings_table.append(TR(TD(B(settings[key][1])), TD(settings[key][0])))
        
    content.append(edit)
    content.append(settings_table)
    
    return dict(content = content)

@auth.requires(auth.has_membership('admin'))
def edit():
    '''
        This funciton shows a page to edit hcp settings
    '''
    response.title = T("Edit settings")
    response.view = 'general/only_content.html'
    
    return_url = URL('index')
    
    settings = get_settings()
    
    form = SQLFORM.factory(
        Field('date_format', requires=IS_IN_SET(session.date_formats, zero=T("Please select...")), 
                default=settings['date_format'][0], 
                label=settings['date_format'][1]),
        submit_button=T("Update"),
        separator=' '
    )
    
    if form.process().accepted:
        date_format = form.vars.date_format
        if db.hcp_properties(Property='date_format'):
            row = db.hcp_properties(Property='date_format')
            row.PropertyValue = date_format
            row.update_record()
        else:
            db.hcp_properties.insert(Property='date_format', PropertyValue=date_format)
        session.date_format = date_format
        redirect(return_url)
    
    content = form
    
    back = get_button('back', return_url)
    
    return dict(content=content, back=back)