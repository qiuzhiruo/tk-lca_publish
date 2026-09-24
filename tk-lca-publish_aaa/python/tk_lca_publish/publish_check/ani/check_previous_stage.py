# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.01
#
# Description: As the description shows below
#
############################################

import os
import traceback

STAGE_LIST = ['blocking', 'animation']
IGNORED_LIST = ['z', 'a20005', 'a20100', 'a20120', 'a20140', 'a20165']


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查前一个Stage是否已经通过。"
        self.description = u"检查前一个动画Stage是否已经有版本被通过（Remark为ok）。"
        self.auto_fix = False
        self.duty = u"艺术家本人和PC。"
        return


    def run_check(self):
        try:
            shot = self.dialog.entity.get('name')
            if any(shot.startswith(i) for i in IGNORED_LIST):
                return ''

            assert hasattr(self.dialog, 'version_tag')
            current = self.dialog.version_tag

            assert current in STAGE_LIST
            index = STAGE_LIST.index(current)
            if index == 0:
                tasks = self.dialog.sg.find('Task',
                                            [['entity', 'is', self.dialog.entity],
                                             ['step', 'name_is', 'ani'],
                                             ['content', 'is', 'reference'],
                                             ['sg_status_list', 'is', 'aa']])
                if tasks:
                    return ''
                else:
                    return u'该镜头的动画参考任务还没有通过，不能提交%s。' % current

            previous = STAGE_LIST[index-1]
            versions = self.dialog.sg.find('Version',
                                           [['entity', 'is', self.dialog.entity],
                                            ['sg_remark', 'is', 'ok'],
                                            ['tag_list', 'is', previous]],
                                           [])
            if not versions:
                return u'该镜头还没有通过%s的动画版本，不能提交%s。' % (previous, current)

            return ''

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


