# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.08
#
# Description: 
#
############################################

import os
import traceback
import shutil
from sgtk.platform.qt import QtCore, QtGui

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝 sequence picture lock 图片序列链接"
        self.description = u"拷贝 sequence picture lock 图片序列链接"
        return


    def proceed(self):
        try:
            isStereo = self.dialog.w_publish_file.stereo_checkBox.checkState()
            self.copy_images_to_picklock('L')
            if isStereo == QtCore.Qt.Checked:         #Left + Right
                self.copy_images_to_picklock('R')
            
            return ""

        except:
            return traceback.format_exc()


    def copy_images_to_picklock(self, L_or_R):
        img_dir = self.dialog.version_dir + '/jpg/%s/' % L_or_R
        if not os.path.isdir(img_dir):
            os.makedirs(img_dir)

        for file_name in os.listdir(img_dir):
            if os.path.isfile(img_dir + file_name):
                os.remove(img_dir + file_name)
        
        # e.g. /mnt/proj/projects/cat or Z:/project/cat
        root_path = self.dialog.version_dir.replace('\\', '/').split('/preproduction/')[0]
        frame_cnt = 1
        for i in sorted(self.dialog.edt_cuts.keys()):
            shot_name = self.dialog.edt_cuts[i]['shot_name']
            for edt_info in self.dialog.edt_cuts[i]['edt_info']:
                v_name = edt_info[0]
                l_files = self.dialog.d_shot_versions[shot_name][v_name]['images']
                tokens = v_name.split('.')
                
                for j in range(edt_info[1], edt_info[2]):
                    src_file = root_path + '/shot/' + tokens[0][:3] + '/' + tokens[0] + '/' + tokens[1] + '/publish/' + v_name + '/jpg/%s/' % L_or_R + l_files[j]
                    dest_file =  img_dir + self.dialog.entity['name'] + '.' + ('%06d' % frame_cnt) + '.jpg'
                    shutil.copyfile(src_file, dest_file)
                    frame_cnt += 1

            # link blank images
            blank_img_root_path = root_path.replace('\\', '/').split('/projects/')[0]
            # /mnt/proj/resource/picturelock/TPR/config/blank.jpg
            blank_img_path = blank_img_root_path + '/resource/picturelock/img/blank.jpg'

            edt_info_end = self.dialog.edt_cuts[i]['edt_info'][-1][4]
            if i >= len(self.dialog.edt_cuts.keys()) - 1:
                break
            # e.g. [['z12020.lgt.lighting.v010', 0, 73, 352, 425], ['z12020.lgt.lighting.v010', 74, 76, 426, 428]]
            shot_info_list = self.dialog.edt_cuts[i + 1]['edt_info']
            for j, shot_info in enumerate(shot_info_list):
                next_edt_start = shot_info[3]
                if next_edt_start > edt_info_end:
                    blank_length = int(next_edt_start) - int(edt_info_end)
                    self.dialog.print_log('blank_img_path: ' + blank_img_path)
                    self.dialog.print_log('fill blank_jpg: %d (%d - %d)\n' % (blank_length, frame_cnt, frame_cnt + blank_length))
                    for k in range(blank_length):
                        dest_file = img_dir + tokens[0][:3] + '.' + ('%06d' % frame_cnt) + '.jpg'
                        self.dialog.print_log(dest_file)
                        shutil.copyfile(blank_img_path, dest_file)
                        frame_cnt += 1
                edt_info_end = shot_info[4]
            

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

