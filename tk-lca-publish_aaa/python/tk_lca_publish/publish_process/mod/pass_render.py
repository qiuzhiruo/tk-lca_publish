# -*- coding:utf-8 -*-
import traceback
import sys
# TOOL_ROOT = '/mnt/utility/'
# sys.path.append(TOOL_ROOT + '/toolset/lib/production')
import os
import getpass
from production.shotgun_connection import Connection
from proc.function_running_time import record_time
sg = Connection('get_shot_info').get_sg()
import maya.cmds as mc
import pymel.core as pm
import production.python_job as python_job
from production.farm_ip import LcaFarmIPManage


def unlock_visibility_for_groups(group_paths):
    for grp_path in group_paths:
        if not pm.objExists(grp_path):
            continue

        grp = pm.PyNode(grp_path)
        children = grp.getChildren(type='transform')

        if not children:
            continue

        for child in children:
            attr_name = "{}.visibility".format(child.name())
            if pm.objExists(attr_name):
                if pm.getAttr(attr_name, lock=True):
                    pm.setAttr(attr_name, lock=False)


class StdProcess():
    def __init__(self,dialog):
        self.dialog = dialog
        self.process_name = u'三级角色渲染pass'
        self.description = u'有pass 的三级角色渲染pass'
        return

    @record_time(__file__)
    def proceed(self):
        try:

            asset_name = self.dialog.d_assets_info.keys()[0]
            proj_name = self.dialog.project['name'].upper()
            asset_name = self.dialog.entity.get('name')
            asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()],
                                                           ['code', 'is', asset_name]],
                                                 ['sg_diffculty2', 'sg_asset_type'])
            # 目前 变脸只在xun项目
            if self.dialog.project['name'].lower() in ['lic']:
                return ''

            # check if chr:
            if str(asset_info.get('sg_diffculty2')) not in ['3'] or asset_info.get('sg_asset_type') != 'chr':
                return ''
            if not mc.objExists('|master|shape|face_pass_grp'):
                return ''

            # if not mc.objExists('|master|shape|face_pass_grp') and not mc.objExists('|master|poly|hi|mesh_grp|cloth_grp'):
            #     return ''

            # del proxy
            if mc.objExists('|master|poly|proxy'):
                mc.delete('|master|poly|proxy')
            if mc.objExists('|master|shape|to_rig'):
                mc.setAttr('|master|shape|to_rig.visibility', 0)
            if mc.objExists('|master|shape|to_lay'):
                mc.setAttr('|master|shape|to_lay.visibility', 0)
            # unlock visibility
            groups = [
                "|master|shape|face_pass_grp",
                "|master|poly|hi|mesh_grp|cloth_grp",
                "|master|shape|to_cfx|hair_grp|head_hair"
            ]
            unlock_visibility_for_groups(groups)

            pm.setAttr('body_geo.visibility', lock=False)
            maya_file = pm.sceneName().replace('\\', '/')

            pass_preview_path = os.path.join(os.path.dirname(maya_file), 'pass_preview')
            if not os.path.exists(pass_preview_path):
                os.makedirs(pass_preview_path, 0777)
            pass_render_ma = os.path.join(pass_preview_path, os.path.basename(maya_file))
            pm.saveAs(pass_render_ma, f=True)

            # ------------------------------
            user = getpass.getuser()
            mayapy = '/mnt/utility/linked_tools/lca_rez/launchers/lic/linux/mayapy'
            # com_pub_py_host = '/mnt/work/shome/liangyue/package/lcatools/tools/mod/mod_pass_render/pass_combine_pub_host.py'
            com_pub_py_host = '/mnt/utility/linked_tools/lcatools/tools/mod/mod_pass_render/pass_combine_pub_host.py'
            # 把路径转成linux
            pass_render_ma_l =pass_render_ma.replace('\\', '/').replace('W:/', '/mnt/work/')
            job_id = python_job.send_job(com_pub_py_host,
                                         proj=str(proj_name.upper()),
                                         url=str(LcaFarmIPManage().MASTERCACHE),
                                         args='{} {} {}'.format(proj_name, asset_name, pass_render_ma_l),
                                         user=user,
                                         python_exe=str(mayapy),
                                         pools='common',
                                         priority=10000,
                                         msg='{} mod pass combine and pub'.format(asset_name),
                                         job_name_prefix='[{} MOD Pass Job]'.format(asset_name),
                                         submitdl=True)
            print('----jobid:', job_id)

            mc.file(newFile=True, force=True)
            return ''

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
