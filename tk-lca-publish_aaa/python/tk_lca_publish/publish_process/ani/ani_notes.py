# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil
import production.notification_rules.recipients as recipients


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Downstream的动画文件发送Note"
        self.description = u"Downstream的动画文件发送Note"
        return

    def proceed(self):
        try:
            info = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name'].lower()],
                                                    ['id', 'is', self.dialog.task['id']]], ['sg_status_list'])
            if not info: return ""
            if info and info['sg_status_list'] in ['wtg', 'rdy', 'ip']: return ""
            links = []
            links.append(self.dialog.v_info)
            subject = u'%s 提交了 %s 的新版动画' % (
                self.dialog.user['name'],
                self.dialog.entity['name']
            )
            # recipient = str(self.dialog.w_publish.lineEdit_email.text())
            # usernames = recipient.replace(',', ' ').replace(u'，', ' ')
            # usernames = usernames.split()
            usernames = []
            users = ''
            if 'pmd' not in usernames:
                usernames.append('pmd')
            if 'cfx_leader' not in usernames:
                usernames.append('cfx_leader')
            if u'ani修改了相机' in self.dialog.description:
                rec = recipients.TaskRecipients()
                lay_lead_list = rec.get_dept_lead('lay')
                usernames.extend(lay_lead_list)

            usernames = list(set(usernames))
            if usernames:
                users = self.dialog.sg.find(
                    'HumanUser',
                    [{'filter_operator': 'any',
                      'filters': [['login', 'is', name] for name in usernames]}]
                )
                users += self.dialog.sg.find(
                    'Group',
                    [{'filter_operator': 'any',
                      'filters': [['code', 'is', name] for name in usernames]}]
                )
            if u'ani修改了相机' in self.dialog.description:
                l_flo_task = self.dialog.sg.find('Task', [['project', 'name_is', self.dialog.project['name']],
                                                          ['entity', 'is', self.dialog.entity],
                                                          ['step', 'name_is', 'flo'],
                                                          ['sg_status_list', 'not_in', ['hld', 'omt']]],
                                                 ['task_assignees'])
                if l_flo_task:
                    for flo_task in l_flo_task:
                        if flo_task['task_assignees']:
                            users += flo_task['task_assignees']

            l_cfx_task = self.dialog.sg.find('Task', [['project', 'name_is', self.dialog.project['name']],
                                                      ['entity', 'is', self.dialog.entity], ['step', 'name_is', 'cfx']],
                                             ['task_assignees'])
            if l_cfx_task:
                for cfx_task in l_cfx_task:
                    if cfx_task['task_assignees']:
                        users += cfx_task['task_assignees']

            note = self.dialog.sg.create(
                'Note',
                {'user': self.dialog.user,
                 'content': self.dialog.description,
                 'subject': subject,
                 'addressings_to': users,
                 'project': self.dialog.project,
                 'note_links': links,
                 'sg_note_type': u'通知',
                 'tasks': [self.dialog.task]},
            )

            thumbnail_path = self.dialog.version_dir + '/preview/thumbnail.jpg'
            if os.path.isfile(thumbnail_path):
                self.dialog.sg.upload('Note', note['id'], thumbnail_path)
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
