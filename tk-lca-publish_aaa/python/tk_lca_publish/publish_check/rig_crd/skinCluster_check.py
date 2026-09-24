# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Jingwei Wan
#
# Date: 2018.11
#
# Description: In crd asset, every mesh should be skined by a joint to make sure it can be used in produce a oat asset.
#
########################################################################################

import traceback
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有没有被蒙皮的模型"
        self.description = u"检查是否有没有被蒙皮的模型"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            meshList = pm.listRelatives("hi", ad=1, type="mesh",ni=1)
            for mesh in meshList:
                skinCluster = pm.mel.findRelatedSkinCluster(mesh.getParent())
                if not skinCluster:
                    return "%s is not driven by a skinCluster node!" % mesh
            return ""
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        pass

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
