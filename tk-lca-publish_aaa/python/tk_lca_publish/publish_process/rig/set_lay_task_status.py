# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2016 Light Chaser Animation
#
# Author: Guo JianWei
#
# Date: 2016.10.19
#
# Description: Export rigging info
#
############################################

import os
import sys
import string
import traceback
import hashlib
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.cmds as cmds
import xml.etree.ElementTree as ET
from production.shotgun_utils.sg_updater import Updater


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog=None):
        self.dialog = dialog
        self.process_name = u"设置绑定文件状态。"
        self.description = u"为rigging_layout设置文件状态"
        self.updater = Updater(self.dialog.sg)
        return

    def proceed(self):
        try:
            reason=u"新 Publish 了（自动认为艺术通过的）Downstream 版本"
            #if self.dialog.version_tag == u"完整版":
            task_name = "rigging_layout"
            task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
            task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
            self.updater.update_task_status(task, 'sc', reason)


            #content = self.dialog.w_publish.plainTextEdit_auto_description.toPlainText()
            subject = u'%s 提交了 %s 的新版绑定'%(self.dialog.user['name'],self.dialog.entity['name'])
            ani_users = self.dialog.sg.find('Group', [['code', 'is', 'lay']], ['code', 'users', 'addressings_to','sg_ticket_type', 'sg_priority'])[0]
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

            try:
                import webbrowser
                url = "http://shotgun.zhuiguang.com/detail/Asset/" + str(self.dialog.entity['id']) + "#Task_" + str(task['id'])+"_"+str(task['name'])
                hrome_path = '"C:\Users\Lc\AppData\Local\Google\Chrome\Application\chrome.exe" %s'
                webbrowser.get(hrome_path).open(url)
            except:
                pass

            # try:
            #     parent_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['parents'])
            #     parent_asset = [sub_asset['name'] for sub_asset in parent_info['parents']] or []
            #     if parent_asset:
            #         c_asset_entity = self.dialog.sg.find_one('Asset',[['project', 'is', self.dialog.project], ['code', 'is', parent_asset[0]]])
            #         c_asset_entity["name"] = parent_asset[0]
            #         c_task_info_rig = self.dialog.sg.find('Task',[['entity', 'is', c_asset_entity], ['content', 'is', task_name]], ["step"])
            #         c_task = {'type': 'Task', 'name': task_name, 'id': c_task_info_rig[0]["id"]}
            #         self.updater.update_task_status(c_task, 'sc', reason)
            #         try:
            #             import webbrowser
            #             url = "http://shotgun.zhuiguang.com/detail/Asset/" + str(self.dialog.entity['id']) + "#Task_" + str(task['id'])+"_"+str(task['name'])
            #             hrome_path = '"C:\Users\Lc\AppData\Local\Google\Chrome\Application\chrome.exe" %s'
            #             webbrowser.get(hrome_path).open(url)
            #         except:
            #             pass
            # except:
            #     pass
            return ""
        except:
            return traceback.format_exc()







    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
