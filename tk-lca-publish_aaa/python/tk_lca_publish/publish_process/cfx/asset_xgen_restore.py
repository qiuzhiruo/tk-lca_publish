# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Zhixiang
#
# Date: 
#
# Description: As the description shows below
#
#
############################################

import os
import shutil
import traceback

import xml.dom.minidom as dom
from pymel.core import *

try:
    import production.CacheUtils.XgenTranslater  as trans
    import production.CacheUtils.XgenCacheExporter  as xc
    from pymel.mayautils import getMayaLocation 
    xgenModelPath = getMayaLocation()+'/plug-ins/xgen/scripts'
    sys.path.append(xgenModelPath)
    import xgenm as xg
except:
    pass

#import production.shotgun_connection as sgc

def setAuxPachesFile(ABCpath,palette):
    descShapes = listRelatives( palette, type="xgmDescription", ad=True )

    for d in range(len(descShapes)):
        descShapes[d].aiUseAuxRenderPatch.set(1)
        descShapes[d].aiAuxRenderPatch.set(ABCpath)  

def setAuxPachesRestore(palette):
    descShapes = listRelatives( palette, type="xgmDescription", ad=True )
    for d in range(len(descShapes)):    
        descShapes[d].aiUseAuxRenderPatch.set(0)
        descShapes[d].aiAuxRenderPatch.set('')



# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"恢复 xgen 节点出 Cache 前的设置"
        self.description = u"恢复 xgen 节点出 Cache 前的设置。"
        return


    def proceed(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                return ''
                
            self.dialog.l_palettes = ls(et='xgmPalette')
            if len(self.dialog.l_palettes)>0:
                #6 restore the resolation path
                for palette in self.dialog.l_palettes:
                    #restore oreint name
                    palette.xgFileName.set(self.dialog.d_xgFileNameOreint[palette])
                    xg.setAttr('xgDataPath', self.dialog.d_currentxgDataPathAll[palette], str(palette) )
                    #setAuxPachesRestore(palette)

            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

