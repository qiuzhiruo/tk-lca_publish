# -*- coding:utf-8 -*-

import os
import sys
import re
import glob
import shutil
import traceback

import maya.cmds as cmds
import pymel.core as pm
import maya.app.general.fileTexturePathResolver as ftpr
import maya.mel as mel

from proc.function_running_time import record_time


class StdProcess:

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发布贴图"
        self.description = u"将贴图发布到work盘和proj盘"
        return

    def get_obj(self, node):

        if not isinstance(node, list):
            node = [node]
        for i in node:
            if pm.objectType(i) == u'shadingEngine':
                objects = i.dagSetMembers.connections()
                return [obj.name() for obj in objects]
            if i.outputs():
                return self.get_obj(i.outputs())

    def copy_texture(self, tex_path, target_dir):
        """
        复制普通贴图或 UDIM 贴图。
        Args:
            tex_path (str): fileTextureName
            target_dir (str): 目标目录
        Returns:
            list: 实际复制后的目标文件
        """
        copied_files = []
        tex_path = tex_path.replace('\\', '/')
        # UDIM
        if '<UDIM>' in tex_path or '<udim>' in tex_path:
            pattern = (tex_path.replace('<UDIM>', '*').replace('<udim>', '*'))
            source_files = glob.glob(pattern)
        else:
            source_files = [tex_path]
        for src_file in source_files:
            if not os.path.isfile(src_file):
                continue
            file_name = os.path.basename(src_file).replace(' ', '')
            dst_file = os.path.join(target_dir, file_name)
            if os.path.isfile(dst_file):
                src_size = os.path.getsize(src_file)
                dst_size = os.path.getsize(dst_file)
                # 大小相同，不需要重新复制
                if src_size == dst_size:
                    copied_files.append(dst_file)
                    continue

            # 不存在 / 文件大小不同
            shutil.copyfile(
                src_file,
                dst_file
            )

            copied_files.append(dst_file)

        return copied_files

    def copy_all_tex(self, asset_name):

        version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
        asset_type = self.dialog.d_assets_info[asset_name]['type']
        maya_tex_path = os.path.join(version_dir, 'images', 'tex_low')

        work_tex_dir = os.path.join('/mnt/work/projects/', self.dialog.project['name'].lower(), 'asset', asset_type, asset_name, 'mod', 'task', 'images', 'tex_low')
        if sys.platform.startswith('win'):
            work_tex_dir = os.path.join('W:/projects/', self.dialog.project['name'].lower(), 'asset', asset_type, asset_name,'mod', 'task', 'images', 'tex_low')

        if not os.path.exists(work_tex_dir):
            os.makedirs(work_tex_dir, 0o777)
        if not os.path.exists(maya_tex_path):
            os.makedirs(maya_tex_path, 0o777)

        for file_node in pm.ls(typ='file'):
            tex_path = pm.getAttr(file_node + '.fileTextureName')
            if tex_path.startswith('Z') or tex_path.startswith('/mnt/proj') or '/srf/' in tex_path.replace('\\', '/'):
                continue

            # chinese
            # pattern = re.compile(u'[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f]')
            new_tex_name = os.path.basename(tex_path).replace(' ', '')
            # if pattern.findall(os.path.basename(tex_path)) or str('?') in str(os.path.basename(tex_path)):
            #     shape_objs = [i.replace('|', '_') for i in self.get_obj(file_node)]
            #     if shape_objs:
            #         if pattern.findall(os.path.basename(tex_path)) or str('?') in str(new_tex_name):
            #             new_tex_name = '_'.join(shape_objs) + '.' + os.path.basename(tex_path).split('.')[-1]
            #     else:
            #         continue

            # tar_tex_file = os.path.join(maya_tex_path, new_tex_name)
            work_tex_file = os.path.join(work_tex_dir, new_tex_name)
            try:
                # if new_tex_name not in os.listdir(work_tex_dir):
                    # shutil.copyfile(tex_path, work_tex_file)
                work_texs = self.copy_texture(tex_path, work_tex_dir)
                # if new_tex_name not in os.listdir(maya_tex_path):
                    # shutil.copyfile(tex_path, tar_tex_file)
                maya_texs = self.copy_texture(tex_path, maya_tex_path)
                pm.setAttr(file_node + '.fileTextureName', work_tex_file)

                # fresh
                if not cmds.about(batch=True):
                    cmds.select(cmds.ls(type="mesh"))
                    cmds.displaySmoothness(divisionsU=0, divisionsV=0, pointsWire=4, pointsShaded=1, polygonObject=1)
                    cmds.select(cl=True)
            except Exception as e:
                traceback.print_exc()

    @record_time(__file__)
    def proceed(self):
        try:
            mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
            for asset_name in self.dialog.d_assets_info.keys():
                self.copy_all_tex(asset_name)
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
