# -*- coding:utf-8 -*-

import os
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"锁定当前asb资产下的所有env资产的transform属性"
        self.description = u"锁定当前asb资产下的所有env资产的transform属性，避免动画误操作导致位置改变"
        return

    def proceed(self):
        try:
            import maya.cmds as mc

            lock_attr=['translate', 'rotate', 'scale']
            all_ar_nodes = mc.listRelatives('|master|asb', c=1, ad=True, type='assemblyReference')

            for ar in all_ar_nodes:
                if ar.split(':')[0].endswith('_asb'):
                    continue
                path = mc.getAttr('{}.definition'.format(ar)).replace('\\', '/')
                if 'env' not in path.split('/'):
                    continue
                for attr in lock_attr:
                    mc.setAttr('{}.{}'.format(ar, attr), lock=1)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



