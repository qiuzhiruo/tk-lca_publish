# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os, shutil
import traceback
import production.CacheUtils.XgenTranslater  as trans
from pymel.core import *
import xml.dom.minidom as dom


def set_output_format():
    """
        setup the global output settings.
    """
    cmds = '''
        source setMayaSoftwareFrameExt.mel;
        setMayaSoftwareFrameExt(3,0);
        setAttr "defaultRenderGlobals.extensionPadding" 4;
    '''
    mm.eval(cmds)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出xgenXmlfile"
        self.description = u"输出毛发xgenXmlfile供srf组使用。"
        return
    def proceed(self):
        try:
            xgmDescDagPath= ls(et='xgmDescription')
            for xgmDes in xgmDescDagPath:
                partname = xgmDes.name().split('|')[-1]
                xmlPath=self.dialog.version_dir +'/xgen/xml/'
                if os.path.isdir(xmlPath):
                    shutil.rmtree(xmlPath)
                os.makedirs(xmlPath)
                path = xmlPath+partname+'.xml'
                #metadata
                           
                doc = dom.Document()   
                procedrualArray = []
                procedrualArray=trans.getTheXgenProceduralData(xgmDes)
                for pro in procedrualArray:    
                    root_node = doc.createElement('description')
                    root_node.setAttribute("name", xgmDes.name())
                    attrs = vars(pro)
                    for k,v in attrs.items():
                        child = doc.createElement('data')
                        child.setAttribute("name", k)
                        if type(v) .__name__  == 'list':
                            child.setAttribute("value", str(v).strip('[]'))
                        else:
                            child.setAttribute("value", str(v))
                        root_node.appendChild(child)
                    doc.appendChild(root_node)

                f = open(path, 'w')
                f.write(doc.toprettyxml(encoding='utf-8'))
                f.close()
                print  "________________________XGEN__paramater___________________________"
                for pro in procedrualArray:
                    attrs = vars(pro)
                    print ', \n'.join("%s: %s" % item for item in attrs.items())
                print  "________________________XGEN__paramater____________________________"
                
            return ''
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


