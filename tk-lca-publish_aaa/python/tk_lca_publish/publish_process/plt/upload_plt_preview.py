# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Huang Xin
#
# Date: 2020.6
#
# Description: As the description shows below
#
# when publish plt, upload mov to plant_edit task
#
#
#
#
#
#
############################################

import os, shutil, sys
import traceback
import production.rv_python as rvpy
import production.python_job as ppj
import production.pipeline.utils as pplu
from production.farm_ip import LcaFarmIPManage
import getpass

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"更新plant_edit渲染图"
        self.description = u"将当前mov更新到plant_edit任务下"

    def proceed(self):
        try:
            if "plant_edit" == self.dialog.task['name']:
                return ""

            self.dialog.l_preview_files = [str(f_path) for f_path in self.dialog.l_preview_files]
            if not self.dialog.l_preview_files:
                return ""

            versionEntity = self.dialog.sg.find('Version',[['project','is', self.dialog.project],
                ['entity','is', self.dialog.entity],
                ['code','contains', "plant_edit"]],
                ['id','sg_version_folder','sg_version_type'])

            if versionEntity:
                latest_version = versionEntity[-1]
                path = latest_version['sg_version_folder']['local_path_linux']
                mov_path = self.dialog.l_preview_files[0]
                mov_folder = mov_path[:-4]
                if os.path.isdir(mov_folder):
                    cur_mov = path+'preview/'+path.split('/')[-2]+'.mov'
                    if not os.path.isfile(cur_mov):
                        return ""

                    job_id = ppj.send_job(__file__,
                        args=' '+' '.join([self.dialog.entity['name'], mov_path, cur_mov, str(latest_version['id'])]),
                        proj=self.dialog.project['name'].upper(),
                        job_name_prefix='[Upload_plt_mov]'+self.dialog.project['name']+'_'+self.dialog.entity['name']+' by '+getpass.getuser(),
                        step='PLT',
                        user=getpass.getuser(),
                        url=LcaFarmIPManage().MASTERCACHE,
                        python_exe=pplu.get_dcc_launcher(proj='gen',dcc='lca_python'),
                        submitdl=True
                    )
                    
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


def upload_sg_mov(shot, mov_path, cur_mov, version_id):
    mov_folder = mov_path[:-4]
    exr_seq = mov_folder+'/'+shot+'.plt.####.exr'
    memory = rvpy.get_exrseq_memory(exr_seq)[0]
    render_time = rvpy.get_exrseq_time(exr_seq)[-1]

    from production import shotgun_connection
    sg = shotgun_connection.Connection('get_shot_info').get_sg()

    print 'Copy -- %s -- to -- %s'%(mov_path, cur_mov)
    shutil.copyfile(cur_mov, cur_mov+'.old.mov')
    shutil.copyfile(mov_path, cur_mov)
    print 'Update_shotgun_info: ', version_id, cur_mov, memory, render_time
    if memory and render_time:
        extra_data = {'sg_memory': float('%.2f'%memory), 'sg_remark':'%.2fmin'%render_time}
        sg.update('Version', int(version_id), extra_data)
    sg.upload('Version', int(version_id), mov_path, 'sg_uploaded_movie')


if __name__ == '__main__':
    shot = sys.argv[1]
    mov_path = sys.argv[2]
    cur_mov = sys.argv[3]
    version_id = sys.argv[4]

    upload_sg_mov(shot, mov_path, cur_mov, version_id)
   