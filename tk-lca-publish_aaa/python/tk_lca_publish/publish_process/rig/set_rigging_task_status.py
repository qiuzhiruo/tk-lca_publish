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


def open_web(entity_id,task_id,task_name):
    try:
        import webbrowser
        # url = "http://shotgun.zhuiguang.com/detail/Asset/" + str(self.dialog.entity['id']) + "#Task_" + str(task['id'])+"_"+str(task['name'])
        url = "http://shotgun.zhuiguang.com/detail/Asset/" + str(entity_id) + "#Task_" + str(task_id)+"_"+str(task_name)
        hrome_path = '"C:\Users\Lc\AppData\Local\Google\Chrome\Application\chrome.exe" %s'
        webbrowser.get(hrome_path).open(url)
    except:
        pass



# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog=None):
        self.dialog = dialog
        self.process_name = u"设置绑定文件状态。"
        self.description = u"为rigging_facial,rigging_body,rigging设置文件状态"
        self.updater = Updater(self.dialog.sg)
        return

    def proceed(self):
        try:
            reason=u"新 Publish 了（自动认为艺术通过的）Downstream 版本"
            if self.dialog.version_tag == u"完整版":

                task_name = "rigging"
                task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
                task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
                if task_info_rig:
                    self.updater.update_task_status(task, 'sc', reason)
                else:
                    pm.warning("Not task info")
                try:
                    task_name = "rigging_facial"
                    task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
                    if task_info_rig:
                        task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
                        self.updater.update_task_status(task, 'sc', reason)
                except:
                    print traceback.format_exc()


                # try:
                #     task_name = "rigging_blocking"
                #     task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
                #     if task_info_rig:
                #         task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
                #         self.updater.update_task_status(task, 'sc', reason)
                # except:
                #     print traceback.format_exc()


                try:
                    task_name = "rigging_ani"
                    task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
                    if task_info_rig:
                        task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
                        self.updater.update_task_status(task, 'sc', reason)
                except:
                    print traceback.format_exc()

            elif self.dialog.version_tag == u"身体权重":

                task_name = "rigging_body"
                task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
                task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
                if task_info_rig:
                    self.updater.update_task_status(task, 'sc', reason)

            elif self.dialog.version_tag == u"加表情整合":

                task_name = "rigging_facial"
                task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
                task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
                if task_info_rig:
                    self.updater.update_task_status(task, 'sc', reason)

                task_name = "rigging_body"
                task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
                task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
                if task_info_rig:
                    self.updater.update_task_status(task, 'sc', reason)

            sunmark_host = os.getenv('SUNMARK_HOST')
            if sunmark_host != 'http://smk.zhuiguang.com:9001':
                task_name = "rigging"
                task_info_rig = self.dialog.sg.find('Task', [['entity', 'is', self.dialog.entity], ['content','is',task_name]], ["step"])
                task = {'type': 'Task', 'name': task_name, 'id': task_info_rig[0]["id"]}
                if task_info_rig:
                    open_web(self.dialog.entity['id'], task['id'],task['name'])

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
