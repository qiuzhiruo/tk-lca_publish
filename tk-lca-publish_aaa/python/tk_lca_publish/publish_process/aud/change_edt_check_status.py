# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import subprocess
import os
import sys

#import get_wav_abc as gwa

# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将镜头的edt_check状态改为aa"
        self.description = u"Downstream时，若镜头状态为ip，自动将镜头的edt_check状态改为aa"
        return
    
    def proceed(self):
        #if just normal audio task, do not need to convert anything
        try:
            self.task_name=self.dialog.version_dir.split('.')[-2]
            if self.task_name == 'audio':
                new_names=[]
                for wav_file in self.dialog.wav_files:
                    shot_name = os.path.basename(wav_file).rsplit('.',1)[0]
                    edt_check_status = self.dialog.sg.find_one('Task', 
                                                               [['project','name_is', self.dialog.project['name']], 
                                                                ['entity', 'name_is', shot_name], 
                                                                ['content', 'is', 'edt_check']], 
                                                               ['id', 'sg_status_list'])
                    if not edt_check_status:
                        return shot_name + ' do not have edt_check task.'
                    
                    if edt_check_status['sg_status_list'] == 'ip':
                        self.dialog.sg.update('Task', edt_check_status['id'], {'sg_status_list': 'aa'})
                        self.dialog.print_log(u'修改 %s edt_check任务状态为aa' % shot_name)
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


if __name__ == '__main__':
    dialog = Fake_Dialog()
    stdProcess = StdProcess(dialog)
    stdProcess.proceed()
    print 'Done'
    
    
