# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Format and send publish emial
#
############################################

import traceback
import getpass
import sys
import time
import os
import xml.dom.minidom as minidom

from sgtk.platform.qt import QtCore, QtGui
from production.mail.mail import SendMail
import production.notification_rules.recipients as recipients
reload(recipients)

pmd_grp = {'type': 'Group', 'id': 4, 'name': 'PMD'}

# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发送Note(场景过大,修改了相机等)"
        self.description = u"发送相关Note通知相关人员, 如场景过大且flo有理由保留, 修改了相机等"
        return

    def proceed(self):
        try:
            if u'flo修改了相机' not in self.dialog.description or not self.dialog.note_content:
                return ''

            shot_entity = self.dialog.sg.find_one('Shot', [['project', 'name_is', self.dialog.project['name'].upper()],
                                                           ['code', 'is', self.dialog.entity['name']]],
                                                  ['id', 'code'])
            tr = recipients.TaskRecipients()

            if u'flo修改了相机' in self.dialog.description:  # send camera change notes if camera is changed
                users = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name'].upper()], ['entity', 'is', shot_entity], ['content', 'in', ['animation', 'stereo']]], ['task_assignees'])['task_assignees']
                ani_pc = tr.get_dept_pc('ani')
                for i in ani_pc:
                    users.append(self.dialog.sg.find_one('HumanUser', [['login', 'is', i]], ['name', 'login', 'id']))
                # group_pmd_users = self.dialog.sg.find('HumanUser', [['groups', 'is', {'type': 'Group', 'id': 4, 'name': 'PMD'}],['sg_status_list','is','act'],['name','is_not','Yu Zhou'],['name','is_not','Song Yiyi']], ['name', 'login', 'id','groups','sg_status_list'])
                # for group_pmd_user in group_pmd_users:
                #     pass
                
                if pmd_grp not in users:
                    users.append(pmd_grp)
                note = self.dialog.sg.create(
                    'Note',
                    {'user': self.dialog.user,
                     'content': u'flo修改了相机,上下游请注意跟进最新版相机!',
                     'subject': u'{}: FLO新pub版本修改了相机'.format(self.dialog.entity['name']),
                     'addressings_to': users,
                     'project': self.dialog.project,
                     'note_links': [shot_entity],
                     'sg_note_type': u'通知',
                     'tasks': [self.dialog.task]},
                )

            if self.dialog.note_content:  # send scene face number is too big notes
                mail_subject = u'[%s][场景过大预警]%s' % (self.dialog.project['name'].upper(), self.dialog.version_name)
                filters = [['project', 'name_is', self.dialog.project['name'].upper()],['code', 'is', self.dialog.version_name]]
                fields = ['sg_task', 'user', 'code', 'sg_version_type', 'sg_version_type']
                version = self.dialog.sg.find_one("Version", filters, fields)
                sender_sg = None
                if version['user'] and version['user']['type'] == 'HumanUser':
                    sender_sg = self.dialog.sg.find_one('HumanUser', [['id', 'is', version['user']['id']]], ['sg_chinese', 'name', 'login'])

                if sender_sg:
                    # Note to l_recipients
                    receiver_grps = ['SET']
                    receiver_users = recipients.TaskRecipients().get_dept_pc('lay')
                    receiver_users.extend(recipients.TaskRecipients().get_dept_pc('lgt'))
                    receiver_users.extend(recipients.TaskRecipients().get_dept_td('lgt'))

                    receivers = []
                    for recipient in receiver_grps:
                        receiver = self.dialog.sg.find_one('Group', [['code', 'is', recipient]], ['id', 'code'])
                        receivers.append(receiver)

                    for recipient in receiver_users:
                        receiver = self.dialog.sg.find_one('HumanUser', [['login', 'is', recipient]], ['name', 'login', 'id'])
                        receivers.append(receiver)

                    task_assignees = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name'].upper()],
                                                                      ['entity', 'is', shot_entity],
                                                                      ['content', 'is', 'final_layout']],
                                                            ['task_assignees'])['task_assignees']
                    if task_assignees:
                        receivers.extend(task_assignees)

                    # project_entity = self.dialog.sg.find_one('Project',
                    #                                          [['name', 'is', self.dialog.project['name'].upper()]],
                    #                                          ['name', 'sg_cg_sup', 'sg_asset_sup'])
                    # for cg_sup in project_entity['sg_cg_sup']:
                    #     receivers.append(cg_sup)
                    # for asset_sup in project_entity['sg_asset_sup']:
                    #     receivers.append(asset_sup)

                    _receiver = self.dialog.sg.find_one('HumanUser', [['login', 'is', 'gule']], ['name', 'login', 'id'])
                    receivers.append(_receiver)

                note = self.dialog.sg.create('Note', {'user': sender_sg, 'project': self.dialog.project,
                                                      'content': self.dialog.note_content, 'subject': mail_subject,
                                                      'sg_note_type': u'通知', 'addressings_to': receivers ,
                                                      'note_links': [shot_entity],  'tasks': [self.dialog.task]})
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

