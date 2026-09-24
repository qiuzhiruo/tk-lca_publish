# -*- coding:utf-8 -*-

########################################################################################
#
# Author: liangyue
#
# Date: 2026.06
#
# Description: 纯净版：仅对衣服(cloth)和头发(hair)pass的组层级与命名进行规范验证，不检查Mesh。
#
########################################################################################
import os
import json
import re
import string
import pymel.core as pm
import maya.cmds as cmds
import traceback

from proc.function_running_time import record_time


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查fur pass层级结构与命名规范。"
        self.description = u"检查fur pass层级结构与命名规范。\n 具体规范请参考： \n https://rcn8f1ebg7ch.feishu.cn/wiki/U1Ivwo57Ji1PijkjQ2McZuazn0g?fromScene=spaceOverview"
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
            asset_name = self.dialog.entity.get('name')
            asset_info = self.dialog.sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name'].lower()],
                                                           ['code', 'is', asset_name]],
                                                 ['sg_diffculty2', 'sg_asset_type', 'tag_list'])

            tag_list = asset_info.get("tag_list", [])
            crd_face_pass = '|master|shape|crd_face_pass_grp'

            # 仅针对 wuk 项目
            if self.dialog.project['name'].lower() in ['lic']:
                return ''
            # crd_变脸资产，制片必须标注 ‘crd_face_pass’的tags
            if not tag_list or 'fur_pass' not in tag_list:
                return ''

            # 因为 模型会发一版本给 rig 的文件，里面没有变脸，这个文件可以不创建crd_face_pass_grp组，rig工具肯定会出crd_face_pass_grp组
            # if not cmds.objExists(crd_face_pass):
            #     return ''
                # return '当前crd资产制片标注了tag:crd_long_hair，是变脸crd资产 \n 请确保变脸模型放在 |master|shape|crd_face_pass_grp组下'

            # 有 长辫子需求的必须标注 ‘crd_long_hair’的tags
            if tag_list and 'crd_long_hair' in tag_list:
                if not cmds.objExists('|master|poly|hi|mesh_grp|hair_grp|head_hair|hair_long_grp'):
                    return '当前crd资产制片标注了tag:crd_long_hair，是长辫子资产，' \
                           '\n请确保长辫子放在 |master|poly|hi|mesh_grp|hair_grp|head_hair|hair_long_grp组下'

                hair_root = '|master|poly|hi|mesh_grp|hair_grp|head_hair'
                hair_long_grps = [
                    grp for grp in cmds.listRelatives(hair_root, c=True, type='transform', fullPath=True) or []
                    if re.match(r'.*\|hair_long_[a-z]+_grp$', grp)
                ]
                if not hair_long_grps:
                    pm.confirmDialog(title=u"提示 ！！！", message=u'当前crd资产制片标注了tag:crd_long_hair，是长辫子资产，请确保除了hair_long_grp 别的长辫子组命名为： hair_long_a/b/c_grp！！！', bgc=[1, 0.6, 0.4])

            # ------------------------------------------------------------------
            # 2. 基础配置与阻断检查
            # ------------------------------------------------------------------
            cloth_pass_grp = "|master|poly|hi|mesh_grp|cloth_grp"
            hair_pass_grp = '|master|shape|to_cfx|hair_grp|head_hair'
            suffix = "_grp"
            errors = []
            if not cmds.objExists(cloth_pass_grp):
                return ''
            if not cmds.objExists(hair_pass_grp):
                return '请确保{}组存在'.format(hair_pass_grp)
            hair_pass_default_grp = '{}|hair_default_grp'.format(hair_pass_grp)
            if not cmds.objExists(hair_pass_default_grp):
                return '请确保{}组存在'.format(hair_pass_default_grp)
            # 各通道特定的前缀配置
            pipe_configs = {
                cloth_pass_grp: {
                    "prefix": "CLT_",
                    "default_grp": "CLT_default_grp",
                    "label": "衣服pass"
                }
            }

            active_pipes = [pipe for pipe in pipe_configs.keys() if cmds.objExists(pipe)]
            if not active_pipes:
                return ''

            # ------------------------------------------------------------------
            # 3. 重名冲突全局排查 (仅限衣服和头发层级内部)
            # ------------------------------------------------------------------
            all_nodes_to_check = []
            for pipe in active_pipes:
                all_nodes_to_check.append(pipe)
                descendents = cmds.listRelatives(pipe, allDescendents=True, fullPath=True) or []
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
                    duplicate_errors.append("重名冲突：场景中存在同名节点 '{}'，分别位于：\n  - {}".format(name, "\n  - ".join(paths)))

            if duplicate_errors:
                return "检测到层级内有重名节点，请先修正：\n\n" + "\n".join(duplicate_errors[:5])

            # ------------------------------------------------------------------
            # 4. pass结构与二级子组命名验证 (无 Mesh 检查)
            # ------------------------------------------------------------------
            for pipe_path in active_pipes:
                cfg = pipe_configs[pipe_path]
                p_prefix = cfg["prefix"]
                p_default_grp = cfg["default_grp"]
                p_label = cfg["label"]

                # 获取当前pass一级的直接变换节点
                all_first_children = cmds.listRelatives(pipe_path, children=True, type='transform', fullPath=True) or []

                # 过滤出一级节点中纯带有 _grp 后缀的组类型节点（安全忽略直接放置在目录下的 Mesh）
                children = [child for child in all_first_children if child.endswith("_grp")]

                if not children:
                    errors.append("结构错误：{} '{}' 下未发现任何_grp后缀的子组层级。".format(p_label, pipe_path))
                    continue

                child_names = [path.split("|")[-1] for path in children]

                # 验证必须存在默认组 (如 CLT_default_grp 或 hair_default_grp，或以其结尾的组)
                has_default = False
                for c_name in child_names:
                    if c_name == p_default_grp or c_name.endswith("_default_grp"):
                        has_default = True
                        # hair pass 的 _default_grp 组不能有 long 字段（ rig要求的）
                        if c_name.startswith("hair_") and 'long' in c_name:
                            return 'rig要求 hair pass 的 _default_grp 组不能有 long 字段,请修改组名字：{}'.format(c_name)
                        break

                if not has_default:
                    errors.append("结构错误：{} '{}' 下缺少必需的默认组（如含有 'default_grp' 字段的组）。".format(p_label, pipe_path))

                # 遍历一级子组验证命名规则
                for child_path in children:
                    child_name = child_path.split("|")[-1]

                    # 验证一级子组的合法命名规则（必须符合 前缀_描述名_grp 规范）
                    is_valid_grp_name = False
                    if child_name.endswith(suffix) and child_name.startswith(p_prefix):
                        desc_part = child_name[len(p_prefix): -len(suffix)]
                        if desc_part:
                            is_valid_grp_name = True

                    if not is_valid_grp_name:
                        errors.append(
                            "命名错误：{}下的组 '{}' 不符合 '{}{{描述名}}{}' 的规范。".format(p_label, child_name, p_prefix, suffix))

                    # 注意：彻底移除了 check_pipe_meshes，不对衣服和头发内部的 Mesh 进行任何校验。

            # ------------------------------------------------------------------
            # 5. 汇总并返回错误报告
            # ------------------------------------------------------------------
            if errors:
                max_display = 12
                dialog_msg = "检查未通过！\n组长判断后加tag: skip_cloth_pass 可以跳过。\n 共发现 {} 处结构/命名错误：\n\n".format(len(errors))
                dialog_msg += "\n".join(errors[:max_display])

                if len(errors) > max_display:
                    dialog_msg += "\n\n......等更多错误，请查看后台 Script Editor 输出。"

                print("\n" + "=" * 30 + " 衣服/头发pass独立检查详细错误清单 " + "=" * 30)
                for err in errors:
                    print(err)
                print("=" * 88 + "\n")

                return dialog_msg

            # check |master|shape|crd_face_pass_grp
            # if 'skip_crd_face_pass' in tag_list:
            #     return ''
            suffix_error_list = []
            mesh_error_list = []
            no_isalpha_list = []
            if not cmds.objExists(crd_face_pass):
                return ''
                # result = pm.confirmBox(
                #     title='警告',
                #     message='请确保有变脸的 fur_pass 资产 需要建组{}!! \n 是否继续进行后面检查?'.format(crd_face_pass),
                #     button=['是', '否'],  # 自定义按钮文字
                #     defaultButton='是',  # 默认高亮的按钮
                #     cancelButton='否'  # 点击 X 等同于哪个按钮
                # )
                #
                # if result == '是':
                #     return ''
            face_children = cmds.listRelatives(crd_face_pass, children=True, type='transform') or []
            print('---face_children-->>', face_children)
            for fc in face_children:
                if fc.endswith("_grp") and fc.startswith("face_"):
                    fc_suffix = fc[len('face_'): -len('_grp')]
                    print('--fc_suffix--->', fc_suffix)
                    if fc_suffix not in string.ascii_letters:  # 'abc...zABC...Z'
                        no_isalpha_list.append(fc)
                    for fc_child in cmds.listRelatives(fc, children=True, type='transform') or []:
                        if fc_child.endswith('_grp'):
                            continue
                        if not fc_child.endswith(fc_suffix):
                            suffix_error_list.append('{}的命名应该以 _{}结尾'.format(fc_child, fc_suffix))
                            continue

                        check_mesh_name = re.sub(r'^facial_|_{}$'.format(fc_suffix), '', fc_child)
                        if not cmds.objExists(check_mesh_name):
                            mesh_error_list.append('{}的母体：{}不存在'.format(fc_child, check_mesh_name))

            if no_isalpha_list:
                return "以下mesh 的命名错误, 命名规范： face_{a/b/c...}_grp" + "\n".join(no_isalpha_list)
            if suffix_error_list:
                return "以下mesh 的命名错误, 组长判断后加tag: skip_crd_face_pass 可以跳过：" + "\n".join(suffix_error_list)
            if mesh_error_list:
                if 'skip_crd_face_pass' not in tag_list:
                    return "以下mesh 的母体mesh不存在, 组长判断后加tag: skip_crd_face_pass 可以跳过：" + "\n".join(mesh_error_list)
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
