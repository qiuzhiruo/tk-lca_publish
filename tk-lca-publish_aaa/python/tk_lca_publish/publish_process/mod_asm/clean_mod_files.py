# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Proceed model publish files
#
############################################

import os
import traceback

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"清理模型文件。"
        self.description = u"将模型几何体的点相对坐标(***Shape.pnts[*].pntx, ..pnty, ..pntz )清除。"
        return


    def proceed(self):
        try:
            import pymel.core as pm
            for asset_name in self.dialog.d_assets_info.keys():
                node = self.dialog.d_assets_info[asset_name]['node']
                node_hi = pm.PyNode(node.name()+'|poly|hi')
                pm.select(node_hi, r=True)
                pm.mel.eval('newCluster " -envelope 1";')
                pm.select(node_hi, r=True)
                pm.refresh()

                l_nodes = pm.listRelatives(node_hi, type='mesh', ad=True)
                #l_nodes.extend(pm.listRelatives(node, type='nurbsCurve', ad=True))
                for n in l_nodes:
                    if n.getAttr('vertexNormal', size=True) != 0:
                        pm.polyNormalPerVertex(n, ufn=True)

                pm.select(node_hi, r=True)
                pm.delete(ch=True)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


