# -*- coding:utf-8 -*-

import os
import  sys
import re
import pymel.core as pm
import maya.cmds as cmds
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查关系资产"
        self.description = u"检查父子资产是否是最新"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        self.asset_name = os.path.basename(pm.sceneName()).split('.')[0]
        self.asset_info = self.get_asset_relation_info(self.asset_name)

        self.is_auto_fix = True
        self.confirm_update = True
        self.error_sub_assets = []
        self.publish_wait = False
        # 不允许同时存在父资产和子资产
        if self.asset_info['asset_sg_mod_parent_assets_assets'] and self.asset_info['sg_mod_parent_assets']:
            self.is_auto_fix = False
            return u'当前资产{}同时拥有父资产和子资产，这是错误的，需要联系制片修改。'.format(self.asset_name)

        result = self.run_fix()
        # 如果存在子资产
        if self.asset_info['asset_sg_mod_parent_assets_assets']:
            # 在pa父资产的时候不允许修改子资产，反之亦然
            if result:
                return result
            self.error_sub_assets = []

            # if 'publishing_automatically' in self.asset_info['tag_list']:
            #     self.publish_wait = True
            #     return u'资产更新中，请稍后再尝试.'

            # 子资产也不能同时拥有父资产和子资产
            for sub_asset_info in self.asset_info['asset_sg_mod_parent_assets_assets']:
                self.sub_relation_info = self.get_asset_relation_info(sub_asset_info['name'])
                if self.sub_relation_info['asset_sg_mod_parent_assets_assets'] and self.sub_relation_info['sg_mod_parent_assets']:
                    self.error_sub_assets.append(sub_asset_info['name'])
            if self.error_sub_assets:
                return u'这些子资产{}同时拥有父资产和子资产，这是错误的，需要联系制片修改。'.format('\n'.join(self.error_sub_assets))

            current_sub_assets = [a.name().split('|')[-1].replace('_at', '') for a in pm.listRelatives('|master|poly|hi|mesh_grp|attach_grp|sub_asset')]

            if not current_sub_assets:
                return u'当前资产在sg上标记有子资产，但当前场景中没有导入'
            sg_sub_assets = [sub_info['name'] for sub_info in self.asset_info['asset_sg_mod_parent_assets_assets']]
            print(current_sub_assets, '===============================', sg_sub_assets)
            if list(set(sg_sub_assets) - set(current_sub_assets)):
                return u"当前场景中子资产与sg上不匹配{}".format(list(set(sg_sub_assets) - set(current_sub_assets)))

        # 存在父资产
        if self.asset_info['sg_mod_parent_assets']:
            all_parents = [parent['name'] for parent in self.asset_info['sg_mod_parent_assets']]
            # 查找没有pa版本的父资产
            error_p = []
            for p_name in all_parents:
                asset =  self.dialog.sg.find_one('Asset', [['code', 'is', p_name]], ['sg_asset_type'])

                model_task =  self.dialog.sg.find_one('Task', [['entity', 'is', asset], ['content', 'is', 'Model']])

                versions =  self.dialog.sg.find(
                                            "Version",
                                            [
                                                ["entity", "is", asset],
                                                ["sg_task", "is", model_task]
                                            ],
                                            ["id", "code"]
                                         )

                if not versions:
                    error_p.append(p_name)

            if error_p:
                return u'下面这些父资产没有pa版本，请先pa了父资产，或者找制片去除这些父资产:\n{}'.format('\n'.join(error_p))

            msg = u'更新当前模型版本会导致其以下所有父资产更新版本。\n{}\n' \
                  u'           是否仍然更新？'.format('\n'.join(all_parents))
            result = pm.confirmDialog( title=u"注意！！！" , message=msg, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if result == 'No':
                self.confirm_update = False
                return u'已中断当前资产发布'
        l_script_nodes = []
        for n in pm.ls(type='script'):
            if n.name() != 'sceneConfigurationScriptNode':
                l_script_nodes.append(n.name())
        if len(l_script_nodes) > 0:
            pm.delete(l_script_nodes)
        return ''

    def get_latest_version(self, publish_dir, task_name=''):

        if os.path.exists(publish_dir):
            version_num = []
            for sub_file in os.listdir(publish_dir):
                if task_name in sub_file:
                    match = re.search(r'v(\d+)', sub_file)
                    if match:
                        version_num.append(int(match.group(1)))
            if version_num:
                return int(max(version_num))
        return


    def get_asset_relation_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['asset_sg_mod_parent_assets_assets', 'sg_mod_parent_assets', 'tag_list'])
        return asset_info

    def run_fix(self):
        '''Auto Fix'''
        # 强调提醒无法通过自动修复进行修复，只能找制片
        if not self.is_auto_fix:
            return u'当前资产{}同时拥有父资产和子资产，这是错误的，需要联系制片修改。'.format(self.asset_name)
        if self.error_sub_assets:
            return u'这些子资产{}同时拥有父资产和子资产，这是错误的，需要联系制片修改。'.format('\n'.join(self.error_sub_assets))
        if not self.confirm_update:
            return u'已中断当前资产发布'

        if self.publish_wait:
            return u'资产更新中，请稍后再尝试.'

        if sys.platform.startswith('win'):
            path_root = 'Z:/projects'
        else:
            path_root = '/mnt/proj/projects'
        proj_name = self.dialog.project['name'].lower()
        if not pm.objExists('|master|poly|hi|mesh_grp|attach_grp'):
            pm.group(name='attach_grp', empty=True, parent='|master|poly|hi|mesh_grp')

        if not pm.objExists('|master|poly|hi|mesh_grp|attach_grp|sub_asset'):
            pm.group(name='sub_asset', empty=True, parent='|master|poly|hi|mesh_grp|attach_grp')

        for c_sub in pm.listRelatives('|master|poly|hi|mesh_grp|attach_grp|sub_asset', f=True):
            pm.delete(c_sub)
        if self.asset_info['asset_sg_mod_parent_assets_assets']:

            for sub_asset_info in self.asset_info['asset_sg_mod_parent_assets_assets']:
                flt = [['project', 'name_is', proj_name.upper()], ['code', 'is', sub_asset_info['name']]]
                sub_asset_type = self.dialog.sg.find_one('Asset', flt, ['sg_asset_type'])['sg_asset_type']
                sub_version_path = os.path.join(path_root, proj_name, 'asset', sub_asset_type, sub_asset_info['name'], 'mod', 'publish', sub_asset_info['name'] + '.mod.model', sub_asset_info['name']+'.ma')
                pub_version_path = os.path.join(path_root, proj_name, 'asset', sub_asset_type, sub_asset_info['name'], 'mod', 'publish')
                pm.importFile(sub_version_path, returnNewNodes=True)
                sub_mesh_grp = '|' + sub_asset_info['name'] + '_master' + '|poly|hi|mesh_grp'
                new_grp = pm.rename(sub_mesh_grp, '|' + sub_asset_info['name'] + '|poly|hi|' + sub_asset_info['name'])
                pm.parent(new_grp, '|master|poly|hi|mesh_grp|attach_grp|sub_asset')
                for i in pm.listRelatives('|' + sub_asset_info['name'] + '_master', ad=1, f=1):
                    pm.lockNode(i, lock=False)
                pm.delete('|' + sub_asset_info['name'] + '_master')
                asset_grp = pm.ls('|master|poly|hi|mesh_grp|attach_grp|sub_asset|' + sub_asset_info['name'])[0]
                if not asset_grp.hasAttr('sub_version'):
                    asset_grp.addAttr('sub_version', dt='string')
                version_n = self.get_latest_version(pub_version_path, 'model')
                asset_grp.sub_version.set(str(version_n))

                for sub_node in pm.listRelatives('|master|poly|hi|mesh_grp|attach_grp|sub_asset|', ad=True, typ='transform'):
                    sub_node.rename(sub_node.name()+'_at')
        else:
            pm.delete('|master|poly|hi|mesh_grp|attach_grp|sub_asset')
            if not pm.listRelatives('|master|poly|hi|mesh_grp|attach_grp'):
                pm.delete('|master|poly|hi|mesh_grp|attach_grp')

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


