# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset geometry hierarchy
#
############################################

import traceback
import maya.cmds as cmds
import os
import re

# All system check classes will use StdCheck as the class name.
from assetsystem_sgl.tools.common.publish.ls_nurbsCurve_ctrl import check_wrong_name_pri_and_sec


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产层级命名。"
        self.description = u"资产最上层组为master,其次为rig,poly, hi/lo组。lo组必须有。如果是layout rig任务，只有lo组"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            import pymel.core as pm
            if not cmds.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            if not cmds.objExists("|master|poly"):
                return u"没有找到次高层的 |master|poly 组。"

            if not cmds.objExists("|master|rig"):
                return u"没有找到次高层的 |master|rig 组。"

            if not cmds.objExists("|master|rig|anim_rig"):
                return u"没有找到次高层的 |master|rig|anim_rig 组。"

            if not cmds.objExists("|master|poly|hi"):
                return u"没有找到次高层的 |master|poly|hi 组。"

            if not cmds.objExists("|master|poly|proxy"):
                return u"没有找到次高层的 |master|poly|proxy 组。"

            # if cmds.objExists("anim_guides_grp"):
            #     return u"anim_guides_grp 组必须被删除。"

            #check hirarchy under the master group
            cs=cmds.listRelatives('|master',c=1,pa=1)
            if cs:
                grps=['poly','shape','rig', 'misc']
                for grp in grps:
                    if grp in cs:
                        cs.remove(grp)
                if not (cs==None or cs==[]):
                    return u"|master 层级下不能有多余的组,只能有['poly','shape','rig', 'misc']"

            cs=cmds.listRelatives('|master|rig',c=1,pa=1)
            if cs:
                grps=['anim_rig','tech_rig']
                for grp in grps:
                    if grp in cs:
                        cs.remove(grp)
                if not (cs==None or cs==[]):
                    return u"|master|rig 层级下不能有多余的组,只能有['anim_rig','tech_rig']"  

            cs=cmds.listRelatives('|master|rig|anim_rig',c=1,pa=1)
            if cs:
                grps=['anim_controls_grp','anim_skeletons_grp','anim_modules_grp']
                for grp in grps:
                    if grp in cs:
                        cs.remove(grp)
                if not (cs==None or cs==[]):
                    return u"|master|rig|anim_rig 层级下不能有多余的组,只能有['anim_controls_grp','anim_skeletons_grp','anim_modules_grp']"

            if cmds.objExists('|master|rig|tech_rig'):
                cs=cmds.listRelatives('|master|rig|tech_rig',c=1,pa=1)
                if cs:
                    grps=['tech_controls_grp','tech_skeletons_grp','tech_modules_grp']
                    for grp in grps:
                        if grp in cs:
                            cs.remove(grp)
                    if not (cs==None or cs==[]):
                        return u"|master|rig|tech_rig 层级下不能有多余的组,只能有['tech_controls_grp','tech_skeletons_grp','tech_modules_grp']"

            # if self.dialog.task['name'].startswith('layout_rig'):
                # if cmds.objExists("|master|poly|hi"):
                    # return u"如果是layout rig任务,没有hi组,只有lo组"

            #if not pm.objExists("|master|poly|lo"):
            #    return u"没有找到低模 |master|poly|lo 组。"

            n = cmds.ls('visibility_ctrl')
            if not n:
                return u"没有找到 visibility_ctrl 控制器。"

            visattrlist=['mesh_display_type','proxy_vis','facial_panel','char_name','tech_rig_vis','anim_rig_vis']
            for vattr in visattrlist:
                if not cmds.objExists('visibility_ctrl.'+vattr):
                    return u"visibility_ctrl 控制器不是系统生成的，请删除并用系统生成一个新的。"


            check_pri_sec_grp = check_wrong_name_pri_and_sec()

            return ",".join(check_pri_sec_grp)
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


