# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shtogun data
#
############################################

import traceback
import tempfile
import os
import re
import subprocess

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的预览文件的尺寸。"
        self.description = u"提交的预览文件尺寸过大会导致shot服务器内存的浪费，可以吧文件路径放在描述里面。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            l_preview_files = [self.dialog.w_file.listWidget_preview.item(i).text() for i in xrange(self.dialog.w_file.listWidget_preview.count())]

            if len(l_preview_files) == 0:
                return u"还没有选择文件。"

            zero_file=[]
            huge_file=[]
            index=0

            self.huge_file_index=[]
            for file_path_qtstr in l_preview_files:
                file_path = str(file_path_qtstr)

                p = subprocess.Popen('"' + self.dialog.rvls_path + '" -l ' + file_path, shell=True, stdin= subprocess.PIPE, stdout= subprocess.PIPE)
                tokens = p.communicate()[0].split('\n')[1].split(' ')
                tokens = [i for i in tokens if i != '']

                img_w = int(tokens[0])
                img_h = int(tokens[2])
                self.ratio = min(900/float(float(img_w)), 600/float(img_h))

                if img_w == 0 or img_h ==0:
                    zero_file.append(file_path)
                    l_preview_files.remove(file_path)

                if img_w >3000 or img_h >3000:
                    huge_file.append(file_path)
                    l_preview_files.remove(file_path)
                    self.huge_file_index.append(index)
                    #self.dialog.w_file.listWidget_preview.takeItem(index)

                index+=1

            if not len(zero_file)==0:
                return u"文件没有尺寸大小 : ".join(zero_file)

            if not len(huge_file)==0:
                self.huge_list=huge_file
                return u" ".join(huge_file) +u'文件尺寸超过3k , 使用自动修复可以把文件尺寸转到3k一下。'

            self.dialog.l_preview_files = l_preview_files

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''

        try:
            if self.huge_file_index==0:
                return u"文件尺寸为0的无法修复。"

            else:
                for index in self.huge_file_index:
                    src = str(self.dialog.w_file.listWidget_preview.item(index).text())
                    dst=os.path.join(tempfile.mkdtemp(),os.path.basename(src))
                    cmd = '"'+ self.dialog.rvio_path +'" ' +src  + ' -scale ' + str(self.ratio) + ' -o ' + dst

                    ext_src = src.lower().split('.')[-1]
                    if ext_src == 'exr':
                        cmd += ' -outsrgb'

                    os.system(cmd)

                    self.dialog.w_file.listWidget_preview.takeItem(index)
                    self.dialog.w_file.listWidget_preview.addItem(dst)

            self.run_check()
            return ""

        except:
            return traceback.format_exc()
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


