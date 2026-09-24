# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Jingwei Wan
#
# Date: 2018.11
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil
import maya.cmds as mc
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"reorder层级, 使输出绑定满足制作正确action的要求"
        self.description = u"reorder层级, 使输出绑定满足制作正确action的要求"
        return

    # CJW 由于 |master|rig|anim_rig 被锁住，所以无法reorder(重排)骨骼
    def proceed(self):
        try:
            import pymel.core as pm
            
            if pm.objExists("rig"):
                # CJW rig组下所有子物体解锁
                rigObjs = mc.listRelatives('rig', ad=1)
                for r in rigObjs:
                    mc.lockNode(r,lock=False)
                pm.reorder("rig", front=1)
            else:
                return "no rig group to perform reorder!"                

            if pm.objExists("anim_skeletons_grp"):
                pm.reorder("anim_skeletons_grp", front=1)
                # CJW rig组下所有子物体解锁
                rigObjs = mc.listRelatives('rig', ad=1)
                for r in rigObjs:
                    # Modified by Sheng Liao on 2021/12/01 -------------
                    # mc.lockNode(r,lock=True)
                    mc.lockNode(r, lock=False)
                    # ------------- Modified by Sheng Liao on 2021/12/01
            else:
                return "no anim_skeletions_grp to perform reorder!"

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

