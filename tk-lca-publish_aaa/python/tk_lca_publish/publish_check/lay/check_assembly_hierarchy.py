# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm
import maya.cmds as cmds
import production.mayautils.assembly as assutils

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Assembly Reference 是否全部位于|assets|[grp]下"
        self.description = u"Assembly Reference 必须全部位于|assets|[grp]中"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            top_ars = []
            for ar in pm.ls(type='assemblyReference'):
                ass = assutils.getOpenMayaAssemblyNode(ar.name())
                if ass.isTopLevel():
                    top_ars.append(ar)
            
            illegal_ars = []
            for top_ar in top_ars:
                full_path = cmds.ls(str(top_ar), long = True)[0]
                if not (full_path.startswith('|assets') and len(full_path.split('|')) >= 4):
                    illegal_ars.append(top_ar)
            
            if illegal_ars:
                message = u'以下AR节点层级结构不正确：\n%s' % str(illegal_ars)
                return message
            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

