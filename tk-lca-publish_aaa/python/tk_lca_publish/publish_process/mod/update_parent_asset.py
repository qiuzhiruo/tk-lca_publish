# -*- coding:utf-8 -*-
import sys
import os
import getpass

import pymel.core as pm
import traceback

from mod.mod_batch_publish import submit_mod_publish_job
from proc.function_running_time import record_time


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"更新父资产"
        self.description = u"如果子资产更新了，那么所关联的所有父资产都要重新拉取一遍子资产进行更新。父子产更新是有延迟的"
        return

    # 删除大环
    def remove_global_ctrl(self):
        self.rig_node = pm.PyNode(u'rig')
        # Delete Rig
        l_rig_nodes = pm.listRelatives(self.rig_node, ad=True)
        for n in l_rig_nodes:
            pm.lockNode(n, l=False)
        pm.delete(self.rig_node)

        if not pm.objExists('|master|poly|hi'):
            pm.createNode('transform', parent='|master|poly', name='hi')

        # Rebuild the master, poly group
        for node_name in ['|master', '|master|poly']:
            node = pm.ls(node_name)[0]
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                node.setAttr(attr, lock=0, keyable=1 )

        n = pm.PyNode('|master|poly')
        n.setAttr("inheritsTransform", 1)
        return

    @record_time(__file__)
    def proceed(self):
        # 更新父子产，要采用模型外包的方式，提交到dlm上自动更新，无论任务级别再高，子资产更新后父资产都不一定能及时更新
        # 如果只更新了子资产，那么父资产pa版本，父资产的材质，绑定都是要跟一下的
        # 发角色的turntable cam 直接调用最新版本对应的work盘文件（work盘文件的版本号与proj盘一致）
        self.asset_name = os.path.basename(pm.sceneName()).split('.')[0]
        self.asset_info = self.get_asset_relation_info(self.asset_name)
        if self.asset_info['sg_mod_parent_assets']:
            for p_info in self.asset_info['sg_mod_parent_assets']:
                p_name = p_info['name']
                latest_version, asset_type = self.get_latest_version_and_type(p_name)

                if not latest_version:
                    # 父资产还未发布版本， 应该写个检查项卡父资产没有版本的，子资产不让发？ 还是直接跳过？？？
                    continue
                # 由于work版本proj版本是对应的可找到work版本
                proj_root = 'Z:/projects'
                if sys.platform.startswith('linux'):
                    proj_root = '/mnt/proj/projects'
                proj_ma = os.path.join(proj_root, self.dialog.project['name'].lower(), 'asset', asset_type, p_name, 'mod/publish', latest_version['code'], p_name+'.ma')
                preview = latest_version['sg_path_to_movie'].replace('${RV_PATHSWAP_ROOT}', '/mnt/proj')
                image = latest_version['image']
                user = getpass.getuser()
                submit_mod_publish_job.submit_mod_auto_pub_job(self.dialog.project['name'].lower(), proj_ma, preview, user=user)

        return ''

    def get_latest_version_and_type(self, asset_name):
        asset = self.dialog.sg.find_one('Asset', [['code', 'is', asset_name], ['project', 'is', self.dialog.project]], ['sg_asset_type'])
        model_task = self.dialog.sg.find_one('Task', [['entity', 'is', asset], ['content', 'is', 'Model']])
        latest_version = self.dialog.sg.find_one(
                                                    "Version",
                                                    [
                                                        ["entity", "is", asset],
                                                        ["sg_task", "is", model_task]
                                                    ],
                                                    ["id", "code", "created_at", "description", "sg_path_to_movie", "user", "image"],
                                                    [{"field_name": "created_at", "direction": "desc"}]
                                                 )

        return latest_version, asset['sg_asset_type']

    def get_asset_relation_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['asset_sg_mod_parent_assets_assets', 'sg_mod_parent_assets'])
        return asset_info

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
