# -*- coding:utf-8 -*-

import os
import getpass
from production import shotgun_connection

sg = shotgun_connection.Connection('get_project_info').get_sg()


class MG:

    @staticmethod
    def get_user():
        user_list = []
        for dep in ['Model', 'Animation', 'Layout']:
            # get pc
            user_list.extend(sg.find('HumanUser', [{'filter_operator': 'all', 'filters': [['department_sg_coordinator_departments','name_contains', dep],['sg_status_list','is','act']]}]))
        for dep_leader in ['ANI', 'LAY', 'MOD']:
            # get leader
            leader = '{}_leader'.format(dep_leader)
            user_list.extend(sg.find('HumanUser', [{'filter_operator': 'all', 'filters': [['groups','name_contains', leader],['sg_status_list','is','act']]}]))
        user_list.append(sg.find_one('HumanUser', [['login', 'is', getpass.getuser()]], []))
        return user_list

    @staticmethod
    def get_recipients():
        recipients_list = []
        recipients_list.extend(MG.get_user())
        recipients_list.append(getpass.getuser())
        recipients_list = [sg.find_one('HumanUser', [['login', 'is', name]], []) for name in recipients_list]

        return recipients_list


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发送asb修改信息note"
        self.description = u"给相关人员发送asb修改信息"
        return

    def proceed(self):
        if self.dialog.ar_msg:
            self.send_node(self.dialog.ar_msg)
        return ''


    def send_node(self, content):
        user = sg.find_one('HumanUser', [['login', 'is', 'aokang']], [])
        recipients_list = MG.get_user()
        print('recipients_list============>', recipients_list)
        note_info = {'project': self.dialog.project,
                     'content': content,
                     'addressings_to': recipients_list,
                     'sg_note_type': u'通知',
                     'note_links': [self.dialog.entity],
                     'user': user}
        note_id = sg.create('Note', note_info)

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



