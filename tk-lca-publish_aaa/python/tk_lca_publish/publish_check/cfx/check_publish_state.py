# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Huang Xin
#
# Date: 2020.3
#
# Description: As the description shows below
#
############################################

import os
import traceback
import re

# All system check classes will use StdCheck as the class name.





class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查publish任务状态"
        self.description = u"当前镜头所有角色任务都已aa/sc，才可带‘制作’Tag publish 下游。\n所有任务只存在rtk/sc/da状态，才可带‘返修’Tag publish 下游"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def __check_ds(self):
        """
        return check result
        """
        filter_data=[
            ['entity', 'is', self.dialog.entity],
            ['entity', 'type_is', 'shot'],
            ['step', 'is', self.dialog.step],
            ['project', 'is', self.dialog.project],
            ['content', 'not_in', ['hair','cloth']],
            ["sg_status_list","not_in",["aa","sc","da","omt"]]
        ]
        uncompleted_tasks = self.dialog.sg.find('Task', filter_data, ['id','code', 'content','sg_status_list'])

        if uncompleted_tasks:
            return u'以下任务状态不是aa/sc/da/omit, 不能带“制作”Tag publish下游，如果修改已完成联系制片改aa：\n'+', '.join(t['content'] for t in uncompleted_tasks)+u'\n如果是临时版给下游请选择“测试”Tag，如果是retake返修请选择“返修”Tag'
        else:
            return ""

    def __check_retake(self):
        """
        return check result
        """
        filter_data=[
            ['entity', 'is', self.dialog.entity],
            ['entity', 'type_is', 'shot'],
            ['step', 'is', self.dialog.step],
            ['project', 'is', self.dialog.project],
            ["sg_status_list","in",["wtg","rdy","hld","ip","aaa"]]
        ]
        uncompleted_tasks = self.dialog.sg.find('Task', filter_data, ['id','code', 'content','sg_status_list'])
        if uncompleted_tasks:
            return u'以下任务状态还是制作中, 请找制片核对任务状态，不能带“返修”Tag publish下游：\n'+', '.join(t['content'] for t in uncompleted_tasks)
        else:
            return ""

    def run_check(self):

        try:
            msg = ""
            if self.dialog.version_tag ==  u"制作":
                msg = self.__check_ds()
            elif self.dialog.version_tag ==  u"返修":
                msg = self.__check_retake()

            return msg

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


