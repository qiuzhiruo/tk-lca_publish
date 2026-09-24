# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: guan ze jie
#
# Date: 2023.09
#
############################################

import os
import traceback
import shutil
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝贴图文件到服务器上版本文件夹"
        self.description = u"拷贝贴图文件到服务器上版本文件夹。"
        return

    # 获取材质publish文件的版本，如果没有就返回空
    def get_srf_version(self):
        proj = self.dialog.project['name'].lower()
        asset_name = self.dialog.entity['name']
        asset_name_version = self.dialog.sg.find_one('Asset',
                                                     [['project', 'name_is', proj], ['code', 'is', asset_name]],
                                                     ['code', 'assets', "sg_versions_2"])
        srf_version = []
        for asset in asset_name_version['sg_versions_2']:
            if "srf.surfacing.v" in asset["name"] and "srf.surfacing.v000" not in asset["name"]:
                srf_version.append(asset["name"])
        return srf_version

    # 获取所有的贴图文件和节点  return[[节点名，文件路径]，[节点名1，文件路径1]]
    def get_tex(self):
        pm.mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
        path_list = []
        texture_list = cmds.ls(type="file")
        for tex_file in texture_list:
            file_path = cmds.getAttr(tex_file + ".fileTextureName")
            path_list.append([tex_file, file_path])
        return path_list

    def proceed(self):
        try:
            # 如果没找到贴图或者材质版本已经存在直接跳过
            task_name = self.dialog.task['name']
            tex_path = self.get_tex()
            srf_version = self.get_srf_version()
            if not srf_version:
                # if task_name != 'hair':
                return ''
            if not tex_path:
                return ''

            # 创建文件夹
            tex_file_path = self.dialog.version_dir + "/tex"
            if not os.path.isdir(tex_file_path):
                os.makedirs(tex_file_path)
                os.chmod(tex_file_path, 0777)

            #   复制贴图并修改maya文件里的贴图路径
            print tex_file_path

            for tex in tex_path:
                print tex
                if os.path.isfile(tex[1]):
                    new_path = os.path.join(tex_file_path, os.path.basename(tex[1]))
                    if tex[1].replace('\\', '/') != new_path.replace('\\', '/'):
                        shutil.copy(tex[1], new_path)
                    cmds.setAttr(tex[0]+".fileTextureName", new_path, type="string")
            return ''

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


