# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Jingwei Wan
#
# Date: 2016.6
#
# Description: Check to see if there is completely overlapping geometry
#
########################################################################################

import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查疑似完全重叠的几何体"
        self.description = u"检查是否有完全重叠的模型，如果有，需要模型师确认是否为多余物体。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            sum_str = ''
            for res in pm.listRelatives('|master|poly', c=True, type = 'transform'):
                mesh_list = pm.listRelatives(res, ad=True, type = "mesh")
                bboxStr_dict = {}
                overlapping_geo_list =[]
                for mesh in mesh_list:
                    mesh = mesh.getParent()
                    name = str(mesh.name())
                    bbox = mesh.getBoundingBox()
                    bboxStr = ""
                    for i in bbox:
                        for j in i:
                            bboxStr = bboxStr + "%.8f "%j
                    bboxStr_dict.setdefault(bboxStr, list())
                    bboxStr_dict.get(bboxStr).append(name)


                for k,v in bboxStr_dict.items():               
                    if len(v) > 1:
                        #print v
                        sub_str = ''                   
                        for i in range(len(v)):
                            if i != (len(v)-1):
                                sub_str = sub_str + v[i] + " 和 "
                            else:
                                sub_str = sub_str + v[i] + " 疑似重叠\n"
                            pm.select(v[i],add =True)
                        sum_str = sum_str + sub_str
            
            if sum_str:
                return "已选中以下疑似与其他物体完全重合的物体，请检查：\n" + sum_str            
            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


