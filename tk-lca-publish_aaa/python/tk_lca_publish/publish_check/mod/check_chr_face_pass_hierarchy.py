# -*- coding:utf-8 -*-

########################################################################################
#
# Author: liangyue
#
# Date: 2026.06
#
# Description: 检查三级角色资产模型Pass层级结构与命名规范。
#
########################################################################################
import pymel.core as pm
import maya.cmds as cmds
import traceback
import re
from proc.function_running_time import record_time
from proc.get_versions import get_task_versions

class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查三级角色资产模型Pass层级结构与命名规范。"
        self.description = u"规范验证 face_pass_grp、cloth_pass_grp、hair_pass_grp pass下的组命名。" \
                           u"精确校验脸部Mesh前后缀、头发Mesh前缀，衣服Mesh不校验。" \
                           u"没有毛发可以加tag： skip_no_hair 跳过" \
                           u"\n https://rcn8f1ebg7ch.feishu.cn/wiki/KzgjwKVNxiQNKZkSIR9c255hnJo?fromScene=spaceOverview"
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

            # check face_pass_grp  skip tag: skip face_pass_grp
            face_pass_grp = "|master|shape|face_pass_grp"
            if pm.objExists(face_pass_grp):
                if 'skip_face_pass_grp' in asset_info['tag_list']:
                    return ''

                if str(asset_info.get('sg_diffculty2')) not in ['3'] or asset_info.get(
                        'sg_asset_type') != 'chr':
                    rig_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'rig')
                    cfx_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'cfx')
                    print('had cfx_versions--0->', len(cfx_versions))
                    if not rig_versions and not cfx_versions:
                        return '目前只有三级变脸角色需要加 |master|shape|face_pass_grp 组,当前资产不需要, rig 和cfx当前无发布版本\n' \
                               '如果需要跳过，组长判断后加tag 跳过： skip_face_pass_grp'

                all_first_children = cmds.listRelatives(face_pass_grp, children=True, type='transform',
                                                      fullPath=True) or []
                if len(all_first_children) <= 1:
                    rig_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'rig')
                    print('had rig_versions-->', len(rig_versions))
                    if not rig_versions:
                        cfx_versions = get_task_versions(self.dialog.project['name'].upper(), asset_name, 'cfx')
                        print('had cfx_versions--->', len(cfx_versions))
                        if not cfx_versions:
                            return ''
                    return '当前资产只有一套 face pass 请删掉|master|shape|face_pass_grp 组，毛发应该放在 |master|shape|to_cfx|hair_grp 组下 \n ' \
                           'rig 和cfx已经有版本，需要组长判断后加tag 跳过： skip_face_pass_grp'

            # 目前 变脸只在xun项目
            if self.dialog.project['name'].lower() in ['lic']:
                return ''

            print('tag_list--->>>', asset_info['tag_list'])
            if asset_info['tag_list'] and 'skip_face_pass' in asset_info['tag_list']:
                return ""

            if str(asset_info.get('sg_diffculty2')) not in ['3'] or asset_info.get('sg_asset_type') != 'chr':
                return ''
            if not pm.objExists(face_pass_grp):
                return ''

            # ------------------------------------------------------------------
            # 配置与基础参数定义
            # ------------------------------------------------------------------
            face_pass_grp = "|master|shape|face_pass_grp"
            cloth_pass_grp = "|master|poly|hi|mesh_grp|cloth_grp"
            hair_pass_grp = '|master|shape|to_cfx|hair_grp|head_hair'

            if pm.objExists(face_pass_grp):
                if not pm.objExists(hair_pass_grp):
                    if asset_info['tag_list'] and 'skip_no_hair' in asset_info['tag_list']:
                        return ''
                    return '当前变脸角色的头发需要放在 |master|shape|to_cfx|hair_grp|head_hair 组下, 当前场景没有该组'

            # mod leader 想要限制 cloth_pass_grp
            if not cmds.objExists(cloth_pass_grp):
                if asset_info['tag_list'] and 'skip_cloth_pass' in asset_info['tag_list']:
                    return ""
                else:
                    return '当前角色没有 |master|poly|hi|mesh_grp|cloth_grp 这个组，请把衣服放在下面， 如果没有衣服请找组长加tags：skip_cloth_pass 跳过 '

            # 统一后缀
            suffix = "_grp"

            # 各通道特定的前缀配置
            pipe_configs = {
                face_pass_grp: {
                    "prefix": "face_",
                    "default_grp": "face_default_grp",
                    "label": "脸部pass"
                },
                cloth_pass_grp: {
                    "prefix": "CLT_",
                    "default_grp": "CLT_default_grp",
                    "label": "衣服pass"
                },
                hair_pass_grp: {
                    "prefix": "hair_",
                    "default_grp": "hair_default_grp",
                    "label": "头发pass"
                }
            }

            errors = []
            active_pipes = [pipe for pipe in pipe_configs.keys() if cmds.objExists(pipe)]

            if not active_pipes:
                return ''

            # ------------------------------------------------------------------
            # 1. 重名冲突全局排查
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
            # Helper: 分pass针对性校验 子 Mesh 的规范
            # ------------------------------------------------------------------
            def check_pipe_meshes(current_node, current_grp_title, pipe_type, required_suffix=""):
                local_shapes = cmds.listRelatives(current_node, allDescendents=True, type='mesh', fullPath=True) or []
                if not local_shapes:
                    return

                local_mesh_transforms = list(
                    set([cmds.listRelatives(s, parent=True, fullPath=True)[0] for s in local_shapes]))

                for m_path in local_mesh_transforms:
                    m_name = m_path.split("|")[-1]

                    # A. 脸部pass Mesh 规范：前缀 body_/shell_，后缀严格匹配
                    if pipe_type == face_pass_grp:
                        allowed_face_prefixes = ("body_", "shell_", 'jewelry_')
                        if not m_name.startswith(allowed_face_prefixes):
                            errors.append(
                                "模型前缀错误：脸部组 '{}' 内部的模型 '{}' 必须以 'body_' 或 'shell_' 或 'jewelry_'开头。".format(current_grp_title,
                                                                                               m_name))
                        if not m_name.endswith(required_suffix):
                            errors.append("模型后缀错误：脸部组 '{}' 内部的模型 '{}' 必须以 '{}' 结尾。".format(current_grp_title, m_name,
                                                                                           required_suffix))

                    # B. 头发pass Mesh 规范：只需要 shell_ 开头，不检查后缀
                    elif pipe_type == hair_pass_grp:
                        if not m_name.startswith("shell_"):
                            errors.append(
                                "模型前缀错误：头发组 '{}' 内部的模型 '{}' 必须以 'shell_' 开头。".format(current_grp_title, m_name))

                    # C. 衣服pass Mesh 规范：根据要求，cloth_pass_grp 下面完全不检查 mesh 命名
                    elif pipe_type == cloth_pass_grp:
                        pass

            # ------------------------------------------------------------------
            # 2. 核心主循环：按pass相互独立验证组结构
            # ------------------------------------------------------------------
            for pipe_path in active_pipes:
                cfg = pipe_configs[pipe_path]
                p_prefix = cfg["prefix"]
                p_default_grp = cfg["default_grp"]
                p_label = cfg["label"]

                # 获取当前pass一级的直接变换节点
                all_first_children = cmds.listRelatives(pipe_path, children=True, type='transform', fullPath=True) or []

                # 【核心修改点】过滤出一级节点中纯 Group 类型的节点（排除直接放置的 Mesh）
                children = []
                for child in all_first_children:
                    # if not (child.split("|")[-1].endswith("_grp") and child.split("|")[-1].startswith(p_prefix)):
                    if not child.split("|")[-1].endswith("_grp"):
                        continue
                    children.append(child)

                if not children:
                    errors.append("结构错误：{} '{}' 下未发现任何规范的子组层级。".format(p_label, pipe_path))
                    continue

                child_names = [path.split("|")[-1] for path in children]

                # 验证当前pass下，必须存在带有默认标识的组
                has_default = False
                for c_name in child_names:
                    if c_name == p_default_grp or c_name.endswith("_default_grp"):
                        has_default = True
                        break

                if not has_default:
                    errors.append("结构错误：{} '{}' 下缺少必需的默认组（如含有 'default_grp' 字段的组）。".format(p_label, pipe_path))

                # 遍历一级子组进行二级深度规范匹配
                for child_path in children:
                    child_name = child_path.split("|")[-1]

                    # 验证一级子组的合法命名规则（必须符合 各自前缀_xxx_grp 或者是 默认组）
                    is_valid_grp_name = False
                    desc_part = ""

                    if child_name.endswith(suffix) and child_name.startswith(p_prefix):
                        # 剥离前后缀提取描述名部分
                        desc_part = child_name[len(p_prefix): -len(suffix)]
                        if desc_part:
                            is_valid_grp_name = True

                    if not is_valid_grp_name:
                        errors.append(
                            "命名错误：{}下的组 '{}' 不符合 '{}{{描述名}}{}' 的规范,如果是共用的组，不要以 _grp为后缀。".format(p_label, child_name, p_prefix, suffix))
                        continue

                    # 动态定义当前大组下所有嵌套 Mesh 必须遵循的后缀
                    if "default" in desc_part.lower():
                        required_mesh_suffix = "_default"
                    else:
                        required_mesh_suffix = "_{}".format(desc_part)

                        # ----------------------------------------------------------
                        # 3. 特殊规则处理：针对脸部pass的胡子组层级进行校验
                        # ----------------------------------------------------------
                        if pipe_path == face_pass_grp:
                            expected_face_hair_name = "{}{}_face_hair".format(p_prefix, desc_part)
                            expected_face_hair_path = "{}|{}".format(child_path, expected_face_hair_name)

                            # 精准校验：只有当该胡子组真实存在时，才穿透检查其内部子组
                            if cmds.objExists(expected_face_hair_path):
                                hair_children = cmds.listRelatives(expected_face_hair_path, children=True,
                                                                   fullPath=True) or []
                                hair_child_names = [hc.split("|")[-1] for hc in hair_children]

                                expected_up_grp = "{}{}_up_grp".format(p_prefix, desc_part)
                                expected_dw_grp = "{}{}_dw_grp".format(p_prefix, desc_part)

                                # 两者都不在的时候才报错（即只要有一个在，就不报错）
                                if (expected_up_grp not in hair_child_names) and (
                                        expected_dw_grp not in hair_child_names):
                                    errors.append(
                                        "特殊层级错误：胡子组 '{}' 下必须包含 '{}' 或 '{}' 至少一个子组。".format(
                                            expected_face_hair_name, expected_up_grp, expected_dw_grp
                                        )
                                    )

                    # ----------------------------------------------------------
                    # 4. 校验该大组下的所有 Mesh
                    # ----------------------------------------------------------
                    check_pipe_meshes(child_path, child_name, pipe_path, required_mesh_suffix)

            # ------------------------------------------------------------------
            # 5. 返回msg
            # ------------------------------------------------------------------
            if errors:
                max_display = 12
                dialog_msg = "检查未通过！\n组长判断后加tag: skip_face_pass 可以跳过。\n 共发现 {} 处结构/命名错误：\n\n".format(len(errors))
                dialog_msg += "\n".join(errors[:max_display])
                if len(errors) > max_display:
                    dialog_msg += "\n\n......等更多错误，请查看后台 Script Editor 输出。"

                print("\n" + "=" * 30 + " 详细错误清单 " + "=" * 30)
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


'''
# 配置与基础参数定义
face_pass_grp = "|master|shape|face_pass_grp"
cloth_pass_grp = "|master|poly|hi|mesh_grp|cloth_grp"
hair_pass_grp = '|master|shape|to_cfx|hair_grp|head_hair'

check_grp_list = [face_pass_grp, cloth_pass_grp, hair_pass_grp] # 这些组如果有，而且默认组"default_grp"为后缀的组必须有， 就检查下面的组，必须按照规定前后坠，比如cloth_pass_grp前缀 cloth_pass_prefix...， 后缀都是suffix


suffix = "_grp"
cloth_pass_prefix = 'CLT_'
face_pass_prefix = "face_"
hair_pass_prefix = 'hair_'
default_grp_name = "default_grp"


# 检查check_grp_list 下所有的 mesh（第归）只有face_pass_grp下可以有 body_ 开头，其他组mesh都必须 shell_ 开头


#face_pass_grp 比较特殊的部分， 比如face_default_grp 下面如果有face_default_face_hair 下就必须是face_default_up_grp， face_default_dw_grp（_dw_grp或者_up_grp结尾的组）face_a_grp以及其它也以此类推

'''
