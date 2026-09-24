# -*- coding:utf-8 -*-

import traceback
from production.shotgun_utils.sg_updater import Updater
from proc.function_running_time import record_time

class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"rtk 状态改为 sc"
        self.description = u"rtk状态发布新版本后自动改称sc"
        self.updater = Updater(self.dialog.sg)
        return

    def has_rtk_mark(self):
        task_info = self.dialog.sg.find_one('Task', [['id', 'is', self.dialog.task['id']]], ['sg_status_list'])
        if task_info['sg_status_list'] in ['rtk']:
            return True


    @record_time(__file__)
    def proceed(self):
        try:
            if self.has_rtk_mark():
                self.updater.update_task_status(self.dialog.task, 'sc', reason=u"model 任务之前是rtk，现在新 PA 了 donwstream 版本")
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


