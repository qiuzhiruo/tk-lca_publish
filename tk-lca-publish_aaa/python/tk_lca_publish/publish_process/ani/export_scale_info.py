# -*- coding: UTF-8 -*-
# @Time:2023/10/13 下午4:48
# @Author:yulu
import getpass
import os
import sys
import json
import traceback

import pymel.core as pm


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u'导出角色缩放信息'
        self.description = u'导出角色缩放信息,判断是否使用毛发缩放流程'
        return

    def proceed(self):
        try:
            if sys.platform.startswith('lin'):
                import production.python_job as python_job
            else:
                import production.python_job_win as python_job
            refs = self.get_all_chr_namespace()
            if not refs:
                self.dialog.print_log("no asset reference")
                return ''
            import ani.lca_export_scale_info as esi
            script_file = '{}/tools/ani/lca_export_scale_info/export_scale_json_script.py'.format(os.getenv('LC_TOOLSET'))
            # script_file = '/mnt/work/home/yulu/git_debug/lcatools/tools/ani/lca_export_scale_info/export_scale_json_script.py'
            proj = self.dialog.project['name']
            shot = self.dialog.entity['name']
            python_exe = '{}/launchers/{}/linux/mayapy'.format(os.getenv('LCA_REZ'), proj.lower())
            from production.farm_ip import LcaFarmIPManage
            if self.dialog.step['name'] == 'ani':
                ma_file = self.dialog.publish_ma.replace('\\', '/')
                job_name_prefix = '[SCALE INFO {0} by {1}]{2}'.format(shot, getpass.getuser(), ma_file.split('/')[-2])
                python_job.send_job(script_file, proj=proj, priority=2000, step='ANI', python_exe=python_exe,
                                    job_name_prefix=job_name_prefix, url=LcaFarmIPManage().MASTERCACHE,
                                    args='"' + ma_file + '"', msg=None)
            if self.dialog.step['name'] == 'flo':
                ma_file = self.dialog.tank_file.replace('\\', '/')
                job_name_prefix = '[SCALE INFO {0} by {1}]{2}'.format(shot, getpass.getuser(), ma_file.split('/')[-2])
                python_job.send_job(script_file, proj=proj, priority=2000, step='ANI', python_exe=python_exe,
                                    job_name_prefix=job_name_prefix, url=LcaFarmIPManage().MASTERCACHE,
                                    args='"' + ma_file + '"' + ' ' + '0', msg=None)
            return ''
        except:
            return traceback.format_exc()

    def get_all_chr_namespace(self):

        refs = pm.ls(type='reference')
        namespces = []
        for ref in refs:
            file_ref = ref.referenceFile()
            # chr\prp
            if not file_ref:
                continue
            ns = ref.associatedNamespace(ref.name())
            if ns:
                namespces.append(ns)
        return namespces

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
