# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil
import pymel.core as pm

import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )
import tagsInFrustum as tifr
reload(tifr)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"标记相机可视范围内的物体"
        self.description = u"标记相机可视范围内的物体，传递给xml文件"
        return

    def proceed(self):
        try:
            if not pm.objExists('|assets'):
                return ""

            # tag lca_visible attribute on musters in view
            tagObj = tifr.TagsInFrustum()
            masters = tagObj.getObjectInFrustum()
            if masters:
                tagObj.tagMasters(masters)
            else:
                print 'TagsInFrustum.getObjectInFrustum(): failed to get masters in camera view, ignored!'

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


