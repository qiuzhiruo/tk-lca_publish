# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
############################################

import getpass
import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"asb 资产第一个 Downstream 版本，需要组长检查"
        self.description = u"asb 资产第一个 Downstream 版本，需要组长检查组级布局。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):

        try:
            
            self.dialog.mod_asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type','tag_list'])
            if self.dialog.mod_asset['sg_asset_type'] in ['chr', 'crd', 'msc', 'efx', 'scn']:
                return ""

            if not (self.dialog.task['name'] == 'model' or self.dialog.task['name'].startswith('assembly')):
                return ""

            if self.dialog.mod_asset['sg_asset_type'] in ['prp', 'env', 'veh', 'flg']:
                if self.dialog.version_tag == u"粗模":
                    return ""
                else:
                    l_versions = self.dialog.sg.find('Version', [['sg_task', 'is', self.dialog.task], ['sg_version_type', 'is', 'Downstream'], ['tag_list', 'is', u'精模']], [])
            else:
                if self.dialog.task['name'].startswith('assembly') and self.dialog.version_tag == u"粗模":
                    return ""
                l_versions = self.dialog.sg.find('Version', [['sg_task', 'is', self.dialog.task], ['sg_version_type', 'is', 'Downstream']], [])

            if len(l_versions) > 0:
                return ""

            # Is ther a TD check mark?
            if pm.objExists('td_name_check'):
                n = pm.PyNode('td_name_check')
                if n.hasAttr('asset') and n.getAttr('asset') == self.dialog.entity['name']:
                    return ""
            if 'skip_asb_lead_check' in self.dialog.mod_asset['tag_list']:
                return ""
            return u"asb 资产的第一个精模 Downstream 版本，需要组长检查组级布局 主要是为了检查模型层级布局。\n 请保存当前文件，并通知组长。\n组长检查完命名后使用 LCA MOD > Check > Lead Name Check 给当前文件打上通过的记号。\n模型师重开文件后可以 Publish。"

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            
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



