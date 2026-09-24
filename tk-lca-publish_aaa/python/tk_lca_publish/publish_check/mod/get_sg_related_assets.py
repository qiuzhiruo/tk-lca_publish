# -*- coding:utf-8 -*-

import pymel.core as pm
import sys,glob,subprocess,platform,shutil,traceback
from production.shotgun_connection import Connection
sg = Connection('get_shot_info').get_sg()

class check_related_assets():
    '''just for publish_dialog, not for publish check'''

    def __init__(self):
        self.check_name = u"检查当前资产是否有相关资产"
        self.description = u"检查当前资产是否有相关资产，若有打开相关资产的文件。"
        return

    def get_related_assets(self,asset_name):
        related_assets = sg.find_one('Asset',[['code','is',asset_name]],['sg_related_assets'])['sg_related_assets']
        if not related_assets:
            return ''
        else:
            related_assets_name_lst = []
            for assets in related_assets:
                related_assets_name_lst.append(assets['name'])
            return related_assets_name_lst

    def open_related_assets(self,proj,asset_name):
        import maya.cmds as cmds
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


    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description


