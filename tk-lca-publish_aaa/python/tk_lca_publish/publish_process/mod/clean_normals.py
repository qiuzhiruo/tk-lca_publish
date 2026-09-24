# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.09
#
# Description: 
#
############################################

import os
import traceback
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"清理法线。"
        self.description = u"将模型Publish文件中法线信息清除。"
        return


    @record_time(__file__)
    def proceed(self):
        try:
            #print '<clean_normal>'
            #print self.dialog.d_assets_info
            for asset_name in self.dialog.d_assets_info.keys():
                tank_file = self.dialog.d_assets_info[asset_name]['tank_file']

                ma_file = tank_file.replace('\\', '/')
                print ma_file
                f = open(ma_file, 'r')
                l_lines = f.readlines()
                f.close()

                in_mesh_chunk = False
                in_normal_chunk = False

                l_new_lines = []

                for i in range(len(l_lines)):
                    line = l_lines[i]
                    if line.startswith('createNode '):
                        if line.startswith('createNode mesh '):
                            in_mesh_chunk = True
                        else:
                            in_mesh_chunk = False
                            in_normal_chunk = False

                    if in_mesh_chunk:
                        if line.startswith('	setAttr '):
                            tokens = line.split(' ')
                            for t in tokens:
                                if t == '':
                                    tokens.remove(t)

                            if tokens[1] == '-s' and tokens[3].startswith('".n'):
                                in_normal_chunk = True

                            n_key = False
                            for t in tokens:
                                if t.startswith('".n'):
                                    n_key = True

                            if not n_key:
                                in_normal_chunk = False

                    if not in_normal_chunk:
                        l_new_lines.append(line)

                f = open(ma_file, 'w')
                f.writelines(l_new_lines)
                f.close()
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


