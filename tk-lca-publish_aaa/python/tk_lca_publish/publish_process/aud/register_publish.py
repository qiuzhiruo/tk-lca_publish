# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import traceback
import subprocess
import os
import sys
import pprint
import tank
from sgtk.platform.qt import QtCore, QtGui

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun数据库为音频建立 Published File 。"
        self.description = u"在shotgun数据库建立 PublishedFile。该entity可以被之后的流程工具引用。"
        return



    def proceed(self):
        try:
            wav_files = [wav_file for wav_file in os.listdir(self.dialog.version_dir) if wav_file.endswith('.wav')]
            for wav_file in wav_files:        # from publish_check/aud/audio_sampling_frequency.py
                tank_file = self.dialog.version_dir + '/' + wav_file
                args = {
                    "tk": self.dialog.tk,
                    "context": self.dialog.ctx,
                    "comment": self.dialog.version_name +' ' + self.dialog.description,
                    "task": self.dialog.ctx.task,
                    "dependency_paths": self.dialog.dependency_paths,
                    "published_file_type":  'Audio Wav',
                    "path": tank_file,
                    "name": self.dialog.version_key,
                    "version_number": int(self.dialog.version_num),
                }
                
                try:
                    sg_data = tank.util.register_publish(**args)
                    wav_code = wav_file + '.v%03d' % int(self.dialog.version_num)
                    self.dialog.sg.update(sg_data['type'], sg_data['id'], {"code": wav_code, "version": self.dialog.v_info })
                except:
                    self.dialog.print_log(traceback.format_exc(), txt_color = QtGui.QColor(255, 150, 30))
            return ''

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


