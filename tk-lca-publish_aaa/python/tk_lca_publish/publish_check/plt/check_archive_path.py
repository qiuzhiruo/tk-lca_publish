# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: yingjie
#
# Date: 2017.5.26
#
# Description: As the description shows below
#
############################################

import traceback
import plt.xgen_file_manager.file_utils as pxfu

    
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查description里的archive 路径"
        self.description = u"只能使用植被库里的archive，和当前项目的archive"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def is_archive_valid(self,archive_path):
        if archive_path.startswith('/mnt/proj/projects/'+self.dialog.project['name'].lower()) or \
            archive_path.startswith('${LC_PROJ_PATH}/'+self.dialog.project['name'].lower()) or \
            archive_path.startswith('${LC_PROJ_PATH}/render_lib/plant') or \
            archive_path.startswith('/mnt/work/projects/lib/publish/asset/')  or \
            archive_path.startswith('${LC_WORK_PATH}/lib/publish/asset/') or \
            archive_path.startswith('${LC_PROJ_PATH_PLANT_ARCHIVE}/'+self.dialog.project['name'].lower()) or \
            archive_path.startswith('${LC_PROJ_PATH_PLANT_ARCHIVE}/render_lib/plant'):
            return True
        else:
            return False            

    def run_check(self):
        try:
            archive_file_path=pxfu.get_all_archives()
            error_archive=[]
            proj_name=self.dialog.project['name'].lower()

            for k,paths in archive_file_path.items():
                for v in paths:
                    if proj_name in ['cat']:
                        if  not self.is_archive_valid(v):
                            error_archive.append(k+' '+v.split('xg_archive')[0])
                    elif not pxfu.is_archive_valid(v, proj_name):
                        error_archive.append(k+' '+v.split('xg_archive')[0])

            if error_archive:
                return u'不能使用其它项目的archive\n'+'\n'.join(error_archive)

            return ''
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


