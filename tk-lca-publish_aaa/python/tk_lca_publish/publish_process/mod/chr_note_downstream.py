# -*- coding:utf-8 -*-

import getpass
import traceback

from production import shotgun_connection
from proc.function_running_time import record_time


sg = shotgun_connection.Connection('get_project_info').get_sg()


class MG:

    @staticmethod
    def get_user(proj):
        user_list = []
        # for dep in ['Model', 'Surfacing']:
        #     # get pc
        #     user_list.extend(sg.find('HumanUser', [{'filter_operator': 'all', 'filters': [['department_sg_coordinator_departments','name_contains', dep],['sg_status_list','is','act']]}], ['login']))
        # get pc
        user_list.extend(sg.find('HumanUser', [{'filter_operator': 'all', 'filters': [["department.Department.name", "is", "PMD"],
                                                                                      ['projects.Project.name', 'include', proj],
                                                                                      ['login', 'not_in', ['yuzhou', 'gary']],
                                                                                      ['sg_status_list','is','act']]}], ['login']))
        for dep_leader in ['MOD', 'CFX', 'SRF', 'RIG']:
            # get leader
            leader = '{}_leader'.format(dep_leader)
            user_list.extend(sg.find('HumanUser', [{'filter_operator': 'all', 'filters': [['groups','name_contains', leader],['sg_status_list','is','act']]}], ['login']))
        user_list.append(sg.find_one('HumanUser', [['login', 'is', getpass.getuser()]], ['login']))

        for sup in ['lujiangli', 'yangbin', 'huixian', 'bingjue', 'gaochi', 'shengyao', 'haiyang']:
            user_list.append(sg.find_one('HumanUser', [['login', 'is', sup]], ['login']))

        return user_list


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"角色第一次发高模通知下游, 发送hair信息"
        self.description = u"角色第一次发高模通知下游"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            if self.dialog.note_downstream:
                self.send_node(self.dialog.note_msg)
            if self.dialog.hair_info:
                self.send_hair_info(self.dialog.hair_info)
            return ''
        except Exception as e:
            print(traceback.format_exc())
            return ''

    def send_node(self, content):
        user = sg.find_one('HumanUser', [['login', 'is', getpass.getuser()]], [])
        recipients_list = MG.get_user(self.dialog.project['name'].lower())
        reply_content = u'+rig, cfx, srf 请各组检查下文件吧。'
        print('recipients_list============>', recipients_list)

        note_info = {'project': self.dialog.project,
                     'content': content,
                     'addressings_to': recipients_list,
                     'sg_note_type': u'通知',
                     'note_links': [self.dialog.entity, {'type': 'Version', 'id': self.dialog.v_info['id']}],
                     'user': user}
        original_note = sg.create('Note', note_info)

        if self.dialog.is_three_chr:
            reply_content = u'+rig, cfx, srf 此角色完全复用，复用信息请查看描述。'

        sg.create('Reply', {'entity': original_note, 'content': reply_content, 'user': user})

    def send_hair_info(self, content):
        print('>' * 1000)
        print(content)
        # mod, rig，cfx 制片
        for dep in ['Model', 'Rigging', 'Character FX']:
            # get pc
            user_list = sg.find('HumanUser', [{'filter_operator': 'all', 'filters': [['department_sg_coordinator_departments','name_contains', dep],['sg_status_list','is','act']]}], ['login'])

        # 获取leader
        for dep_leader in ['MOD', 'CFX', 'SRF', 'RIG']:
            # get leader
            leader = '{}_leader'.format(dep_leader)
            user_list.extend(sg.find('HumanUser', [{'filter_operator': 'all', 'filters': [['groups','name_contains', leader],['sg_status_list','is','act']]}], ['login']))

        user = sg.find_one('HumanUser', [['login', 'is', getpass.getuser()]], [])
        note_info = {'project': self.dialog.project,
                     'content': content,
                     'addressings_to': user_list,
                     'sg_note_type': u'通知',
                     'note_links': [self.dialog.entity, {'type': 'Version', 'id': self.dialog.v_info['id']}],
                     'user': user}
        sg.create('Note', note_info)

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
