# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Create a version on shotgun
#
############################################

import os
import sys
import traceback
import pprint


# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在shotgun上为子资产们建立版本"
        self.description = u"在shotgun上子资产们建立版本。"
        return

    def proceed(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                asset = self.dialog.d_assets_info[asset_name]['asset']
                task = self.dialog.d_assets_info[asset_name]['task']
                version_name = self.dialog.d_assets_info[asset_name]['version_name']

                if sys.platform.startswith('win'):
                    local_path = version_dir.replace('/', '\\') + '\\'
                else:
                    local_path = version_dir + '/'

                d_v_type = {0: 'Daily', 1: 'Downstream'}

                d_version = {'project': self.dialog.project, 'entity': asset, 'sg_task': task, 'code': version_name,
                             'description': self.dialog.description+'   [(model assembly batch publish)]', 'user': self.dialog.user,
                             'sg_version_folder': {'local_path': local_path, 'name': version_name, 'content_type': None,
                                                   'link_type': 'local'},
                             'sg_version_type': d_v_type[self.dialog.publish_mode],
                             'tag_list': [self.dialog.version_tag], 'created_by': self.dialog.user}
                d_version_str = self.__dict_qstr2str(d_version)

                v_info = self.dialog.sg.create('Version', d_version_str)

                if asset_name == self.dialog.entity['name']:
                    self.dialog.v_info = v_info

                if not v_info:
                    return pprint.pformat(d_version_str)

                self.dialog.d_assets_info[asset_name]['v_info'] = v_info

                # Set related tasks
                task_info = self.dialog.sg.find_one('Task', [['id', 'is', task['id']]], ['step'])
                l_tasks = self.dialog.sg.find('Task', [['entity', 'is', asset]], ['step'])
                l_related_tasks = [task_info]
                for task in l_tasks:
                    if not task['step']['name'] in ['art', 'mod']:
                        l_related_tasks.append(task)

                self.dialog.sg.update('Version', v_info['id'], {'sg_related_tasks': l_related_tasks})

            return ""

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
