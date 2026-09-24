# -*- coding:utf-8 -*-

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"更新stereo任务状态，设为Art Approved"
        self.description = u"更新stereo任务状态，设为Art Approved"
        return


    def proceed(self):
        try:
            info = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name'].lower()],['entity', 'name_is', self.dialog.entity['name']], ['step', 'name_is', self.dialog.step['name']], ['content', 'is', self.dialog.task['name']]], ['sg_status_list'])
            usr = self.dialog.user_name
            if info:
                task_id = info['id']
                if 'yuedong' in usr:
                    self.dialog.sg.update('Task', task_id, {'sg_status_list':'aa'})
                #elif 'jiachang' in usr:
                #    self.dialog.sg.update('Task', task_id, {'sg_status_list':'sc'})
            print 'Print stereo task info: ', info

            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


