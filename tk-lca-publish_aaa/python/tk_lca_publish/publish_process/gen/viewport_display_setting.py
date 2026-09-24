# -*- coding:utf-8 -*-

import os
import traceback
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将视窗内容隐藏，加速导出相机"
        self.description = u"将视窗内容隐藏，加速导出相机"
        return

    def proceed(self):
        try:
            panels = pm.getPanel(visiblePanels=True)
            for p in panels:
                try:
                    pm.modelEditor(p, e=True, allObjects=0)
                except:
                    pass
            pm.refresh()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


