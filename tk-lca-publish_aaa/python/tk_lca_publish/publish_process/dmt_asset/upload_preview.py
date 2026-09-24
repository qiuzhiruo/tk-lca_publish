# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Upload the thumbnail for shotgun
#
############################################

import os
import traceback
import shutil

from PySide import QtGui

# TODO: Check for different O.S.
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"上传缩略图"
        self.description = u"为shotgun提交版本直接上传或者将图片序列转换一个视频文件(*.mov)或pdf文件作为预览，该文件会帮助其他艺术家快速了解这个版本。"
        return


    def create_version_preview(self):
        # create preview folder
        preview_dir = self.dialog.version_dir + '/preview/'
        if not os.path.isdir(preview_dir):
            os.makedirs(preview_dir)

        # Jpg - copy and convert
        # mov - copy

        if len(self.dialog.l_preview_files) == 1 and self.dialog.l_preview_files[0].endswith('.mov'):
            self.dialog.v_preview = preview_dir + self.dialog.version_name +'.mov'
            cmdStr = ' '.join(['Copy', self.dialog.l_preview_files[0], self.dialog.v_preview])
            shutil.copyfile( self.dialog.l_preview_files[0], self.dialog.v_preview)
        else:
            l_copied_files = []
            self.dialog.l_preview_files.sort()
            for i in range(len(self.dialog.l_preview_files)):
                shutil.copyfile(self.dialog.l_preview_files[i], preview_dir + (self.dialog.version_name + '.%04d.jpg' % i))
                l_copied_files.append(preview_dir + (self.dialog.version_name + '.%04d.jpg' % i) )

            self.dialog.v_preview = preview_dir + self.dialog.version_name +'.mov'
            cmdStr = '"'+ self.dialog.rvio_path +'" [ ' + preview_dir + self.dialog.version_name + '.%04d.jpg -pa 1.0 ] -o ' + self.dialog.v_preview
            os.system(cmdStr)
            #self.dialog.print_log(cmdStr)

            self.dialog.v_pdf = preview_dir + self.dialog.version_name +'.pdf'
            cmdStr = '"' + self.dialog.pdf_tool + '" -density 72 ' + preview_dir + '*.jpg ' + self.dialog.v_pdf
            os.system(cmdStr)
            #self.dialog.print_log(cmdStr)

            # clean jpg files
            for file_path in l_copied_files:
                os.remove(file_path)

        return cmdStr


    def proceed(self):
        try:
            self.create_version_preview()
            # Upload
            self.dialog.sg.update('Version', self.dialog.v_info['id'], {'sg_path_to_movie': self.dialog.v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/').replace('/mnt/proj/', '${RV_PATHSWAP_ROOT}/').replace('/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/') })

            if os.path.isfile(self.dialog.v_pdf):
                v_preview = self.dialog.v_pdf
            else:
                v_preview = self.dialog.v_preview

            try:
                self.dialog.sg.upload('Version', self.dialog.v_info['id'], v_preview, "sg_uploaded_movie")
            except:
                self.dialog.print_log('Failed to upload the mov file. Will be upload later.', txt_color = QtGui.QColor(255, 150, 30))

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

