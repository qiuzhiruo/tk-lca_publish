# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: YU HuaZhuo
#
# Date: 2018.03
#
# Description: Add Sequences Tags
#
############################################

import os
import traceback
import shutil
import datetime


# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"添加关联场次"
        self.description = u"添加关联场次，之后会把文件publish到场次的对应任务里面。"
        return

    def proceed(self):
        try:

            st=self.dialog.Seq_TableWidget
            seq_list=[st.item(i,0).text() for i in range(0,st.rowCount()) if st.item(i,0).checkState()!=0]

            self.dialog.sg.update('Version',self.dialog.v_info['id'],{'tag_list':seq_list})
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
