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
import ast
import json
import sys
from production.shotgun_connection import Connection
import getpass

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

def normal_path(input_path):
    cur_path = os.path.normpath(input_path)
    cur_path = cur_path.replace("\\", "/")
    return cur_path

class StdProcess():

    def __init__(self, dialog=None):
        self.dialog = dialog
        self.process_name = u"提交文件至muggle服务器"
        self.description = u"提交文件至muggle服务器"
        return

    def proceed(self):
        #localPath = "G:/MuggleD"

        # ignore all asset types except 'chr'
        asset_ct = self.dialog.asset_type
        ignored_asset_ct_list = ['/asb/','/asm/','/crd/','/efx/','/env/','/flg/','/msc/','/prp/','/rra/','/scn/','/veh/']
        # listdirTemp = cmds.file(q=True, sn=True)
        # listdir = normal_path(listdirTemp)
        # for ignored_asset_ct in ignored_asset_ct_list:
        #     if ignored_asset_ct in listdir:
        #         return ""
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

        if not asset_ct == '':
            asset_ct = ' -ct ' + str(asset_ct)
            asset_ct_info = '_' + str(asset_ct)
        else:
            asset_ct_info = ''
        try:
            libPath = 'U:/toolset/lib'
            rigSyspath = sys.path
            if libPath in rigSyspath:
                pass
            else:
                sys.path.append(libPath)
            user_name = getpass.getuser()
        except:
            user_name = 'rig_department'
        import production.python_job as ppj  # -ct lite
        ppj.send_job(r"G:\MuggleD\MuggleRigX\muggleD_pipeline\mcm.py",
                     args="-p {} -r {} -v {}{}".format(proj, asset_name, str(version), asset_ct),
                     proj='{}'.format(proj),
                     user='{}'.format(user_name),
                     pools='muggle',
                     priority=3000,
                     step='ple',
                     output_list=[],  # 需要解除权限的路径放进去  '/mnt/work/shome/wangqi2/test'
                     job_name_prefix="RIGGING_task_{}_{}_{}{}".format(projInfo, asset_name, version_info, asset_ct_info),
                     error_to_failed_count=1,
                     python_exe=r'C:\Python27\python.exe')
        return ""

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
