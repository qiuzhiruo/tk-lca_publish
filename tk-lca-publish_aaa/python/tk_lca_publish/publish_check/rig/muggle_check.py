# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset geometry hierarchy
#
############################################

import traceback
import maya.cmds as cmds
import os
import json
import ast
from production.shotgun_connection import Connection
sg = Connection('get_project_info').get_sg()

def get_proj_id(project):
    proj = sg.find_one('Project', [['name', 'is', project]])
    return proj['id']

def get_asset_id(project, rig_id, version):
    proj_entity = sg.find_one("Project", [['name', 'is', project.upper()]], ['name'])
    filters = [
        ['project', 'is', proj_entity],
        ['step', 'is', {'id': 11, 'name': 'rig', 'type': 'Step'}],
        ['content', 'is', 'rigging_muggle_B'],
        ['entity.Asset.code', 'is', rig_id]
    ]
    asset_entity = sg.find_one("Task", filters, ['entity']).get("entity")
    asset_id = asset_entity.get("id")
    return asset_id

def get_asset_tasks(assetID, asset_ct):
    task_fields = [
        "id",
        "content",
        "sg_status_list",
        "task_assignees"
    ]
    tasks = sg.find(
        "Task",
        filters=[["entity", "is", {"type": "Asset", "id": assetID}]],
        fields=task_fields
    )
    if asset_ct == '' or asset_ct == 'tech':
        filtered_tasks = [task for task in tasks if task.get("content") == "rigging_muggle_B"]
    elif asset_ct == 'lite':
        filtered_tasks = [task for task in tasks if task.get("content") == "rigging_lite_muggle_B"]
    elif asset_ct == 'blocking':
        filtered_tasks = [task for task in tasks if task.get("content") == "rigging_blocking_muggle_B"]
    elif asset_ct == 'layout':
        filtered_tasks = [task for task in tasks if task.get("content") == "rigging_layout_muggle_B"]
    else:
        filtered_tasks = [task for task in tasks if task.get("content") == "rigging_muggle_B"]

    if filtered_tasks:
        target_task = filtered_tasks[0]  # 获取第一个匹配项
        print(target_task)
    return target_task

def update_sg_description(task_ID, new_description):
    sg.update(
        'Task',
        task_ID,
        {'sg_description': new_description}
    )

def get_sg_description(task_ID):
    task_with_description = sg.find_one(
        'Task',
        [['id', 'is', task_ID]],
        ['content', 'sg_description']  # Fields to retrieve
    )
    return task_with_description['sg_description']

def normalize_version(version):
    if isinstance(version, (int, long)):
        return "v{:03d}".format(version)
    if isinstance(version, basestring):
        if version.startswith('v'):
            num_part = version[1:]
            if num_part.isdigit():
                return "v{:03d}".format(int(num_part))
        elif version.isdigit():
            return "v{:03d}".format(int(version))
    return version

def get_convert_state(self):
    rig_id = self._ui.chrNameQL.text()  # 'td_test_aces_chr'
    proj = self._ui.projectQL.text()  # 'SGL'
    asset_ct = self._ui.chrTypeQL.text()  # 'tech'
    version = normalize_version(self._ui.chrVersionQL.text())  # 'v001'
    if asset_ct == 'tech':
        asset_ct = ''
    try:
        projectID = get_proj_id(proj)
        assetID = get_asset_id(proj, rig_id, version)
        muggleB_task = get_asset_tasks(assetID, asset_ct)

        data_dict_string = get_sg_description(muggleB_task['id'])
        if not data_dict_string:
            data_dict = {}
            convert_status = True
        else:
            data_dict = ast.literal_eval(data_dict_string)
            convert_status = data_dict['convertStatus']
    except:
        convert_status = True
    return convert_status

def delete_world_vis_attr_from_all_dag():
    # 获取所有 DAG 节点（完整路径，避免重名问题）
    dag_nodes = cmds.ls(dag=True, long=True)

    for node in dag_nodes:
        # 检查 visco 属性是否存在
        if cmds.attributeQuery('worldVisibility', node=node, exists=True):
            try:
                # 如果属性被锁定，先解锁
                if cmds.getAttr(node + '.worldVisibility', lock=True):
                    cmds.setAttr(node + '.worldVisibility', lock=False)

                # 删除自定义属性
                cmds.deleteAttr(node, attribute='worldVisibility')
                print('Deleted .worldVisibility from: %s' % node)

            except Exception as e:
                pass

def normal_path(input_path):
    cur_path = os.path.normpath(input_path)
    cur_path = cur_path.replace("\\", "/")
    return cur_path
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查muggle check"
        self.description = u"检查muggle check"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        # listdirTemp = cmds.file(q=True, sn=True)
        # listdir = normal_path(listdirTemp)
        # if '/prp/' in listdir:
        #     return ""
        # elif '/crd/' in listdir:
        #     return ""
        # elif '/asb/' in listdir:
        #     return ""
        # elif '/asm/' in listdir:
        #     return ""
        # elif 'layout' in listdir:
        #     return ""
        # elif 'rra' in listdir:
        #     return ""
        # elif 'msc' in listdir:
        #     return ""

        asset_ct = self.dialog.asset_type
        ignored_asset_ct_list = ['/asb/','/asm/','/crd/','/efx/','/env/','/flg/','/msc/','/prp/','/rra/','/scn/','/veh/']
        if "/" + asset_ct + "/" in ignored_asset_ct_list:
            return ""

        # get project, version, chr_id
        asset_name = self.dialog.entity['name'].lower()
        if self.dialog.entity.has_key('sg_chinese'):
            asset_chinese_name = self.dialog.entity['sg_chinese']
        task_name = self.dialog.task['name'].lower() # asset_ct = self.dialog.asset_type
        proj = self.dialog.project['name'].lower()
        projInfo = self.dialog.project['name'].upper()
        vers = self.dialog.version_name
        version = int(vers.split('.')[-1][1:])
        version_info = str(vers.split('.')[-1])

        if task_name == 'rigging':
            asset_ct = ''
        elif task_name == 'rigging_blocking':
            asset_ct = 'blocking'
        elif task_name == 'rigging_lite':
            asset_ct = 'lite'
        elif task_name == 'rigging_box':
            asset_ct = 'box'
        elif task_name == 'rigging_layout':
            asset_ct = 'layout'
        else:
            return ""

        try: # 获取是否可以转换的状态
            projectID = get_proj_id(proj)
            assetID = get_asset_id(proj, asset_name, version)
            muggleB_task = get_asset_tasks(assetID, asset_ct)
            print('198assetct:', asset_ct, muggleB_task)
            data_dict_string = get_sg_description(muggleB_task['id'])

            if not data_dict_string:
                data_dict = {}
                convert_status = True
            else:
                data_dict = ast.literal_eval(data_dict_string)
                convert_status = data_dict['convertStatus']

            if convert_status == False:
                return ""
        except:
            print('fail to find convertStatus')

        if not cmds.attributeQuery("muggle_check", node="master", exists=True):
            return "please use muggle checker first"
        else:
            if cmds.getAttr("master.muggle_check"):
                delete_world_vis_attr_from_all_dag()
                return ""
            else:
                return "please check muggle checker problems"

    def run_fix(self):
        '''Auto Fix'''
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty