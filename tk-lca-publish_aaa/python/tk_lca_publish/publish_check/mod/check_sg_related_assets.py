# -*- coding:utf-8 -*-

import traceback
import pymel.core as pm
import maya.cmds as cmds
import glob
import getpass
import subprocess
import platform
import shutil
from proc.function_running_time import record_time
from PySide2.QtWidgets import QInputDialog
from production.shotgun_connection import Connection
sg = Connection('get_shot_info').get_sg()

class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查关联资产。"
        self.description = u"当前资产有相关资产，请选择要publish的资产。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_related_assets(self,asset_name):
        related_assets = sg.find_one('Asset',[['code','is',asset_name]],['asset_sg_mod_parent_assets_assets'])['asset_sg_mod_parent_assets_assets']
        if not related_assets:
            return ''
        else:
            related_assets_name_lst = []
            for assets in related_assets:
                related_assets_name_lst.append(assets['name'])
            return related_assets_name_lst

    def open_related_assets(self,proj,asset_name):

        try:
            cmds.file(save=True, force=True)
        except:
            print traceback.format_exc()
        orig_path = pm.sceneName()
        if platform.system().lower() == 'windows':
            work_path = 'W:/projects/%s/asset/chr/%s/mod/task/maya/'%(proj,asset_name)
        elif platform.system().lower() == 'linux':
            work_path = '/mnt/work/projects/%s/asset/chr/%s/mod/task/maya/'%(proj,asset_name)
        lst = glob.glob(work_path+asset_name+'.mod.model.*.ma')
        lst.sort()
        version_num = int((lst[-1].rsplit('.',2)[-2]).split('v')[-1])+1
        new_file_path = work_path+asset_name+'.mod.model.v{:0>3d}.ma'.format(version_num)
        shutil.copyfile(orig_path,new_file_path)
        p = subprocess.Popen('maya -file '+new_file_path)
        return ''

    @record_time(__file__)
    def run_check(self):
        if getpass.getuser() != 'aokang':
            return ''
        if self.dialog.d_assets_info[self.dialog.entity['name']]['type'] != 'chr':
            return ''
        related_assets = self.get_related_assets(self.dialog.entity['name'])
        if related_assets:
            related_assets.insert(0,u'<请选择>')
            if related_assets:
                asset,ok = QInputDialog.getItem(self.dialog,u'相关资产选择',u'当前资产有相关资产，请选择要publish的资产，若不pu请点击取消，记得不要忘了继续publish当前资产',related_assets,0,True)
                if ok and asset!=u'<请选择>':
                    self.open_related_assets(self.dialog.project['name'].lower(), asset)
                    return ''

        return ''

    def run_fix(self):
        '''Auto Fix'''

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


