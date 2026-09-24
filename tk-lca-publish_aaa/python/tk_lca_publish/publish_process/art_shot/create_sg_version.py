# -*- coding:utf-8 -*-
import os
import shutil
import sys
import traceback
import pprint
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

def get_version_folder(l_preview_files, proj_name, step_name):
    publish_version_dir = []
    for l_preview_file in l_preview_files:
        shot_name = os.path.basename(l_preview_file).split('.')[0]
        publish_dir = PUBLISH_ROOT + '/projects/' + proj_name.lower() + '/shot/' + shot_name[
                                                                                   :3] + '/' + shot_name + '/' + step_name + '/publish/'
        version_name = sorted(os.listdir(publish_dir))[-1]
        version_dir = publish_dir + version_name
        publish_version_dir.append(version_dir)
    return publish_version_dir


class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun上建立版本并链接到任务"
        self.description = u"在shotgun上建立版本并链接到任务"
        return

    def proceed(self):
        try:
            proj_name = self.dialog.project['name'].lower()
            step_name = self.dialog.step['name']
            task_name = self.dialog.task['name']
            d_v_type = {0: 'Daily', 1: 'Downstream'}

            l_preview = get_version_folder(self.dialog.l_preview_files, proj_name, step_name)
            for file_path in l_preview:
                remove_tmp_dir = os.path.join(file_path, 'tmp')
                if os.path.exists(remove_tmp_dir):
                    shutil.rmtree(remove_tmp_dir)
                    self.dialog.print_log('remove tmp dir.')

                local_path = osPathConvert(file_path)
                s = local_path.split('/')[-1]
                shot_name = s.split('.')[0]
                shot_entity = self.dialog.sg.find_one('Shot',
                                                      [['project', 'name_is', proj_name], ['code', 'is', shot_name]],
                                                      ['type', 'code', 'id'])
                task = self.dialog.sg.find_one('Task', [['entity', 'name_is', shot_name], ['content', 'is', task_name]],
                                               ['type', 'content', 'id'])
                version_name = local_path.split('/')[-1]
                _local_path = local_path.replace('/', '\\')
                d_version = {'project': self.dialog.project, 'entity': shot_entity,
                             'sg_task': task, 'code': version_name,
                             'description': self.dialog.description, 'user': self.dialog.user,
                             'sg_version_folder': {'local_path': _local_path, 'name': version_name,
                                                   'content_type': None, 'link_type': 'local'},
                             'sg_version_type': d_v_type[self.dialog.publish_mode],
                             'tag_list': [self.dialog.version_tag], 'created_by': self.dialog.user}
                self.dialog.print_log('d_version' + str(d_version))
                d_version_str = self.__dict_qstr2str(d_version)
                v_info = self.dialog.sg.create('Version', d_version_str)
                self.dialog.print_log('============create version====================')
                if not v_info:
                    return pprint.pformat(d_version_str)

                self.dialog.v_info = v_info

                # Link to the 'last version' field of task
                self.dialog.sg.update('Task', task['id'], {'sg_last_version': v_info})

                mov_path = os.path.join('preview', version_name + '.mov')
                v_preview = os.path.join(_local_path, mov_path.replace('/', '\\'))
                if os.path.isfile(v_preview):
                    self.dialog.sg.update('Version', self.dialog.v_info['id'], {'sg_path_to_movie': v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/').replace('/mnt/proj/', '${RV_PATHSWAP_ROOT}/').replace('/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/')})
                    self.dialog.sg.upload('Version', self.dialog.v_info['id'], v_preview, 'sg_uploaded_movie')
                    self.dialog.print_log('update version id: ', self.dialog.v_info['id'])
            return ''

        except:
            return traceback.format_exc()

    def __dict_qstr2str(self, dict_data):
        result = {}
        for k, v in dict_data.items():
            if v.__class__.__name__ == 'QString':
                result[k] = unicode(v)
            elif v.__class__.__name__ == 'list':
                new_v = []
                for vv in v:
                    if vv.__class__.__name__ == 'QString':
                        new_v.append(unicode(vv))
                    else:
                        new_v.append(vv)
                result[k] = new_v
            else:
                result[k] = v
        return result

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
