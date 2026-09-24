# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.11
#
# Description: 
#
############################################

import os
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将最新的UV推送到已经Publish的Rig/Mod Publish文件上"
        self.description = u"将最新的UV推送到已经Publish的Rig/Mod Publish文件上。"
        return


    def proceed(self):
        if int(self.dialog.w_publish_file.checkBox.isChecked()):
            self.push_uv_master()
            
        try:
            # Send a singal to push uv
            
            server = self.dialog.version_dir.split('projects')[0]
            linux_version_dir = self.dialog.version_dir.replace(server, '/mnt/proj/')
            v_file = server + 'trash/srf_versions/' + self.dialog.version_name + '.txt'
            f = open(v_file, 'w')
            f.write(linux_version_dir)
            f.close()

            os.system('chmod 777 '+v_file)
            return ''

        except:
            return traceback.format_exc()

    def push_uv_master(self):
        import production.pipeline.utils as pplu
        import production.python_job as ppj
        from production.farm_ip import LcaFarmIPManage
        tokens=self.dialog.version_dir.split('/')
        proj = tokens[4]
        asset_name = tokens[7]
        asset_version = tokens[10]
        
        
        katana_exe = pplu.get_dcc_launcher('katana', proj)
        push_uv_job_id = ppj.send_job(
            '--script=' + os.getenv('LC_TOOLSET') + '/tools/srf/push_shader/srf_pass_update.py',
            args=proj + ' ' + asset_name + ' ' + str(0),
            proj=proj,
            step='SRF',
            python_exe=katana_exe,
            job_name_prefix='[Update UV] ' + asset_version,
            url=LcaFarmIPManage().MASTERCACHE,
            pools='rv',
            priority=2000,
            submitdl=True)
        print '\n\n Push uv  on farm,job id :', push_uv_job_id
        
    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


