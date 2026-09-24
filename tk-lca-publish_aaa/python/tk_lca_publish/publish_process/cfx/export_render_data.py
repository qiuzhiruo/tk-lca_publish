# -*- coding:utf-8 -*-
__author__ = 'huangxin'

import os
import json
import traceback
import production.python_job as ppj
import production.pipeline.utils as pplu
from production.farm_ip import LcaFarmIPManage
from render.muster_functions.muster_user_data_utils import getUserFullFromDB
import production.pipeline.permission_control as ppc

import pymel.core as pm
import maya.cmds as cmds


PYTHON_SCRIPT_ROOT=os.getenv('LC_TOOLSET')
FARMTEMPLATE_ID = LcaFarmIPManage().MASTERCACHE

EXPORT_CMD = '-frameRange 1 1 -uvWrite -worldSpace -dataFormat ogawa -file %s -root %s'

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提交预渲染导出渲染信息"
        self.description = u"提交预渲染任务到farm上, 从log里获取信息更新到shotgun上"

    def send_srf_render(self, proj, asset_name, asset_type):
        PYTHON_SCRIPT_ROOT = os.getenv('LC_TOOLSET')
        # PYTHON_SCRIPT_ROOT = '/mnt/work/shome/taka/git_repo/lcatools'

        send_script = PYTHON_SCRIPT_ROOT + "/tools/srf/turntable_muster/external_call_render_srf.py"
        katana_exc = pplu.get_dcc_launcher(proj=proj, dcc='katana')

        userdata = getUserFullFromDB()
        username = userdata["full_name"]
        department = userdata["department"]

        args = ' '.join([proj, asset_name, asset_type, username, department])
        send_id = ppj.send_job('--script='+send_script,
                                args=args,
                                proj=proj.upper(),
                                job_name_prefix='[CFX Send Srf Render] %s' % (asset_name),
                                step='CFX',
                                user=self.dialog.user_name,
                                pools='centos7',
                                url='10.0.0.214',
                                priority=3000,
                                python_exe=katana_exc,
                               submitdl=True)
        self.dialog.print_log('send srf render: ' + str(send_id))
    
    def proceed(self):

        if 'hair' not in self.dialog.task['name']:
            return ''

        proj = self.dialog.project['name'].lower()
        asset_name = self.dialog.entity['name']
        asset_type = self.dialog.asset_type

        try:
            if os.path.isdir(self.dialog.version_dir):
                version_tag = os.path.basename(self.dialog.version_dir)
                user = self.dialog.user_name

                # 提交srf渲染任务到output盘
                if self.dialog.w_publish_file.cb_render_srf.isChecked():
                    self.send_srf_render(proj, asset_name, asset_type)

                # export camera
                import cfx.lcaCFXTurntable.create_cam as create_cam
                body_cam, head_cam = create_cam.get_cam(asset_type, asset_name, False)
                cam_path = os.path.join(self.dialog.work_root, 'camera')
                head_abc = os.path.join(cam_path, 'head_cam.abc')
                body_abc = os.path.join(cam_path, 'body_cam.abc')
                if not os.path.isdir(cam_path):
                    os.mkdir(cam_path, 0777)
                pc = ppc.PermissionControl(os.path.dirname(cam_path))
                pc.change_mod_permission(777)

                cmds.AbcExport(j=EXPORT_CMD%(head_abc, head_cam.longName()))
                cmds.AbcExport(j=EXPORT_CMD%(body_abc, body_cam.longName()))

                send_job_py = PYTHON_SCRIPT_ROOT+'/tools/cfx/katana_prerender/set_prerender_info.py'
                job_id = ppj.send_job('--script='+send_job_py,
                    args=' '+' '.join([proj, asset_name, version_tag, user]),
                    proj=proj.upper(),
                    job_name_prefix='[Send Asset Prerender]'+version_tag+' by '+user,
                    step='CFX',
                    user=user,
                    url=FARMTEMPLATE_ID,
                    submitdl=True,
                    python_exe=pplu.get_dcc_launcher(proj=proj, dcc='katana')
                )
                if job_id == -1:
                    print 'Farm submit error: ', version_tag
                else:
                    print 'Send builf asset Job: ', job_id
                
                return ''
            else:
                return 'The publish version not exists: '+self.dialog.version_dir
            
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

