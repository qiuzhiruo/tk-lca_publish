# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: Check to see if any vertice are overlapping to each other.
#
########################################################################################

import traceback
import os
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om
import production.pipeline.lcProdProj as lcp
import re

from proc.function_running_time import record_time
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查场景中丢失的贴图"
        self.description = u"检查场景中丢失和非srf的贴图，丢失贴图会导致后面环节渲染错误。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def get_error_tex(self):
        error_image_list=[]
        error_node=[]

        file_list=cmds.ls(type='file')
        for f in file_list:
            f_path = cmds.getAttr(f+'.fileTextureName')
            if not os.path.isfile(f_path) and 'udim' not in f_path or 'projects' not in f_path:
                error_image_list.append(f_path+'  ')
                error_node.append(f)

        file_list=cmds.ls(type='aiImage')
        for f in file_list:
            f_path = cmds.getAttr(f+'.filename')
            if not os.path.isfile(f_path) and 'udim' not in f_path or 'projects' not in f_path:
                error_image_list.append(f_path+'  ')
                error_node.append(f)

        return error_image_list,error_node

    @record_time(__file__)
    def run_check(self):
        try:
            error_image_list,error_node=self.get_error_tex()

            if len(error_image_list)!=0:
                cmds.select(error_node)

                lost_str=''.join(error_image_list)
                return u'当前场景中有丢失和非srf的贴图 : '+lost_str


            return ""
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''

        try:
            error_image_list,error_node=self.get_error_tex()
            cmds.delete(error_node)
            return ''

        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


