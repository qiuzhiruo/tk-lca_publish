# -*- coding:utf-8 -*-

########################################################################################
#
# Author: liangyue
#
# Date: 2026.06
#
# Description: 对衣服 cloth_pass_grp 层级结构与组命名进行规范验证。
#
########################################################################################
import os
import json
import pymel.core as pm
import maya.cmds as cmds
import traceback

import re
from proc.function_running_time import record_time
from proc.get_versions import get_task_versions

class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查1，2, 3级角色资产模型衣服管道层级结构与命名规范。"
        self.description = u"规范验证 cloth_pass_grp 下的组命名。skip_tag: skip_cloth_pass。由于绑定想要规范文件，是绑定对模型的要求"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        """
        check function
        @return: str (错误信息，如果通过则返回空字符串 '')
        """
        try:
            # 基础资产过滤
            asset_name = self.dialog.entity.get('name')
            asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()],
                                                           ['code', 'is', asset_name]],
                                                 ['sg_diffculty2', 'sg_asset_type', 'tag_list'])

            # 目前 变脸/衣服层级检查仅针对 xun 项目
            if self.dialog.project['name'].lower() in ['lic']:
                return ''

            if str(asset_info.get('sg_diffculty2')) not in ['1', '2', '3'] or asset_info.get('sg_asset_type') != 'chr':
                return ''
            tag_list = asset_info['tag_list']

            # 之前做过的不改层级了
            rig_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'rig')
            print('had rig_versions-0->', len(rig_versions))
            if not rig_versions:
                cfx_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'cfx')
                print('had cfx_versions--0->', len(cfx_versions))
                if cfx_versions:
                    return ''
            else:
                return ''

            # ------------------------------------------------------------------
            # 配置与基础参数定义
            # ------------------------------------------------------------------
            cloth_pass_grp = "|master|poly|hi|mesh_grp|cloth_grp"
            suffix = "_grp"
            errors = []
            if tag_list and 'skip_cloth_pass' in tag_list:
                return ""
            # 变脸crd 为了复用 原来三级角色 cfx文件
            if tag_list and 'crd_face_pass' in tag_list and asset_info.get('sg_asset_type') == 'crd':
                return ""

            # mod leader 想要限制 cloth_pass_grp 必须存在
            if not cmds.objExists(cloth_pass_grp):
                if tag_list and 'skip_cloth_pass' in tag_list:
                    return ""
                else:
                    return '当前角色没有 |master|poly|hi|mesh_grp|cloth_grp 这个组，请把衣服放在下面， 如果没有衣服请找组长加tags：skip_cloth_pass 跳过 '

            # ------------------------------------------------------------------
            # 1. 衣服内层级重名冲突全局排查
            # ------------------------------------------------------------------
            all_nodes_to_check = [cloth_pass_grp]
            descendents = cmds.listRelatives(cloth_pass_grp, allDescendents=True, fullPath=True) or []
            all_nodes_to_check.extend(descendents)

            seen_short_names = {}
            for node_path in all_nodes_to_check:
                short_name = node_path.split("|")[-1]
                if short_name in seen_short_names:
                    seen_short_names[short_name].append(node_path)
                else:
                    seen_short_names[short_name] = [node_path]

            duplicate_errors = []
            for name, paths in seen_short_names.items():
                if len(paths) > 1:
                    duplicate_errors.append("重名冲突：衣服管道内存在同名节点 '{}'，分别位于：\n  - {}".format(name, "\n  - ".join(paths)))

            if duplicate_errors:
                return "检测到衣服层级内有重名节点，请先修正：\n\n" + "\n".join(duplicate_errors[:5])

            # ------------------------------------------------------------------
            # 2. 衣服管道结构与二级子组命名验证
            # ------------------------------------------------------------------
            # 获取衣服管道一级的直接变换节点
            all_first_children = cmds.listRelatives(cloth_pass_grp, children=True, type='transform',
                                                    fullPath=True) or []

            # 过滤出一级节点中纯带有 _grp 后缀的组类型节点（安全忽略直接放置在目录下的各种 Mesh）
            children = [child for child in all_first_children if child.endswith("_grp")]

            if not children:
                errors.append("结构错误：衣服管道 '{}' 下未发现任何规范的子组层级。".format(cloth_pass_grp))
                return "检查未通过！\n 共发现 1 处结构错误：\n\n" + errors[0]

            child_names = [path.split("|")[-1] for path in children]

            # 验证必须存在默认组 CLT_default_grp 或以 _default_grp 结尾的组
            has_default = False
            for c_name in child_names:
                if c_name == "CLT_default_grp" or c_name.endswith("_default_grp"):
                    has_default = True
                    break

            if not has_default:
                errors.append("结构错误：衣服管道 '{}' 下缺少必需的默认组（如含有 'default_grp' 字段的组）。".format(cloth_pass_grp))

            # 遍历一级子组验证命名规则
            for child_path in children:
                child_name = child_path.split("|")[-1]
                # skip 共用衣服
                if child_name == 'com_grp':
                    continue

                # 二级子组必须符合 CLT_{描述名}_grp 规范
                if not (child_name.startswith("CLT_") and child_name.endswith(suffix)):
                    errors.append("命名错误：衣服管道下的组 '{}' 不符合 'CLT_{{描述名}}_grp' 的规范。".format(child_name))
                    continue

                # 注意：根据规范，衣服管道内部的 Mesh 完全不进行前缀后缀命名校验，此处直接通过。

            # ------------------------------------------------------------------
            # 3. 汇总并返回错误报告
            # ------------------------------------------------------------------
            if errors:
                max_display = 12
                dialog_msg = "检查未通过！\n组长判断后加tag: skip_cloth_pass 可以跳过。\n 共发现 {} 处结构/命名错误：\n\n".format(len(errors))
                dialog_msg += "\n".join(errors[:max_display])
                if len(errors) > max_display:
                    dialog_msg += "\n\n......等更多错误，请查看后台 Script Editor 输出。"

                print("\n" + "=" * 30 + " 衣服管道独立检查详细错误清单 " + "=" * 30)
                for err in errors:
                    print(err)
                print("=" * 88 + "\n")

                return dialog_msg

            return ""

        except Exception as e:
            return traceback.format_exc()

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
