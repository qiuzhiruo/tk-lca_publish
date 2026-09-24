# -*- coding: utf-8 -*-
import traceback
import maya.cmds as cmds
import sys
import re
import os

if sys.platform.startswith('win'):
    PROJ_ROOT = 'Z:/projects/'
elif sys.platform.startswith('linux'):
    PROJ_ROOT = '/mnt/proj/projects/'



class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查场景中ref是否有rig文件且是否使用rig文件"
        self.description = u"场景中的ref文件有rig文件但是并没有使用，需要使用rig文件"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def grp_is_empty(self,subgroups_of_interest):
        children = cmds.listRelatives(subgroups_of_interest,children = True) or []

        if not children:
            return True
        else:
            return False

    def asset_path_check(self,parent_group, subgroups):
        """
        获取在指定父组下的多个子组中引用的资产的路径。
        只返回一个包含 'mod' 层级且同级目录中存在 'rig' 文件夹的路径。

        :param parent_group: 父组的名称，例如 'assets'
        :param subgroups: 要检测的子组列表，例如 ['chr', 'prp']
        :return: 一个包含 'mod' 层级并且同级有 'rig' 文件夹的路径
        """
        mod_paths_with_rig = set()
        # 正则表达式，用于去除路径中的 {1} 等后缀
        remove_braces_regex = re.compile(r'\{\d+\}$')

        for subgroup in subgroups:
            # 构建子组的全路径（假设 'assets' 是顶层组）
            full_group_path = '|'.join([parent_group, subgroup])

            # 检查子组是否存在
            if not cmds.objExists(full_group_path):
                print("Group '{full_group_path}' does not exist in the scene. Skipping...")
                continue

            # 获取子组下的所有子节点（递归）
            descendants = cmds.listRelatives(full_group_path, allDescendents=True, fullPath=True) or []

            for node in descendants:
                try:
                    if cmds.referenceQuery(node, isNodeReferenced=True):
                        # 获取引用文件路径（未解析）
                        ref_file = cmds.referenceQuery(node, filename=True, unresolvedName=True)

                        # 去除路径中的 {1} 等后缀
                        clean_path = remove_braces_regex.sub('', ref_file)

                        # 查找包含 'mod' 层级的路径
                        if 'mod' in clean_path:
                            # 获取 'mod' 层级的父目录
                            mod_dir = clean_path.split('/mod/')[0] + '/mod'

                            # 检查同层级是否存在 'rig' 文件夹
                            rig_dir = os.path.join(os.path.dirname(mod_dir), 'rig')
                            if os.path.isdir(rig_dir):
                                # 如果存在 'rig' 文件夹，则将这个路径加入集合
                                mod_paths_with_rig.add(clean_path)
                except Exception as e:
                    print("Failed to process node {node}. Error: {str(e)}")
                    continue

        # 返回集合中的一个路径，如果集合为空则返回 None
        return next(iter(mod_paths_with_rig), None)




    def run_check(self):
        try:
            parent_group = 'assets'
            subgroups_of_interest = ['prp']
            if not cmds.objExists(''.join(subgroups_of_interest)):
                return ""

            single_mod_path = self.asset_path_check(parent_group, subgroups_of_interest)


            if single_mod_path:
                return u'以下资产需要替换为已有的rig资产: ' + u' '.join(single_mod_path)

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            return ''
        except:
            return traceback.format_exc()

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
