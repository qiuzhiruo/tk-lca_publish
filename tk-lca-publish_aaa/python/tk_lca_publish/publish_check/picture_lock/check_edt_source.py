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

import traceback
import os
import subprocess
import sgtk
from sgtk.platform.qt import QtCore, QtGui

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 Edt 文件中素材是否符合规范"
        self.description = u"1.使用的是 lgt/pfx 的mov文件\n2.同一个镜头只能用一个版本作为素材\n3.版本有jpg左眼序列\n4.剪辑的帧范围有效(该版本的图片序列有这一帧)"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def get_mov_length(self, src):
        p = subprocess.Popen('"' + self.dialog.rvls_path + '" -l ' + src, shell=True, stdin=subprocess.PIPE, stdout= subprocess.PIPE)
        p_communicate =p.communicate()
        tokens_a = p_communicate[0].split('\n')
        if len(tokens_a) >= 2:
            tokens_b = [i for i in tokens_a[1].split(' ') if i != '']
            if len(tokens_b) >=8 and tokens_b[6].isdigit():
                return int(tokens_b[6])

        return None


    def run_check(self):

        try:
            self.dialog.d_shot_versions = {}
            self.dialog.video_length = 0

            for i in sorted(self.dialog.edt_cuts.keys()):
                shot_name = self.dialog.edt_cuts[i]['shot_name']

                for edt_info in self.dialog.edt_cuts[i]['edt_info']:
                    v_name = edt_info[0]
                    tokens = v_name.split('.')

                    if shot_name != tokens[0]:
                        return u"镜头 " + shot_name + u" 所使用的版本 " + v_name + u" 镜头号不匹配。"

                    dept = tokens[1]
                    if not dept in ['lgt', 'pfx']:
                        return u"剪辑使用了非 lgt/pfx 的版本: " + v_name

                    if not self.dialog.d_shot_versions.has_key(shot_name) :
                        self.dialog.d_shot_versions[shot_name] = {}

                    #if not self.dialog.d_shot_versions[shot_name].has_key(v_name):
                    version = self.dialog.sg.find_one('Version', [['project', 'is', self.dialog.project], ['code', 'is', v_name]], ['entity', 'sg_task', 'code', 'frame_count', 'sg_version_folder', 'sg_version_type', 'tag_list', 'sg_path_to_movie', 'entity.Shot.sg_cut_duration'])
                    if version['frame_count'] is None:
                        mov = version['sg_version_folder']['local_path'].replace('\\', '/') + 'preview/' + v_name + '.mov'
                        length = self.get_mov_length(mov)

                        if length != None:
                            self.dialog.sg.update('Version', version['id'], {'frame_count': length})
                            version['frame_count'] = length

                    version['images'] = []
                    self.dialog.d_shot_versions[shot_name][v_name] = version
                    #self.dialog.print_log('%s' % str(self.dialog.d_shot_versions))
                    if version['frame_count'] is None:
                        return u"无法获得镜头: " + v_name + u" 的时长"

                    if len(self.dialog.d_shot_versions[shot_name].keys()) > 1:
                        return u"在镜头 " + shot_name + u" 使用了多个版本进行剪辑: " + u" ".join(self.dialog.d_shot_versions[shot_name].keys())
                    
                    #if len(version['images']) == 0:
                    img_dir = version['sg_version_folder']['local_path'] + 'jpg/L'
                    if not os.path.isdir(img_dir):
                        return u"版本 " + v_name + u" 没有 /jpg/L 的文件夹"
                    l_imgs = [f for f in os.listdir(img_dir) if f.endswith('.jpg')]
                    l_imgs.sort()
                    version['images'] = l_imgs
                    
                    #self.dialog.print_log(shot_name + ':edt_info[2] '  + str(edt_info[2]) + ' / ' + str(len(version['images']))) + ' ' + img_dir
                    if edt_info[2] > len(version['images']):
                        return u"剪辑信息: " + edt_info[0] + u" " + str(edt_info[1]) + u" " + str(edt_info[2]) + u" 使用的帧数超出了版本的图片序列的范围。"

                    self.dialog.video_length += edt_info[2] - edt_info[1]

            return ""
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

