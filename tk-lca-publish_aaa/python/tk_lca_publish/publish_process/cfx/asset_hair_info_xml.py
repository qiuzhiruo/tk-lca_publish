# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.02
#
# Description: As the description shows below
#
############################################

import pymel.core as pm
from xml.dom.minidom import Document
import traceback

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出毛发节点信息 xml 文件"
        self.description = u"输出毛发节点信息 xml 文件，对 hair publish 版本做一个总结。"
        return


    def proceed(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                return ''
            dom = Document()
            root_elem = dom.createElement('hair')
            yeti_elem = dom.createElement('Yeti')
            xgen_elem = dom.createElement('Xgen')
            dom.appendChild(root_elem)
            root_elem.appendChild(yeti_elem)
            root_elem.appendChild(xgen_elem)

            if pm.ls(type='pgYetiMaya'):
                for n in pm.listRelatives('|master|hair', type='pgYetiMaya', ad=True):
                    yeti_n_elem = dom.createElement('pgYetiMaya')
                    yeti_n_elem.setAttribute('name', n.nodeName())
                    yeti_elem.appendChild(yeti_n_elem)
            else:
                print "no yeti.."

            if pm.ls(type='xgmPalette'):
                for n1 in pm.listRelatives('|master|hair', type='xgmPalette', ad=True):
                    xgmp_elem = dom.createElement('xgmPalette')
                    xgmp_elem.setAttribute('name', n1.nodeName())
                    xgen_elem.appendChild(xgmp_elem)
                    for n2 in pm.listRelatives(n1, type='xgmDescription', ad=True):
                        xgmd_elem = dom.createElement('xgmDescription')
                        l_pathe_names = [t.nodeName() for t in pm.listRelatives(n2.getParent(), type='xgmSubdPatch', ad=True)]
                        l_g = pm.listRelatives(n2.getParent(), type='xgmSplineGuide', ad=True)
                        l_c = pm.listRelatives(n2.getParent(), type='nurbsCurve', ad=True)
                        xgmd_elem.setAttribute('name', n2.nodeName())
                        xgmd_elem.setAttribute('pathes', ','.join(l_pathe_names))
                        xgmd_elem.setAttribute('xgmSplineGuides', str(len(l_g)))
                        xgmd_elem.setAttribute('curves', str(len(l_c)))
                        xgmp_elem.appendChild(xgmd_elem)

            pretty_text = dom.toprettyxml(indent = '    ', newl = '')
            final_text = pretty_text.replace('        ', '    ')
            final_text = final_text.replace('>    <', '>\n    <')
            final_text = final_text.replace('><', '>\n<')
            f = open(self.dialog.version_dir +'/hair_info.xml', 'w')
            f.write(final_text)
            f.close()
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

