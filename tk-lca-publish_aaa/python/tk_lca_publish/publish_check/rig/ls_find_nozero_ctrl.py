# -*- coding:utf-8 -*-

#import os
# import imp
# package_directory = os.path.normpath(os.path.join(os.path.dirname(__file__), "../.."))
# imp.load_source("publishRigCmd", "%s/publishRigCmd.py" % package_directory)
# from publishRigCmd import *    # if you need just this, "import helper" is not required

import traceback
import assetsystem_sgl.tools.common.publish.ls_nurbsCurve_ctrl as ls_nurbsCurve_ctrl
import maya.cmds as mc
reload(ls_nurbsCurve_ctrl)
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查没归零的控制器'
        self.description = u'检查没归零的控制器'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            ununique_name_nodes = ls_nurbsCurve_ctrl.ls_find_noZero_ctrl_cmd()
            # 添加一个筛选，如果变脸面板存在，移除列表中的控制器
            if mc.objExists("root_revies_def") or mc.objExists("root_revies_ctrl"):
                remove_ctrl_list = ["brow_L_all_sec_ctrl", "brow_R_all_sec_ctrl", "chin_M_1_sec_ctrl", "brow_L_1_sec_ctrl", "brow_L_2_sec_ctrl", "brow_L_3_sec_ctrl", "brow_R_1_sec_ctrl", "brow_R_2_sec_ctrl", "brow_R_3_sec_ctrl"]
                if ununique_name_nodes:
                    for each in ununique_name_nodes:
                        if each in remove_ctrl_list:
                            ununique_name_nodes.remove(each)

            if ununique_name_nodes:
                msg = u'有没归零的控制器\n'+"\n".join(ununique_name_nodes)
                return msg
            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix gentest'''
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


