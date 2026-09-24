# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2016.01
#
# Description: See Ticket #2829
#
############################################

import os
import traceback

DEFAULT_TO = [{'type':'Group', 'id':55}]  # ANI_Leader
DEFAULT_CC = [{'type':'Group', 'id':4},   # PMD
              {'type':'Group', 'id':10}]  # RIG
from production.shotgun_utils.sg_updater import Updater

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"通知并Retake下游动画任务"
        self.description = (u"提交chr类资产时，要根据修改内容判断：\n"
                            u"已经完成的下游动画任务，是否需要重新提交。\n\n"
                            u"注：一般情况下，绑定功能性的修改，不需要；\n"
                            u"而模型更新、或CFX需求导致的修改，需要。")
        self.updater = Updater(self.dialog.sg)
        return

    def proceed(self):
        try:

            #content = self.dialog.w_publish.plainTextEdit_auto_description.toPlainText()
            subject = u'%s 提交了 %s 的新版绑定'%(self.dialog.user['name'],self.dialog.entity['name'])
            ani_users = self.dialog.sg.find('Group', [['code', 'is', 'ani']], ['code', 'users', 'addressings_to','sg_ticket_type', 'sg_priority'])[0]
            rig_users = self.dialog.sg.find('Group', [['code', 'is', 'rig']], ['code', 'users', 'addressings_to','sg_ticket_type', 'sg_priority'])[0]
            pmd_users = self.dialog.sg.find('Group', [['code', 'is', 'pmd']], ['code', 'users', 'addressings_to','sg_ticket_type', 'sg_priority'])[0]
            note = self.dialog.sg.create('Note',
                {'user':self.dialog.user,
                 'content':self.dialog.description,
                 'subject':subject,
                 'addressings_to':[ani_users,rig_users,pmd_users],
                 'project':self.dialog.project,
                 'note_links':[self.dialog.entity],
                 'sg_note_type':u'通知',
                 "sg_sub_type":u'Rig',
                 'tasks':[self.dialog.task]
                 },)
            print "set note",note

            assert hasattr(self.dialog, 'note_and_retake_animation')
            if not self.dialog.note_and_retake_animation:
                self.dialog.print_log('Skip this process.')
                return ""

            # Send Note
            links = []
            links.append(self.dialog.v_info)
            links.append(self.dialog.task)
            links.extend(self.dialog.note_and_retake_animation_tasks)
            subject = u'%s 提交了 %s 的新版绑定'%(
                self.dialog.user['name'],
                self.dialog.entity['name']
            )
            note = self.dialog.sg.create(
                'Note',
                {'user':self.dialog.user,
                 'content':self.dialog.description,
                 'subject':subject,
                 'addressings_to':DEFAULT_TO,
                 'addressings_cc':DEFAULT_CC,
                 'project':self.dialog.project,
                 'note_links':links,
                 'sg_note_type':u'通知',
                 'tasks':self.dialog.note_and_retake_animation_tasks},
            )

            # Upload thumbnail and link to Note
            thumbnail_path = self.dialog.version_dir + '/preview/thumbnail.jpg'
            if os.path.isfile(thumbnail_path):
                self.dialog.sg.upload('Note', note['id'], thumbnail_path)

            # Retake all animation tasks in one batch
            batch_data = []
            reason = '提交了新版绑定'+self.dialog.version_name
            for task in self.dialog.note_and_retake_animation_tasks:
              self.updater.update_task_status(task, 'rtk', reason)
            #     request = {'request_type':'update',
            #                'entity_type':'Task',
            #                'entity_id':task['id'],
            #                'data': {'sg_status_list':'rtk'}}
            
            #    batch_data.append(request)
            # self.dialog.sg.batch(batch_data)
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
