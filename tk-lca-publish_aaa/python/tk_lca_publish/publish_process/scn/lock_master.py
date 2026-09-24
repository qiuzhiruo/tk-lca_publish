# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"锁定 |master 节点的 transform"
        self.description = u"锁定 |master 节点的 transform"
        return

    def proceed(self):
        try:
            import pymel.core as pm
            if pm.objExists('|master'):
                n = pm.PyNode('|master')
                for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                    n.setAttr(attr, l=True)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


