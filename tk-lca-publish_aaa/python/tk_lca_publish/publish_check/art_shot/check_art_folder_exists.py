# -*- coding:utf-8 -*-

import traceback
import os
import sys

if sys.platform.startswith('win'):
    # WORK_ROOT = 'W:'
    OUTPUT_ROOT = 'O:'
    PUBLISH_ROOT = 'Z:'
    # TOOL_ROOT = 'U:'
elif sys.platform.startswith('linux'):
    # WORK_ROOT = '/mnt/work'
    OUTPUT_ROOT = '/output'
    PUBLISH_ROOT = '/mnt/proj'
    # TOOL_ROOT = '/mnt/utility'

WORK_ROOT = os.getenv('LC_WORK')
TOOL_ROOT = os.getenv('LC_UTILITY')

class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Art任务(Task)的publish文件夹是否建立。"
        self.description = u"检查Art任务(Task)的publish文件夹是否建立。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            proj_name = self.dialog.project['name'].lower()
            step_name = self.dialog.step['name']
            result = []
            for file_path in self.dialog.l_preview_files:
                shot_name = os.path.basename(file_path).split('.')[0]
                publish_dir = PUBLISH_ROOT + '/projects/' + proj_name + '/shot/' + shot_name[
                                                                                           :3] + '/' + shot_name + '/' + step_name + '/publish/'
                if not os.path.isdir(publish_dir):
                    result.append(publish_dir)
            if result:
                return u'以下镜头Publish文件夹没有建立,请联系制片创建。\n' + '\n'.join(result)
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
