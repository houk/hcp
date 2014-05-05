# -*- coding: utf-8 -*-
"""
    This file contains functions that are useful in more than 1 controller.
"""

import datetime
from gluon import *

def get_group_id():
    '''
        This function returns the group id of the currently logged in user
    '''
    dba = current.globalenv['db']
    w2p_auth = current.globalenv['auth']
    row = dba(dba.auth_membership.user_id == w2p_auth.user.id).select(dba.auth_membership.group_id).first()
    return row.group_id

def get_button(button_type, url, tooltip=""):
    """
        This function returns a button of type "button_type" and redirects to url "url".
        Currently supported for button_type: "back" 
                                             "add"
        The tooltip argument can be used to specify text shown when the mouse hovers over the button
    """
    if button_type == 'add':
        title = current.T("Add")
        icon = "icon plus icon-plus"
    elif button_type == 'edit':
        title = current.T("Edit")
        icon = "icon pencil icon-pencil"
    elif button_type == 'delete':
        title = current.T("Delete")
        icon = "icon remove icon-remove"
    elif button_type == 'delete_notext':
        title = current.T("")
        icon = "icon remove icon-remove"
    elif button_type == 'back':
        title = current.T("Back")
        icon = "icon leftarrow icon-arrow-left"
    elif button_type == 'push':
        title = current.T("")
        icon = "icon chevron right icon-chevron-right"
    elif button_type == 'actions':
        title = current.T("Actions")
        icon = "icon cog icon-cog"
    
    return A(SPAN(_class="buttontext button", _title=tooltip), SPAN(_class=icon), title, _class="button btn", _href=url, _title=tooltip)
    
def log_activity(action, object, description):
    '''
        This function allows easy logging of user activity for auditing
    '''
    dba = current.globalenv['db']
    w2p_auth = current.globalenv['auth']
    user_id = w2p_auth.user.id
    group_id = get_group_id()
    
    dba = current.globalenv['db']
    dba.activity.insert(user_id=user_id,
                        group_id=group_id,
                        hcp_action=action, 
                        hcp_object=object, 
                        description=description)
                        
def none_to_value(var, value):
    '''
        This function check is var is None, if so, it returns value
    '''
    if var is None:
        return value
    else:
        return var