# -*- coding:utf-8 -*-
import datetime
import getpass
import os
import subprocess
import sys
import traceback
from production.translate_os_path import osPathConvert

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


def get_v000_dir(l_preview_files, proj_name, step_name, task_name):
    v000_version_dir = []
    for l_preview_file in l_preview_files:
        shot_name = os.path.basename(l_preview_file).split('.')[0]
        publish_dir = PUBLISH_ROOT + '/projects/' + proj_name.lower() + '/shot/' + shot_name[
                                                                                   :3] + '/' + shot_name + '/' + step_name + '/publish/'
        v000_dir = '.'.join([shot_name, step_name, task_name, 'v000'])
        version_dir = publish_dir + v000_dir
        v000_version_dir.append(version_dir)
    return v000_version_dir


class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在服务器上建立无版本号文件夹,在shotgun上建立版本"
        self.description = u"在服务器上建立无版本号文件夹,在shotgun上建立版本。"
        return

    def create_version(self, entity, proj, code, task, local_path, user):
        d_version = {
            'entity': entity,
            'project': proj,
            'description': 'publish auto create v000',
            'sg_version_folder': {'local_path': local_path, 'name': code,
                                  'content_type': None, 'link_type': 'local'},
            'sg_version_type': 'Daily',
            'code': code,
            'sg_task': task,
            'user': user}
        version = self.dialog.sg.create('Version', d_version)
        return version

    def create_v000_preview(self, v000_dir):
        l_preview_files = []
        if not os.path.isdir(v000_dir):
            os.makedirs(v000_dir, 0777)
            os.system('chmod 777 ' + v000_dir)

        for f in os.listdir(v000_dir):
            preview_file = os.path.join(v000_dir, f)
            if not os.path.isfile(preview_file):
                continue
            if f.split('.')[-1].lower() in ['jpg', 'jpeg', 'tif', 'tiff', 'png', 'tga']:
                l_preview_files.append(preview_file)

        if len(l_preview_files) == 0:
            l_preview_files = [__file__.split('publish_process')[0] + 'depts/default/art_shot/delete_image.jpg']

        l_preview_files.sort()

        version_name = os.path.split(v000_dir)[-1]
        preview_dir = os.path.join(v000_dir, 'preview')
        v_preview = os.path.join(preview_dir,
                                 version_name + '.' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.mov')

        mov_files = ' '.join(l_preview_files)
        cmd = '"' + self.dialog.rvio_path + '" ' + mov_files + ' -o ' + v_preview
        if sys.platform.startswith('linux'):
            cmd += ' -outparams comment="author ' + getpass.getuser() + '"'
        print('Merge mov files. ' + cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        return v_preview

    def update_v000_version(self, l_preview_files, proj_name, step_name, task_name):
        l_version_dirs = get_v000_dir(l_preview_files, proj_name, step_name, task_name)
        for l_version_dir in l_version_dirs:
            # create v000 preview file
            v_preview = self.create_v000_preview(l_version_dir)
            v_preview = v_preview.replace('/', '\\')
            self.dialog.print_log('================v_preview================', v_preview)
            if not os.path.isfile(v_preview):
                return ""

            # create and update v000 sg version
            v_path = osPathConvert(v_preview)
            v_name = v_path.split('/')[-3]
            v_info = self.dialog.sg.find_one('Version', [['code', 'is', v_name]], [])
            proj = self.dialog.sg.find_one('Project', [['name', 'is', proj_name]], [])
            shot_name = v_name.split('.')[0]
            shot_entity = self.dialog.sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]],
                                      ['type', 'code', 'id'])
            task = self.dialog.sg.find_one('Task', [['entity', 'name_is', shot_name], ['content', 'is', task_name]],
                               ['type', 'content', 'id'])
            if v_info:
                self.dialog.sg.update('Version', v_info['id'], {
                    'sg_path_to_movie': v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/').replace('/mnt/proj/',
                                                                                                 '${RV_PATHSWAP_ROOT}/').replace(
                        '/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/')})
                self.dialog.sg.upload('Version', v_info['id'], v_preview, "sg_uploaded_movie")
                self.dialog.print_log('============update old v000 version id: ', v_info['id'])

            else:
                _l_version_dir = l_version_dir.replace('/', '\\')
                v000_sg_version = self.create_version(shot_entity, proj, v_name, task, _l_version_dir, self.dialog.user)
                self.dialog.sg.update('Version', v000_sg_version['id'], {
                    'sg_path_to_movie': v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/').replace('/mnt/proj/',
                                                                                                 '${RV_PATHSWAP_ROOT}/').replace(
                        '/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/')})
                self.dialog.sg.upload('Version', v000_sg_version['id'], v_preview, "sg_uploaded_movie")
                self.dialog.print_log('================create_v000_version================')

    def proceed(self):
        try:
            proj_name = self.dialog.project['name'].lower()
            step_name = self.dialog.step['name']
            task_name = self.dialog.task['name']
            self.update_v000_version(self.dialog.l_preview_files, proj_name, step_name, task_name)
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

