# -*- coding:utf-8 -*-

import os
import traceback
import shutil
import pymel.core as pm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝flo文件生成stereo版本"
        self.description = u"拷贝flo文件生成stereo版本"
        return

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

    def findLatestVersion(self, filename):
        if not os.path.isfile(filename):
            return filename
        old_version = os.path.basename(filename).split('.')[-2]
        new_version = 'v' + format(int(old_version[1:]) + 1, '03d')
        new_filename = os.path.join(os.path.dirname(filename),
                                    os.path.basename(filename).replace(old_version, new_version))
        return self.findLatestVersion(new_filename)

    def proceed(self):
        try:
            log = 'copy_to_stereo.py\n'

            info = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name'].lower()],
                                                    ['entity', 'name_is', self.dialog.entity['name']],
                                                    ['content', 'is', 'stereo']],
                                           ['sg_status_list'])
            need_copy_to_stereo = True
            if info:
                task_status = info['sg_status_list']
                if task_status == 'omt':
                    # omitted stereo task, ignore
                    log += 'stereo status is omit, no need to copy ma file to stereo\n'
                    need_copy_to_stereo = False

            if need_copy_to_stereo:
                scene_name = os.path.basename(str(pm.sceneName()))
                log += 'scene name: ' + scene_name + '\n'
                path = os.path.dirname(str(pm.sceneName())).replace('\\', '/')
                log += 'path: ' + path + '\n'
                if not path.endswith('/'):
                    path = path + '/'

                stereo_file = self.findLatestVersion(path + scene_name.replace('final_layout', 'stereo'))
                log += 'stereo file: ' + stereo_file + '\n'

                if not os.path.isfile(stereo_file):
                    shutil.copyfile(str(pm.sceneName()), stereo_file)
                    log += 'copy file from ' + str(pm.sceneName()) + ' to ' + stereo_file + '\n'

            self.write_log(log)

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
