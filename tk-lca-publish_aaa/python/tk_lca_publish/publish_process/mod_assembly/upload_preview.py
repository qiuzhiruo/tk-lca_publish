# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: 
#
############################################

import os
import sys
import traceback
import shutil
import subprocess
import getpass

# from PySide import QtGui
import sgtk
from sgtk.platform.qt import QtCore, QtGui
os.environ['RV_ENABLE_MIO_FFMPEG'] = '1'


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"上传缩略图"
        self.description = u"为shotgun提交版本直接上传或者将图片序列转换一个视频文件(*.mov)作为版本预览，会帮助其他艺术家快速了解这个版本。"
        return


    def create_version_preview(self, jpg_file, mov_file):
        cmd = '"'+ self.dialog.rvio_path +'" [ ' + jpg_file + ' -pa 1.0 ] -o ' + mov_file
        if sys.platform.startswith('linux'):
            cmd += ' -outparams comment="author '+getpass.getuser()+'"'

        p = subprocess.Popen(cmd, shell=True)
        p.communicate()

        print 'preview file: ' + mov_file
        return mov_file


    def proceed(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                if os.path.isfile(self.dialog.d_assets_info[asset_name]['thumbnail']):
                    if asset_name == self.dialog.entity['name']:
                        jpg_file = self.dialog.l_preview_files[0]

                    else:
                        jpg_file = self.dialog.d_assets_info[asset_name]['thumbnail']

                    version_dir = self.dialog.d_assets_info[asset_name]['version_dir'] 
                    version_name = self.dialog.d_assets_info[asset_name]['version_name']
                    v_info = self.dialog.d_assets_info[asset_name]['v_info']
                    mov_file = self.dialog.d_assets_info[asset_name]['version_dir'] + '/preview/' + version_name + '.mov'

                    self.create_version_preview( jpg_file, mov_file)
                    if asset_name == self.dialog.entity['name']:
                        self.dialog.v_preview=mov_file
                    # Upload
                    if os.path.isfile(mov_file):
                        try:
                            self.dialog.sg.upload('Version', v_info['id'], mov_file, "sg_uploaded_movie")
                        except:
                            self.dialog.print_log('Failed to upload the mov file for '+version_name+'. Will be upload later.', txt_color = QtGui.QColor(255, 150, 30))

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

