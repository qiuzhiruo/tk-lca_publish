# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: No referenced nodes under |master.
#
########################################################################################

import traceback
import pymel.core as pm
import maya.cmds as cmds
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否用publish工具存master以及version"
        self.description = u"检查是否用publish工具存master以及version"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            if not pm.objExists("master.save_master"):
                return "文件没有用publish工具存master"
            else:
                version_info = cmds.about(version=True)
                if version_info > '2019':
                    return "文件没有用maya2019制作"
                else:
                    return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        pass
    #
    # if not mc.objExists("master.save_master"):
    #     save_master = pm.PyNode("master")
    #     save_master.addAttr("save_master")

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



