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
import plt.xgen_file_manager.file_utils as pxfu
reload(pxfu)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出布料毛发ma文件"
        self.description = u"将文件另存为一个ma文件。"
        return


    def proceed(self):
        try:
            self.dialog.tank_file = self.dialog.version_dir +'/'+ self.dialog.entity['name'] + '.ma'
            pxfu.export_scene(self.dialog.version_dir,
                                         update_xgdatapath=True,
                                         preserve_reference=False,
                                         entity_name=self.dialog.entity['name']
                                     )

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

