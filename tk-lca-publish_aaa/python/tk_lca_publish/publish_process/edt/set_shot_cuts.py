# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description:
#
############################################

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"设定镜头剪辑"
        self.description = u"将每个镜头的剪辑点输出到镜头之上。"
        return

    def proceed(self):
        try:
            for i in range(self.dialog.w_publish_file.tableWidget_shots.rowCount()):
                shot_item = self.dialog.w_publish_file.tableWidget_shots.item(i,0)
                sg_duration_item = self.dialog.w_publish_file.tableWidget_shots.item(i,3)
                cut_duration_item = self.dialog.w_publish_file.tableWidget_shots.item(i,4)
                if shot_item and cut_duration_item:
                    shot_name = str(shot_item.text())
                    cut_duration = str(cut_duration_item.text())
                    if not cut_duration.isdigit():
                        continue
                    
                    if self.dialog.d_seq_shots[shot_name]['sg_cut_duration'] != int(cut_duration):
                        self.dialog.print_log(u'镜头' + shot_name +u'更新 Duration ->' + cut_duration)
                        self.dialog.sg.update('Shot', self.dialog.d_seq_shots[shot_name]['id'], {'sg_cut_duration': int(cut_duration)})

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


