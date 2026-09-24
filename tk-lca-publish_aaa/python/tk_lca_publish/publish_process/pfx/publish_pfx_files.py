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
import traceback
import shutil
import subprocess
import multiprocessing
import time
import ConfigParser
import re

def call_cmd(cmd):
    p=subprocess.Popen(cmd)
    p.wait()

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return


    def proceed(self):
        try:
            l_folder=str(self.dialog.w_publish_file.lineEdit_lseq.text())
            r_folder=str(self.dialog.w_publish_file.lineEdit_rseq.text())
            nk_file=str(self.dialog.w_publish_file.lineEdit_nk.text())
            self.publish_file_data = [l_folder,r_folder,nk_file]

            try:
                os.makedirs(self.dialog.version_dir+'/exr')
                os.makedirs(self.dialog.version_dir+'/jpg/L')
                os.makedirs(self.dialog.version_dir+'/jpg/R')
            except:
                pass

            if l_folder and self.dialog.l_seqs and os.path.isdir(self.dialog.version_dir+'/exr'):
                if os.path.islink(self.dialog.version_dir+'/exr/L'):
                    os.unlink(self.dialog.version_dir+'/exr/L')
                os.symlink(l_folder, self.dialog.version_dir+'/exr/L' )

            if r_folder and self.dialog.r_seqs and os.path.isdir(self.dialog.version_dir+'/exr'):
                if os.path.islink(self.dialog.version_dir+'/exr/R'):
                    os.unlink(self.dialog.version_dir+'/exr/R')
                os.symlink(r_folder, self.dialog.version_dir+'/exr/R' )

            if l_folder :
                for l in self.dialog.l_jpg_seqs:
                    shutil.copy(l,self.dialog.version_dir+'/jpg/L/'+os.path.basename(l))

            if r_folder :
                for r in self.dialog.r_jpg_seqs:
                    shutil.copy(r,self.dialog.version_dir+'/jpg/R/'+os.path.basename(r))

            if nk_file:
                shutil.copy(nk_file,os.path.join(self.dialog.version_dir,os.path.basename(nk_file)))
            try:
                with open('/mnt/proj/trash/lgt_publish_info/'+self.dialog.version.split('/')[3]+'.'+os.path.basename(self.dialog.version)+'.pub','w') as f:
                    f.writelines(self.dialog.version)
            except:
                traceback.print_exc()


            return ''
        except:
            try:
                if os.path.isdir(self.dialog.version_dir):
                    shutil.rmtree(self.dialog.version_dir)
                return u'Publish 没有成功，拷贝文件出错。'+traceback.format_exc()
            except:
                return u'Publish 没有成功,试图删除版本号出错。'+traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
