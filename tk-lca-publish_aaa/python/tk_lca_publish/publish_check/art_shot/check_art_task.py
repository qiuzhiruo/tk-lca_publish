# -*- coding:utf-8 -*-

import traceback
import os


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查镜头是否创建Art任务(Task)。"
        self.description = u"检查镜头是否创建Art任务(Task)。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            proj_name = self.dialog.project['name'].lower()
            result = []
            for file_path in self.dialog.l_preview_files:
                shot_name = os.path.basename(file_path).split('.')[0]
                task_info = self.dialog.sg.find_one('Task',
                                        [['project', 'name_is', proj_name],
                                         ['entity', 'name_is', shot_name],
                                         ['step', 'name_is', 'art']], ['content'])
                if not task_info:
                    result.append(shot_name)
            if result:
                return u'以下镜头未在shotgun上创建Art任务，请联系制片创建。\n' + '\n'.join(result)
            else:
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
