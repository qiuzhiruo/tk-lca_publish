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
from sgtk.platform.qt import QtCore, QtGui

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"生成 sequence picture lock 图片序列链接 (symbolic link)"
        self.description = u"生成 sequence picture lock 图片序列链接 (symbolic link)"
        return


    def proceed(self):
        try:
            isStereo = self.dialog.w_publish_file.stereo_checkBox.checkState()
            self.link_images_to_picklock('L')
            if isStereo == QtCore.Qt.Checked:         #Left + Right
                self.link_images_to_picklock('R')
            
            return ""

        except:
            return traceback.format_exc()


    def link_images_to_picklock(self, L_or_R):
        img_dir = self.dialog.version_dir + '/jpg/%s/' % L_or_R
        if not os.path.isdir(img_dir):
            os.makedirs(img_dir)

        for file_name in os.listdir(img_dir):
            if os.path.isfile(img_dir + file_name):
                os.remove(img_dir + file_name)

        frame_cnt = 1
        for i in sorted(self.dialog.edt_cuts.keys()):
            shot_name = self.dialog.edt_cuts[i]['shot_name']
            for edt_info in self.dialog.edt_cuts[i]['edt_info']:
                v_name = edt_info[0]
                l_files = self.dialog.d_shot_versions[shot_name][v_name]['images']
                tokens = v_name.split('.')
                
                for j in range(edt_info[1], edt_info[2]):
                    cmd = 'ln -s ../../../../../../../../shot/' + tokens[0][:3] + '/' + tokens[0] + '/' + tokens[1] + '/publish/' + v_name + '/jpg/%s/' % L_or_R + l_files[j] + ' '
                    #cmd += img_dir + tokens[0][:3] + '.' + ('%06d' % frame_cnt) + '.jpg'
                    cmd += img_dir + self.dialog.entity['name'] + '.' + ('%06d' % frame_cnt) + '.jpg'
                    frame_cnt += 1
                    os.system(cmd)
            
            # link blank images
            edt_info_end =  self.dialog.edt_cuts[i]['edt_info'][-1][4]
            if i < len(self.dialog.edt_cuts.keys()) - 1:
                next_edt_start = self.dialog.edt_cuts[i+1]['edt_info'][0][3]
                if next_edt_start > edt_info_end:    
                    self.dialog.print_log('fill blank_jpg: %d\n' % (int(next_edt_start) - int(edt_info_end)))
                    for k in range(int(next_edt_start) - int(edt_info_end)):
                        cmd = 'ln -s ../../../../../../../../../../resource/picturelock/TPR/config/blank.jpg '
                        cmd += img_dir + tokens[0][:3] + '.' + ('%06d' % frame_cnt) + '.jpg'
                        frame_cnt += 1
                        os.system(cmd)


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

