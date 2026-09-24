#! -*- coding:utf-8 -*-
import os
import traceback
import json
import io
import maya.cmds as cmds

class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出没有动画的控制器"
        self.description = u"检查哪些没有动画的控制器，并导出没有动画的控制器"
        return

    def proceed(self):
        try:
            out_dir = os.path.join(self.dialog.version_dir, 'extra_data')


            ctrl_nodes = cmds.ls('*:*ctrl', type='transform') or []
            final_list = [c for c in ctrl_nodes if not (c.endswith('pri_ctrl') or c.endswith('sec_ctrl'))]

            unused_rig_grp = self.get_zero_value_controls(final_list)

            print len(unused_rig_grp)

            for unused_rig in unused_rig_grp[:]:
                if self.isAnimation(unused_rig):
                    unused_rig_grp.remove(unused_rig)
            print len(unused_rig_grp)

            for unused_rig in unused_rig_grp[:]:
                parent_ctrl = cmds.listRelatives(unused_rig, parent=True, fullPath=True)
                if parent_ctrl:
                    parent_ctrl = parent_ctrl[0]
                    if parent_ctrl.endswith('pri_ctrl'):
                        if parent_ctrl not in unused_rig_grp:
                            unused_rig_grp.remove(unused_rig)
                            continue
                        else:
                            grandparent_ctrl = cmds.listRelatives(parent_ctrl, parent=True, fullPath=True)
                            if grandparent_ctrl:
                                if grandparent_ctrl.endswith('sec_ctrl') and grandparent_ctrl not in unused_rig_grp:
                                    unused_rig_grp.remove(unused_rig)
                                    continue

                    elif parent_ctrl.endswith('sec_ctrl'):
                        if parent_ctrl not in unused_rig_grp:
                            unused_rig_grp.remove(unused_rig)
                            continue
            print len(unused_rig_grp)
            asset_unuseRigCtrl = {}
            for u in unused_rig_grp:
                asset_key = u.split(':')[0]
                if asset_key in asset_unuseRigCtrl:
                    asset_unuseRigCtrl[asset_key].append(u)
                else:
                    asset_unuseRigCtrl[asset_key] = [u]
            self.write_json_str(asset_unuseRigCtrl, out_dir)
        except:
            return traceback.format_exc()
        return ''

    def isAnimation(self, root, animCurveType=['animCurve', 'animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU',
                                         'animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU']):
        l_ctrl_curves = cmds.listRelatives(root, ad=True, pa=True, type='nurbsCurve') or []
        # l_ctrl_curves.append(root)
        l_anim_ctrls = [cmds.listRelatives(node, parent=True, fullPath=True)[0] for node in l_ctrl_curves if
                        cmds.listRelatives(node, parent=True)]
        l_anim_ctrls.insert(0, root)

        for node in l_anim_ctrls:
            anim = []
            for anicurvetype in animCurveType:
                temp = cmds.listConnections(node, type=anicurvetype) or []
                anim.extend(temp)
            for a in set(anim):
                # 判断一个节点是否来自引用（reference）文件。
                if cmds.referenceQuery(a, isNodeReferenced=True):
                    continue
                # 查询动画曲线上的关键帧数。
                if cmds.keyframe(a, query=True, keyframeCount=True) <= 1:
                    continue
                if not self.flat_curve(a):
                    return True
        return False

    def flat_curve(self, a):
        # 获取播放帧范围
        f_start = cmds.playbackOptions(q=True, minTime=True)
        f_end = cmds.playbackOptions(q=True, maxTime=True)

        # 获取连接到 a 的上游节点（假设只取第一个）
        parent_nodes = cmds.listConnections(a, s=False, d=True) or []
        if parent_nodes:
            parent_node = parent_nodes[0]

            # 如果该节点来自参考，并且是 chr 路径，则重新设置起始帧为首关键帧
            if cmds.referenceQuery(parent_node, isNodeReferenced=True):
                file_path = cmds.referenceQuery(parent_node, f=True, wcn=True)
                file_path = file_path.replace('\\', '/')
                if 'chr/' in file_path:
                    key_times = cmds.keyframe(a, query=True, timeChange=True)
                    if key_times:
                        f_start = key_times[0]
        # 收集所有关键帧
        key_times = cmds.keyframe(a, query=True, timeChange=True) or []
        l_frames = [f_start, f_end]

        for f in key_times:
            if f > f_start and f < f_end:
                l_frames.append(f)

        l_frames = sorted(set(l_frames))  # 去重排序

        # 计算中间帧（in-betweens）
        l_inbetweens = []
        for i in range(len(l_frames) - 1):
            mid = (l_frames[i] + l_frames[i + 1]) / 2.0
            l_inbetweens.append(mid)

        l_frames.extend(l_inbetweens)
        l_frames = sorted(set(l_frames))  # 再次排序
        return self.flat_in_range(a, l_frames)

    def flat_in_range(self, a, l_frames):
        # 获取初始时间点输出值
        v_start = cmds.getAttr(a + '.output', time=l_frames[0])
        for i in range(len(l_frames) - 1):
            v_next = cmds.getAttr(a + '.output', time=l_frames[i + 1])
            if abs(v_start - v_next) > 0.01:
                return False

        return True

    def get_zero_value_controls(self, ctrls, attrs=('translate', 'rotate'), threshold=1e-4):
        zero_ctrls = []

        for ctrl in ctrls:
            is_zero = True
            for attr in attrs:
                for axis in ['X', 'Y', 'Z']:
                    # full_attr = "{ctrl}.{attr}{axis}"
                    full_attr = "{}.{}{}".format(ctrl, attr, axis)
                    if not cmds.objExists(full_attr):
                        continue
                    value = cmds.getAttr(full_attr)
                    if abs(value) > threshold:
                        is_zero = False
                        break
                if not is_zero:
                    break
            if is_zero:
                zero_ctrls.append(ctrl)

        return zero_ctrls

    def write_json_str(self, data_dict, out_dir):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        out_path = os.path.join(out_dir, 'check_rigctrl_use.json')

        # 注意：如果 data_dict 里有 unicode，dumps 会返回 unicode
        json_text = json.dumps(data_dict, ensure_ascii=False, indent=2, sort_keys=True)

        # 用二进制写，统一成 utf-8 bytes
        if isinstance(json_text, unicode):
            json_bytes = json_text.encode('utf-8')
        else:
            # 万一返回的是 str，就当它已经是 bytes
            json_bytes = json_text

        with open(out_path, 'wb') as f:
            f.write(json_bytes)

        return out_path
    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description