#! -*- coding:utf-8 -*-

__author__ = 'yuke'

import maya.cmds as cmds

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查z33镜头里的资产大环是否被key帧"
        self.description = u"检查z33镜头里的资产大环组上的属性是否被key帧、约束或者被锁定"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        current_file = cmds.file(query=True, sceneName=True)
        if '/z33' not in current_file:
            return ''
        all_refnamespace = self.get_all_refnamespace()
        print(all_refnamespace)
        all_ref_global_ctrl = ['{}:global_ctrl'.format(i) for i in all_refnamespace]
        for global_ctrl in all_ref_global_ctrl:
            if not cmds.objExists(global_ctrl):
                continue
            transform_attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

            for attr in transform_attrs:
                full_attr = "{0}.{1}".format(global_ctrl, attr)
                key_count = cmds.keyframe(full_attr, query=True, keyframeCount=True) or 0
                connections = cmds.listConnections(full_attr, type="animCurve") or []
                is_locked = cmds.getAttr(full_attr, lock=True)

                if key_count > 0 or connections or is_locked:
                    return u'{0}这个大环被key帧 或者被约束 或者属性被锁住了, 请解决一下'.format(global_ctrl)


        return ''

    def get_all_refnamespace(self):
        allRefNodes_ = cmds.ls(rf=1)
        allrfnamespace = []
        for ref in allRefNodes_:
            try:
                is_loaded = cmds.referenceQuery(ref, isLoaded=1)
            except:
                continue
            if is_loaded:
                file_path = cmds.referenceQuery(ref, f=True)
                rf_namespace = cmds.referenceQuery(ref, ns=True)
                if '/cam/' in file_path:
                    continue
                if '/rig/' in file_path:
                    allrfnamespace.append(rf_namespace)
                if '/mod/' in file_path:
                    allrfnamespace.append(rf_namespace)

        return allrfnamespace



    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty