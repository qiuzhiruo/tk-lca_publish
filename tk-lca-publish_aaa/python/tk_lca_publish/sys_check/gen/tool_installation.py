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
import sys
import os
import glob


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查需要的软件是否安装"
        self.description = u"检查转pdf工具 imconvert 和转mov的工具rvio是否安装。"
        self.auto_fix = False
        self.duty = u"IT部门安装软件。"
        return

    def run_check(self):
        try:
            if sys.platform.startswith('win'):
                self.dialog.os = 'win'
                rvio_7_list = glob.glob('C:/Program Files/Shotgun/RV*/bin/rvio_hw.exe')
                rvls_7_list = glob.glob('C:/Program Files/Shotgun/RV*/bin/rvls.exe')
                if rvio_7_list and rvls_7_list:
                    self.dialog.rvio_path = rvio_7_list[0]
                    self.dialog.rvls_path = rvls_7_list[0]
                else:
                    self.dialog.rvio_path = "C:/Program Files/Tweak/RV-4.0.10-64/bin/rvio_hw.exe"
                    self.dialog.rvls_path = "C:/Program Files/Tweak/RV-4.0.10-64/bin/rvls.exe"
                self.dialog.pdf_tool = "W:/software/imconvert/imconvert.exe"
                self.dialog.process_shell = False
            elif sys.platform.startswith('linux'):
                self.dialog.os = 'linux'

                rv_directory = '/usr/local/rv/rv-linux'
                if not os.path.isdir(rv_directory):
                    rv_directory = '/usr/local/rv/rv-Linux-x86-64-6.2.2'
                    if not os.path.isdir(rv_directory):
                        rv_directory = '/usr/local/rv/rv-Linux-x86-64-4.0.10'

                self.dialog.rvio_path = rv_directory + "/bin/rvio_hw"
                self.dialog.rvls_path = rv_directory + "/bin/rvls"
                self.dialog.pdf_tool = "/mnt/usr/bin/convert"
                self.dialog.process_shell = True
            elif sys.platform.startswith('darwin'):
                self.dialog.os = 'mac'
                self.dialog.rvio_path = "/Applications/RV64.app/Contents/MacOS/rvio_hw"
                self.dialog.rvls_path = "/Applications/RV64.app/Contents/MacOS/rvls"
                self.dialog.pdf_tool = ""
                self.dialog.process_shell = True

            if not os.path.isfile(self.dialog.rvio_path):
                return u"没有找到转换视频工具rvio: " + self.dialog.rvio_path

            if not os.path.isfile(self.dialog.pdf_tool) and not os.path.isfile('/usr/local/bin/convert'):
                return u"没有找到转PDF工具: " + self.dialog.pdf_tool

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
