# -*- coding: utf-8 -*-

import maya.cmds as cmds


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产的控制器缩放值是否存在0"
        self.description = u"不允许可以控制缩放的控制器数值有0.0这样的数值存在"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        ctrl_list = cmds.ls("*_ctrl", type='transform', r=True)
        ero_msg = []
        for ctrl in ctrl_list:
            if not cmds.listRelatives(ctrl, s=True, type='nurbsCurve'):
                continue
            for axis in ['scaleX', 'scaleY', 'scaleZ']:
                full_attr = ctrl + '.' + axis
                ani_curves = cmds.listConnections(full_attr, type='animCurve', s=True, d=False)
                if ani_curves:
                    anim_node = ani_curves[0]
                    all_values = cmds.keyframe(anim_node, query=True, valueChange=True)
                    if 0.0 in all_values:
                        times = cmds.keyframe(anim_node, query=True, timeChange=True)
                        valuse = cmds.keyframe(anim_node, query=True, valueChange=True)
                        for i in range(len(valuse)):
                            val = valuse[i]
                            if abs(val) < 0.001:
                                frame = times[i]
                                msg = u'控制器： %s 的属性： %s 在第 %s 帧 数值为： %s' % (ctrl, axis, frame, val)
                                ero_msg.append(msg)
                else:
                    if cmds.getAttr(full_attr, k=True) and (not cmds.getAttr(full_attr, lock=True)):
                        scale_value = cmds.getAttr(full_attr)
                        if abs(scale_value) < 0.001:
                            msg = u'控制器： %s 的属性： %s  数值为： %s' % (ctrl, axis, scale_value)
                            ero_msg.append(msg)
        if ero_msg:
            return '\n'.join(ero_msg)
        else:
            return ''

    def run_fix(self):
        return self.run_fix

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
