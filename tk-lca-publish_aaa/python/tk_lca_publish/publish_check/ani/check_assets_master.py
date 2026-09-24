#! -*- coding:utf-8 -*-

__author__ = 'yuke'

import maya.cmds as cmds

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产master组是否有数值"
        self.description = u"检查master组上的属性是否有数值，如果有数值就让艺术家将数值改到大环的上一层级的属性上"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        all_refnamespace = self.get_all_refnamespace()
        all_ref_master = ['{}:master'.format(i) for i in all_refnamespace]


        checks = (
            ('translate', 0.0, u'位移值'),
            ('rotate', 0.0, u'旋转值'),
            ('scale', 1.0, u'缩放值')
        )

        for master_group in all_ref_master:

            for attr, expected, label in checks:
                plug = '{0}.{1}'.format(master_group, attr)
                if not cmds.objExists(plug):
                    return u'{0} 缺少 {1} 属性， 请检查资产结构'.format(master_group, attr)

                data = cmds.getAttr(plug)


                for tup in data:
                    for v in tup:
                        if abs(v - expected) > 1e-6:
                            return u'请将{0}这个资产的master组上{1}放到大环的上一层级的组上，master组不能有数值'.format(master_group, label)

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