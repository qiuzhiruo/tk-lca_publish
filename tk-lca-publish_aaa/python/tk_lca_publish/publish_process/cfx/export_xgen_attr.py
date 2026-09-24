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


try:
    from pymel.core import *
    from pymel.mayautils import getMayaLocation 
    xgenModelPath = getMayaLocation()+'/plug-ins/xgen/scripts'
    sys.path.append(xgenModelPath)
    import xgenm as xg
    import xgenm.xgGlobal as xgg
except:
    pass


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出 Xgen Attribute 文件"
        self.description = u"导出 .xgen custom attribute，xml 文件"
        return

    def proceed(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                return ''
            self.dialog.l_palettes = ls(et='xgmPalette')
            self.dialog.d_currentxgDataPathAll = {}
            self.dialog.d_xgFileNameOreint = {}

            if len(self.dialog.l_palettes)>0:
                de = xgg.DescriptionEditor

                #target folder
                assetPubFolder=self.dialog.version_dir
                xgen_attr_file = assetPubFolder+'/hair_attr.xml'
                doc = dom.Document()  
                root_node = doc.createElement('xgenAsset')
                root_node.setAttribute("name", self.dialog.entity['name'])
                root_node.setAttribute("maya_file", sceneName())
                
                #source folder
                xgprojPath = workspace( q=True, rd=True )

                for palette in self.dialog.l_palettes:
                    abcName = palette.xgFileName.get().split('.')[0]+'.abc'
                    patchFilePath = assetPubFolder + '/xgen/patchs/' + abcName
                    de.setCurrentPalette(str(palette))
                    palette_node = doc.createElement('palette')
                    palette_node.setAttribute('name', str(palette))
                    palette_node.setAttribute('patch', patchFilePath)
                    rig_pass_attr = str(palette) + '.rigPass'
                    if cmds.objExists(rig_pass_attr):
                        rig_pass = cmds.getAttr(rig_pass_attr)
                        palette_node.setAttribute('rigPass', rig_pass)
                    root_node.appendChild(palette_node)

                    attrlist_node = doc.createElement('attrList')
                    palette_node.appendChild(attrlist_node)
                    
                    pal_attrs = xg.customAttrs(str(palette))
                    for parm in pal_attrs:
                        value = de.getAttr('Palette', parm)

                        attr_node = doc.createElement('attribute')
                        attr_node.setAttribute('name', parm)
                        attr_node.setAttribute('type', 'string')
                        attr_node.setAttribute('value', value)
                        attrlist_node.appendChild(attr_node)

                    descriptions = list(xg.descriptions(str(palette)))
                    descriptions.sort()
                    for des in descriptions:
                        de.setCurrentDescription(des)

                        des_node = doc.createElement('description')
                        des_node.setAttribute('name', des)
                        palette_node.appendChild(des_node)

                        des_attrs = [attr for attr in xg.customAttrs(str(palette), des, 'RendermanRenderer') \
                            if not attr.startswith('custom__arnold_')]

                        des_attr_node = doc.createElement('attrList')
                        des_node.appendChild(des_attr_node)

                        for parm in des_attrs:
                            value = de.getAttr('RendermanRenderer', parm)

                            attr_node = doc.createElement('attribute')
                            attr_node.setAttribute('name', parm)
                            attr_node.setAttribute('type', 'string')
                            attr_node.setAttribute('value', value)
                            des_attr_node.appendChild(attr_node)

                doc.appendChild(root_node)
                f = open(xgen_attr_file, 'w')
                f.write(doc.toprettyxml(encoding='utf-8'))
                f.close()     

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
