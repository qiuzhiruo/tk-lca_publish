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

import os
import re
import traceback
import shutil
import subprocess
import tempfile
import ConfigParser
# All publish process will use StdProcess as the class name.

def get_shot_client_name(dialog):
    projFilter = [ ['name', 'is', str(dialog.project['name'])] ]
    shotgunProjInfo = dialog.sg.find_one('Project', projFilter)

    shotFilter = [
        ['code', 'is', dialog.entity['name']],
        ['project', 'is', {'type': 'Project', 'id': shotgunProjInfo['id']}]
        ]
    info = dialog.sg.find_one('Shot', shotFilter, ['sg_client_name', 'sg_cut_in', 'sg_cut_out'])
    return info


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"创建三帧tif到服务器上的文件夹"
        self.description = u"将艺术家提交的exr文件使用rvio 转换 首中尾三帧到版本文件夹下的tif目录。\n如果有外部镜头名称,将加一个内部和外部镜头在一起的水印。"
        return

    def convert_tif_frames(self):
        # Convert tif , if there's a "tif" folder in the "version_dir".

        if not self.dialog.l_preview_files :
            self.dialog.print_log('No exr file in preview list.')
            return ''
        preview_files = [i for i in self.dialog.l_preview_files]
        # self.dialog.print_log(str(preview_files))
        l_folder=os.path.dirname(self.dialog.l_preview_files[0])

        # prepare exr output path as source 
        src_lst = [
            l_folder,
            '{0}.lgt.comp.####.exr'.format(self.dialog.entity['name'])
            ]
        src_seq = '/'.join(src_lst)

        # prepare tif publish dir as destination 
        tif_lst = [
            self.dialog.version_dir,
            'tif/{0}.lgt.comp.####.tif'.format(self.dialog.entity['name'])
            ]
        tif_seqs = '/'.join(tif_lst)

        # Get client shot name. Used as a watermark. 
        info = get_shot_client_name(self.dialog)
        client_name = info['sg_client_name']
        if not client_name:
            client_name = ' '
        self.dialog.print_log("client name : "+client_name)
        # Get frames. Convert first ,middle and last frames .
        frame_ptn = re.compile(r'\b\d{4}\b')

        # fst_frame = info['sg_cut_in']
        # lst_frame = info['sg_cut_out']
        # mid_frame = int(fst_frame) + (int(lst_frame) - int(fst_frame))/2

        fst_frame = frame_ptn.search(preview_files[0]).group()
        lst_frame = frame_ptn.search(preview_files[-1]).group()
        mid_frame = int(fst_frame) + (int(lst_frame) - int(fst_frame))/2
        fml_frames = '{0},{1},{2}'.format(fst_frame,mid_frame,lst_frame)
        self.dialog.print_log("Frames: "+fml_frames)
        # CMD string 
        cmd_lst = [
            self.dialog.rvio_path,
            src_seq,
            '-o',
            tif_seqs,
            '-codec NONE',
            '-overlay textburn " " " " " " " " " " " {0} | {1} " 0.3 40.0'.format(self.dialog.version_name,client_name),
            '-out8',
            '-outsrgb',
            "-t '{0}'".format(fml_frames)
            ]

        cmd = ' '.join(cmd_lst)
        self.dialog.print_log("CMD: "+cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        self.dialog.print_log('Converting tif done.')
        return
        
    def proceed(self):
        # if 'R3' in self.dialog.version_tag:
        #     return ''

        # if self.dialog.publish_mode==0:
        self.dialog.print_log('Create tif dir.')
        tif_dir = self.dialog.version_dir+'/tif'
        if not os.path.isdir(tif_dir):
            try:
                os.makedirs(self.dialog.version_dir+'/tif',0777)
            except:
                return traceback.format_exc()

        self.dialog.print_log('Converting tif ....')
        try:
            self.convert_tif_frames()
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description