# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import pymel.core as pm

import sys
# sys.path.append('/mnt/utility/toolset/tools/gene/scene_operator')
# sys.path.append('U:/toolset/tools/gene/scene_operator')
toolset = os.getenv('LC_TOOLSET')
sys.path.append('%s/tools/gene/scene_operator' % toolset)
import sceneOperator as scnOp
reload(scnOp)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"存储global_ctrl的位置"
        self.description = u"存储global_ctrl的位置信息到自定义属性内，用于下游的比对。"
        return

    def proceed(self):
        try:
            if not pm.objExists('|scene'):
                return 'Failed to find group: |scene'

            sceneOp = scnOp.Scene()

            masters = []
            for g in ['|scene|scn_asb', '|scene|scn_env', '|scene|scn_prp', '|scene|scn_veh']:
                if pm.objExists(g):
                    masters.extend( sceneOp.getMasters(top=g) )

            for m in masters:
                sceneOp.addExtraTransformAttr(m.name())

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


