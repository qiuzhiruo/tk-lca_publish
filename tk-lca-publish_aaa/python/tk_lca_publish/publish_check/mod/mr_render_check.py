# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if any vertice are overlapping to each other.
#
########################################################################################

import traceback
import maya.cmds as cmds
from production import shotgun_connection
import getpass
from proc.function_running_time import record_time

sg = shotgun_connection.Connection('get_project_info').get_sg()


class MG:

    @staticmethod
    def get_user():
        user_list = []
        user_list.append(sg.find_one('HumanUser', [['login', 'is', 'aokang']], []))
        user_list.append(sg.find_one('HumanUser', [['login', 'is', 'hanbo']], []))
        return user_list


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否加载Mental Ray 渲染器"
        self.description = u"检查是否加载Mental Ray 渲染器，因为渲染农场没有Mental Ray，如果场景中有Mental Ray会导致后面环节渲染错误。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def send_node(self, content):
        user = sg.find_one('HumanUser', [['login', 'is', 'aokang']], [])
        recipients_list = MG.get_user()
        print('recipients_list============>', recipients_list)
        note_info = {'project': self.dialog.project,
                     'content': content,
                     'addressings_to': recipients_list,
                     'sg_note_type': u'通知',
                     'user': user}
        note_id = sg.create('Note', note_info)

    @record_time(__file__)
    def run_check(self):
        try:
            if cmds.pluginInfo('Mayatomr', query=True, n=1 ,l=1):
                msg = '{} 加载了Mental Ray渲染器。'.format(getpass.getuser())

                self.send_node(msg)

                return u'场景中有加载Mental Ray渲染器。'

            mr_nodes = [u'miDefaultFramebuffer',
             u'mentalrayGlobals',
             u'mentalrayItemsList',
             u'Draft',
             u'DraftMotionBlur',
             u'DraftRapidMotion',
             u'miContourPreset',
             u'miDefaultOptions',
             u'Preview',
             u'PreviewCaustics',
             u'PreviewFinalGather',
             u'PreviewGlobalIllum',
             u'PreviewImrRayTracyOff',
             u'PreviewImrRayTracyOn',
             u'PreviewMotionblur',
             u'PreviewRapidMotion',
             u'Production',
             u'ProductionFineTrace',
             u'ProductionMotionblur',
             u'ProductionRapidFur',
             u'ProductionRapidHair',
             u'ProductionRapidMotion']
            for mr_node in cmds.ls(mr_nodes):
                if cmds.lockNode(mr_node, q=1, l=1):
                    cmds.lockNode(mr_node, l=0)
                cmds.delete(mr_node)

            return ""
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''

        try:
            cmds.delete('mentalrayItemsList' ,'mentalrayGlobals' ,'miDefaultOptions', 'miDefaultFramebuffer')
            cmds.flushUndo()
            cmds.unloadPlugin("Mayatomr",f=1)
            return ''

        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


