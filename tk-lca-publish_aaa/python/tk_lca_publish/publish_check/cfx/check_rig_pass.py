# -*- coding: utf-8 -*-
'''
    @Date: 2024.06.06--8:02 PM
    Descriptions:
        
'''
__author__ = 'huangsheng'

import traceback
import re
from cfx.cfx_hair_pass import maya_utils as chpu
reload(chpu)
from production.pipeline import lcProdProj as lpp
reload(lpp)

# All system check classes will use StdCheck as the class name.
class StdCheck(object):
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查当前资产上游是否有RigPass"
        self.description = u"如果上游(Rig)有RigPass信息，则检查Collection是否有RigPass属性并且不为空。请注意：不能判定RigPass属性的正确性"
        self.duty = u"艺术家本人"
        self.auto_fix = False
        return

    def run_check(self):
        try:
            lc_proj = lpp.lcProdProj()
            lc_proj.setProj(self.dialog.project['name'])
            pass_info = lc_proj.rig_pass(self.dialog.entity['name'])
            if not pass_info:
                return ""
            pass_info = pass_info['pass_info']
            if not pass_info:
                return ""
            pass_state = pass_info['rig_pass_state']
            if not pass_state:
                return ""
            import xgenm as xg
            import maya.cmds as cmds
            if not xg.palettes():
                return ""
            msg = ""
            for pal in xg.palettes():
                if not cmds.objExists(chpu.node_pass_attr(pal)) or not cmds.getAttr(chpu.node_pass_attr(pal)):
                    msg += u"当前资产上游有RigPass信息，请检查Collection: %s 与RigPass信息是否对应\n" % pal
            return msg
        except:
            return traceback.format_exc()
        return ""

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


