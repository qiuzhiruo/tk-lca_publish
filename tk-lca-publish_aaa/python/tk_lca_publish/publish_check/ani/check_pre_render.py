# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os
import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查动画预渲染。"
        self.description = u"检查镜头对应的 ./ani/output 文件夹内是否有当前版本做的预渲染。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            result = ''
            mov_path = self.dialog.l_preview_files[0]
            if '/render/' not in mov_path:
                result += u"选择的预览文件不是预渲染: " + mov_path + u', 在Shotgun镜头下也没有找到一天内有含\"不用预渲染\"内容的Note.'

            if result:
                notes = self.dialog.sg.find('Note',
                                            [['note_links', 'is', self.dialog.entity],
                                             ['created_at', 'in_last', (1, 'DAY')]],
                                            ['content', 'user.HumanUser.permission_rule_set'])
                for note in notes:
                    content = note['content']
                    if content is None:
                        continue

                    if isinstance(content, str):
                        content = content.decode('utf-8')

                    content = content.lower().replace(' ', '').replace('-', '')

                    if any(i in content for i in (u'不用预渲染', u'skipprerender'))\
                       and note['user.HumanUser.permission_rule_set'] \
                       and note['user.HumanUser.permission_rule_set']['name'] in ['Lead', 'Admin', 'Manager','Supervisor']:
                        print 'Found a note that allows skipping this check.'
                        result = ''

            return result

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


