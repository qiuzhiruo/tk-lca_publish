# -*- coding:utf-8 -*-

import os
import traceback


def change_flo_status(sg, proj_name, shot_name):
    info = sg.find_one('Task', [['project', 'name_is', proj_name],
                                            ['entity', 'name_is', shot_name],
                                            ['content', 'is', 'final_layout']], ['sg_status_list'])
    if info:
        log = ''
        task_id = info['id']
        task_status = info['sg_status_list']
        if task_status in ['aa', 'aaa', 'da', 'sc', 'fin']:
            if 'z11' in shot_name: # 如果是 z11 ，flo 状态会变成 hld
                sg.update('Task', task_id, {'sg_status_list': 'hld'})
                log += 'flo task status was %s, changed it to hld\n' % task_status
            else:
                sg.update('Task', task_id, {'sg_status_list': 'rtk'})
                log += 'flo task status was %s, changed it to rtk\n' % task_status
        elif task_status in ['wtg', 'rdy']:
            if 'z11' in shot_name: # 如果是 z11 ，flo 状态会变成 hld
                sg.update('Task', task_id, {'sg_status_list': 'hld'})
                log += 'flo task status was %s, changed it to hld\n' % task_status
            else:
                sg.update('Task', task_id, {'sg_status_list': 'ip'})
                log += 'flo task status was %s, changed it to ip\n' % task_status
        return log
    else:
        return None



# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"animation DS publish，或在Daily是pa了相机，会触发flo任务状态改变"
        self.description = u"animation DS publish，或在Daily是pa了相机，会触发flo任务状态改变"
        return

    def write_log(self, content):
        try:
            import proc.log_publish_process as lpp;reload(lpp)
            current_file = pm.sceneName().replace('\\', '/')
            log_file = os.path.dirname(current_file) + '/publish_log/' + \
                       os.path.basename(current_file)[:-3] + '.log.txt'
            log_file = log_file.replace('//', '/')
            lpp.log(log_file, content)
        except:
            pass

    def proceed(self):
        try:
            '''
                this process should be put right after clean_scenes
            '''
            log = 'set_flo_status.py\n'
            if self.dialog.step['name'] == 'ani':
                log += change_flo_status(self.dialog.sg, self.dialog.project['name'].lower(), self.dialog.entity['name'])

            self.write_log(log)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


