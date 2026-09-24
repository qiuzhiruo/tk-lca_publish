# -*- coding:utf-8 -*-

import os
import traceback
# import shutil
import pymel.core as pm

import lay.lca_camera_lock.functions as functions_cl

reload(functions_cl)

import production.lca_xmpp as lca_xmpp

reload(lca_xmpp)

import stereo.findStereoCamera as fsc

reload(fsc)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"animation, final_layout downstream publish会触发stereo任务状态改变"
        self.description = u"animation, final_layout downstream publish会触发stereo任务状态改变"
        return

    def osPathConvert(self, path):
        path = path.replace('\\', '/')
        if os.name == 'nt':
            if path.startswith('/mnt/proj/'):
                return path.replace('/mnt/proj/', 'Z:/')
            elif path.startswith('/mnt/work/'):
                return path.replace('/mnt/work/', 'W:/')
            elif path.startswith('/output/'):
                return path.replace('/output/', 'O:/')
            elif path.startswith('/mnt/utility/'):
                return path.replace('/mnt/utility/', 'U:/')
            elif path.startswith('/mnt/public/'):
                return path.replace('/mnt/public/', 'P:/')
            elif path.startswith('/mnt/usr/'):
                return path.replace('/mnt/usr/', 'C:/Program Files/')
            else:
                return path
        else:
            if path.startswith('Z:/'):
                return path.replace('Z:/', '/mnt/proj/')
            elif path.startswith('W:/'):
                return path.replace('W:/', '/mnt/work/')
            elif path.startswith('O:/'):
                return path.replace('O:/', '/output/')
            elif path.startswith('U:/'):
                return path.replace('U:/', '/mnt/utility/')
            elif path.startswith('P:/'):
                return path.replace('P:/', '/mnt/public/')
            elif path.startswith('C:/Program Files/'):
                return path.replace('C:/Program Files/', '/mnt/usr/')
            else:
                return path

    def write_log(self, content):
        try:
            import proc.log_publish_process as lpp
            reload(lpp)
            current_file = pm.sceneName().replace('\\', '/')
            log_file = os.path.dirname(current_file) + '/publish_log/' + os.path.basename(current_file)[
                                                                         :-3] + '.log.txt'
            log_file = log_file.replace('//', '/')
            lpp.log(log_file, content)
        except:
            pass

    def proceed(self):
        try:
            '''
                this process should be put right after clean_scenes
            '''
            log = 'set_stereo_status.py\n'

            stereo_cam_path = self.osPathConvert(
                str(fsc.findStereoCamera(self.dialog.entity['name'], self.dialog.project['name'].lower())))
            status = False
            if self.dialog.step['name'] == 'flo':
                status = True
                log += 'step is flo, need to change the stereo status\n'
            elif self.dialog.step['name'] == 'ani' and not functions_cl.is_camera_locked() and os.path.isfile(
                    stereo_cam_path):
                status = True
                log += 'step is ani, but camera is unlocked, stereo camera exists also, need to change the stereo status\n'

            if not status:
                log += 'No need to change stereo status\n'
            else:
                info = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name'].lower()],
                                                        ['entity', 'name_is', self.dialog.entity['name']],
                                                        ['content', 'is', 'stereo']],
                                               ['sg_status_list'])
                if info:
                    task_id = info['id']
                    task_status = info['sg_status_list']
                    # if task_status=='aa' or task_status=='aaa' or task_status=='da' or task_status=='fin' or task_status=='rtk':
                    if task_status == 'omt':
                        # omitted stereo task, ignore
                        log += 'stereo status is omit, no need to change the status\n'
                    else:
                        # change status
                        if self.dialog.step['name'] in ['flo', 'ani']:
                            if task_status in ['aa', 'aaa', 'da', 'rtk', 'sc'] and hasattr(self.dialog, 'cam_dir'):
                                if self.dialog.cam_dir:
                                    self.dialog.sg.update('Task', task_id, {'sg_status_list': 'rtk'})
                                    log += 'changed stereo status to rtk\n'

                        # send message
                        try:
                            pidgin = lca_xmpp.Sender()
                            message = self.dialog.project['name'].lower() + ' ' + self.dialog.entity[
                                'name'] + ': stereo status was changed to ip, due to publish of final_layout.'
                            for usr in ['jiachang']:
                                pidgin.send(usr, message)
                            log += 'sent pidgin message to stereo dept successfully\n'
                        except:
                            print traceback.format_exc()
                            log += 'failed to send pidgin message\n' + traceback.format_exc() + '\n'

            self.write_log(log)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
