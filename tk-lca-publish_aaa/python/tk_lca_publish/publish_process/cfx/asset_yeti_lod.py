# -*- coding:utf-8 -*-
__author__ = 'john'

import traceback
from pymel.core import *

LOD_POSTFIX = 'Lod'

def feedAttr(node, attr):
    if not node.hasAttr(attr):
        node.addAttr(attr, at='double')
    return node.attr(attr)

def recordLodAttr(node):
    attr_names = ['renderDensity', 'renderWidth']
    for attr_name in attr_names:
        attr = feedAttr(node, attr_name + LOD_POSTFIX)
        attr.unlock()
        attr.set(node.attr(attr_name).get())
        attr.lock()


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录 Yeti 毛发 LOD 数据"
        self.description = u"作为在 Shot 任务中自动调整 LOD 的依据"
        return

    def proceed(self):
        try:
            for yeti_node in ls(typ='pgYetiMaya'):
                recordLodAttr(yeti_node)
            return ''
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
