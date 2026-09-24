# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Zhixiang
#
# Date: 
#
# Description: As the description shows below
#
############################################

import os
import shutil
import traceback
import xml.dom.minidom as dom
import pymel.core as pm
from proc import apply_uv


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出布料毛发ma文件"
        self.description = u"将文件另存为一个ma文件。"
        return


    def proceed(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                apply_uv.replace_uvmap_folliclemap('lcacfxmap')
            pm.select('|master')
            self.dialog.tank_file = self.dialog.version_dir +'/'+ self.dialog.entity['name'] + '.ma'
            pm.exportSelected(self.dialog.tank_file, type='mayaAscii' )
            # #export Static Asset tag File
            # staticAsset=self.dialog.w_publish_file.dynamiceButton.isChecked()
            # if staticAsset:
            #     tagFile = self.dialog.version_dir + "/staticTag"
            #     file = open(tagFile, 'w')
            #     file.close()

            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

            #thanks  Wanghuan for the help of  getting the model asset path 
            #sg = sgc.get_sg('get_shot_info')

            #self.dialog.print_log(str(self.dialog.project))
            #self.dialog.print_log(str(self.dialog.entity))
            #ABCpathDic={}
            #try:
            #    ABCpathDic=sg.find_one('Version', [['project', 'name_is', self.dialog.project['name']], ['entity', 'name_is', self.dialog.entity['name']], ['sg_version_type', 'is', 'Downstream'], ['sg_task', 'name_is', 'model']], ['sg_version_folder'], order=[{'field_name':'code','direction':'desc'},])  
            #    self.dialog.print_log(ABCpathDic['sg_version_folder']['local_path'])
            #except:
            #    return u'找不到模型资产,请检查你的资产是否存在'
            #ABCpath=ABCpathDic['sg_version_folder']['local_path']+'/scene_graph_xml/hi.abc'

