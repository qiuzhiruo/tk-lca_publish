# -*- coding:utf-8 -*-

import os
import getpass
import re
import traceback

import pymel.core as pm

import xml.etree.ElementTree as ET

from production.notification_rules import recipients
from production import shotgun_connection
from proc.function_running_time import record_time


sg = shotgun_connection.Connection('get_project_info').get_sg()


class MG:

    @staticmethod
    def get_topology_info(xml_file):
        topology_info = {}
        root = ET.parse(xml_file)
        mesh_elements = root.findall('.//mesh')
        for mesh_element in mesh_elements:
            topology_info.update({mesh_element.get('name'): mesh_element.get('topology')})
        return topology_info

    @staticmethod
    def get_recipients():
        recipients_list = []
        user_api = recipients.TaskRecipients()
        recipients_list.extend(user_api.get_dept_lead('srf'))
        recipients_list.extend(user_api.get_dept_lead('cfx'))
        recipients_list.extend(user_api.get_dept_pc('ani'))
        recipients_list.extend(user_api.get_dept_pc('srf'))
        recipients_list.extend(user_api.get_dept_pc('cfx'))
        recipients_list.append(getpass.getuser())
        recipients_list = [sg.find_one('HumanUser', [['login', 'is', name]], []) for name in recipients_list]

        return recipients_list


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发送模型拓补信息"
        self.description = u"如果模型拓补信息发生变化就note给相关人员"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            scene_name = pm.sceneName()
            asset_name = os.path.basename(scene_name).split('.')[0]
            version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
            current_mesh_xml = os.path.join(version_dir, 'mesh.xml')
            pre_version = int(self.get_pre_version(asset_name))

            if not pre_version:
                return ''

            pre_version_format = version_dir.replace(version_dir[-3:], '{:03}')
            pre_version_dir = pre_version_format.format(pre_version)
            pre_mesh_xml = os.path.join(pre_version_dir, 'mesh.xml')
            pre_topology_values = MG.get_topology_info(pre_mesh_xml)
            cur_topology_values = MG.get_topology_info(current_mesh_xml)

            if pre_topology_values == cur_topology_values:
                return ''

            msg = u'{}相校于上一版(v{:03}):\n'.format(asset_name, pre_version)
            change_topology = []
            cur_lost_shape = []

            for shape, topology in pre_topology_values.items():
                if shape in cur_topology_values:
                    if topology != cur_topology_values.get(shape):
                        change_topology.append(shape)
                else:
                    cur_lost_shape.append(shape)

            cur_extra_shape = list(set(list(cur_topology_values.keys())) - set(list(pre_topology_values.keys())))

            if change_topology:
                msg += u'这些shape的拓补发生了变化:\n{}\n'.format('\n'.join(change_topology))
            if cur_lost_shape:
                msg += u'少了这些shape:\n{}\n'.format('\n'.join(cur_lost_shape))
            if cur_extra_shape:
                msg += u'多了这些shape:\n{}\n'.format('\n'.join(cur_extra_shape))

            self.send_node(msg)

            return ''
        except Exception as e:
            print(traceback.format_exc())
            return ''

    def send_node(self, content):
        user = sg.find_one('HumanUser', [['login', 'is', 'aokang']], [])
        recipients_list = MG.get_recipients()
        print('recipients_list============>', recipients_list)
        note_info = {'project': self.dialog.project,
                     'content': content,
                     'addressings_to': recipients_list,
                     'sg_note_type': u'通知',
                     'user': user}
        note_id = sg.create('Note', note_info)

    def get_pre_version(self, asset_name):
        version_number = []
        current_version = self.dialog.d_assets_info[asset_name]['version_dir']
        for version in os.listdir(os.path.dirname(current_version)):
            if re.search(r'v(\d\d\d)$', version):
                version_number.append(re.search(r'v(\d\d\d)$', version).group(1))
        version_number.sort()
        if len(version_number) > 1:
            pre_version = version_number[-2]
        else:
            pre_version = None
        return pre_version

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
