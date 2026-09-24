# -*- coding:utf-8 -*-

import traceback

import os
import re
import json
import pymel.core as pm
import maya.cmds as mc

import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-2]) + '/proc' )
import check_reference_hierarchy as crh

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产组装层级命名。"
        self.description = u"组装资产最上层组为master；master 下只有asb组，rig组 或者 world_PC 节点。reference之间不能互为父子层级。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            if not pm.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            if not pm.objExists("|master|asb"):
                return u"没有找到次高层的 |master|asb 组。"

            for n in pm.listRelatives('|master', c=True):
                if not n.nodeName() in ['asb', 'rig', 'world_PC', 'proxy']:
                    return u"master 下只能有 asb组，rig组 或者 proxy组 或者world_PC 节点。"
            l_bad_plt=[]
            if pm.objExists('|master|asb|plt_proxy_grp'):
                for ar in pm.listRelatives('|master|asb|plt_proxy_grp',c=1,ad=True,type='assemblyReference'):
                    path = str(ar.getAttr("definition")).replace('\\', '/')
                    if 'flg' not in path.split('/'):
                        l_bad_plt.append(ar.name())

            mod_asb_setting_file = os.path.join(os.path.dirname(__file__), 'mod_check_preset.json')
            with open(mod_asb_setting_file, 'r') as f:
                mod_asb_setting = json.loads(f.read())

            l_error_plt = []
            scene_asset = str(pm.sceneName().basename()).split('.')[0]

            if scene_asset not in mod_asb_setting['skip_check_flag_hierarchy']:
                for ar_node in pm.listRelatives('|master|asb', c=1, ad=True, type='assemblyReference'):
                    full_path = ar_node.fullPath()
                    ar_path = str(ar_node.getAttr("definition")).replace('\\', '/')
                    if 'flg' in ar_path.split('/') and '|master|asb|plt_proxy_grp' not in full_path:
                        l_error_plt.append(full_path)

            # reference之间不能互为父子层级
            ref_check = crh.check()

            if l_bad_plt:
                return u'|master|asb|plt_proxy_grp组下有非flg类型的资产:'+' , '.join(str(s) for s in l_bad_plt)
            if l_error_plt:
                pm.select(l_error_plt)
                return u'|master|asb|plt_proxy_grp组外有flg类型的资产:\n{}'.format('\n'.join(l_error_plt))

            if ref_check:
                return ref_check
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


