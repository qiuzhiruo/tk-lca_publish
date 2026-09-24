# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.04
#
# Description: Create image thumbnails for art tools
#
############################################

import os
import traceback
import shutil
import subprocess

# from PySide import QtGui
import sgtk
from sgtk.platform.qt import QtCore, QtGui

# TODO: Check for different O.S.
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出png缩略图"
        self.description = u"为艺术预览工具输出png图标。因为Linux下qt不支持很多图片格式。"
        return


    def convert_file(self, src, dst):
        # p = subprocess.Popen('"' + self.dialog.rvls_path + '" -l ' + src, shell=True, stdin= subprocess.PIPE, stdout= subprocess.PIPE)
        # print 'p.communicate() : ',p.communicate()
        # tokens = p.communicate()[0].split('\n')[1].split(' ')
        # tokens = [i for i in tokens if i != '']
        #
        # if not (tokens[0].isdigit() and tokens[2].isdigit()):
        #     return
        #
        # img_w = int(tokens[0])
        # img_h = int(tokens[2])
        #
        # if img_w == 0 or img_h ==0:
        #     return
        #
        # ratio = min(900/float(float(img_w)), 600/float(img_h))
        # cmd = '"'+ self.dialog.rvio_path +'" ' +src  + ' -scale ' + str(ratio) + ' -o ' + dst
        
        cmd = '"'+ self.dialog.rvio_path +'" ' +src  + ' -o ' + dst
        ext_src = src.lower().split('.')[-1]
        if ext_src == 'exr':
            cmd += ' -outsrgb'

        os.system(cmd)
        return


    def proceed(self):
        try:
            thumbnail_dir = self.dialog.version_dir + '/thumbnail/'
            if not os.path.isdir(thumbnail_dir):
                os.makedirs(thumbnail_dir)

            file_path=str(self.dialog.l_preview_files[0])

            dst = thumbnail_dir + os.path.basename(str(file_path)) + '.png'
            self.convert_file(file_path, dst)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

