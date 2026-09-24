# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

import sys
# sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-2]) + '/proc' )
#import tk_lca_publish.proc.check_reference_hierarchy as crh # 由于导入模块出错，直接在文件中加入函数

def check_hire():
    # reference in group that is under another reference is illegal
    ref_nodes = pm.ls('*:master', rn=True, long=True)
    find_illegal_ref = []
    for ref in ref_nodes:
        for ref2 in ref_nodes:
            if ref.isParentOf(ref2):
                find_illegal_ref.append(ref)
                find_illegal_ref.append(ref2)
                break
        if find_illegal_ref:
            break
    if find_illegal_ref:
        return u"非法的reference层级: "+find_illegal_ref[1]+u"在"+find_illegal_ref[0]+u"层级下。reference之间不能互为父子层级。"
        # why? because we move object by rig, not by transform of shapes directly, simple grouping rule simply doesn't apply to our system
    else:
        return None

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产组装层级命名。"
        self.description = u"组装资产最上层组为master；master 下只有rra组，rig组 或者 world_PC 节点。reference之间不能互为父子层级。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            if not pm.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            if not pm.objExists("|master|rra"):
                return u"没有找到次高层的 |master|rra 组。"

            for n in pm.listRelatives('|master', c=True):
                if not n.nodeName() in ['rra', 'rig', 'world_PC']:
                    return u"master 下只能有 rra组，rig组 或者 world_PC 节点。"

            # reference之间不能互为父子层级
            #ref_check = crh.check()
            #if ref_check:
            #    return ref_check

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


