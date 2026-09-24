# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import traceback
import subprocess
import sys
import copy_katana_set as cks
import datetime

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return



    def proceed(self):
        try:
            # For art/edt department, the publish files and the preview files are the same.
            # for file_path in self.dialog.l_preview_files:
            #     shutil.copyfile(file_path, self.dialog.version_dir + '/' + os.path.basename(file_path))
            
            tag_text = str(self.dialog.w_sys.comboBox_tag.currentText())
            tag_text_time= tag_text+' ( '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")+' )'
                        
            cks.copy_katana_set(self.dialog,{'status':tag_text})

            # task
            self.dialog.sg.update('Task',self.dialog.task['id'],{'sg_remark':tag_text_time})

            if 'Final' in tag_text:
                self.dialog.sg.update('Version',self.dialog.v_info['id'],{'sg_status_list':'apr'})
                self.dialog.sg.update('Task',self.dialog.task['id'],{'sg_status_list':'sc'})

                #da tasks for those steps
                self.da_shot_task('efx')
                self.da_shot_task('cfx')
                self.da_shot_task('ani')
                self.da_shot_task('flo')

            return ''

        except:
            return traceback.format_exc()

    def da_shot_task(self,step):
        shot = self.dialog.entity['name']
        proj = self.dialog.project['name']


        filter_data=[
            ['entity', 'name_is', shot],
            ['entity', 'type_is', 'shot'],
            ['step', 'name_is',step],
            ['project', 'is', self.dialog.project]
        ]

        tasks=self.dialog.sg.find('Task', filter_data, ['id','sg_status_list'])
        
        result=[]
        for task in tasks:
            if task['sg_status_list'] not in ['da','fin','cbb','omt','hld']:
                self.dialog.sg.update('Task',task['id'],{'sg_status_list':'da'})

        self.dialog.print_log('DA tasks of step '+step)

    def da_final_layout(self):
        shot = self.dialog.entity['name']
        proj = self.dialog.project['name']

        filter_data=[
                ['entity', 'name_is', shot],
                ['content','is', 'final_layout'],
                ['step','name_is','flo'],
                ['project', 'is', self.dialog.project]
                ]
                

        final_layout = self.dialog.sg.find_one('Task',filter_data,['id'])
        if final_layout:
            self.dialog.sg.update('Task',
                                 final_layout['id'], 
                                 {'sg_status_list':'da'})

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


