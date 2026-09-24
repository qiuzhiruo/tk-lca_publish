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
    from production.farm_ip import LcaFarmIPManage
    from pymel.mayautils import getMayaLocation 
    xgenModelPath = getMayaLocation()+'/plug-ins/xgen/scripts'
    sys.path.append(xgenModelPath)
    import xgenm as xg
    import xgenm.XgExternalAPI as base
except:
    pass


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
        self.process_name = u"输出 Xgen 文件"
        self.description = u"导出 .xgen 文件和相关缓存，xml 文件"
        return

    def proceed(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                return ''
                
            self.dialog.l_palettes = ls(et='xgmPalette')
            self.dialog.d_currentxgDataPathAll = {}
            self.dialog.d_xgFileNameOreint = {}

            if len(self.dialog.l_palettes)>0:
                #target folder
                assetPubFolder=self.dialog.version_dir
                
                #source folder
                xgprojPath = workspace( q=True, rd=True )
                if os.path.isdir(xgprojPath+'xgen'):
                    if os.path.isdir(assetPubFolder+'/xgen'):
                        shutil.rmtree(assetPubFolder+'/xgen')

                    shutil.copytree(xgprojPath+'xgen', assetPubFolder+'/xgen')
                    print '  export xgen:', assetPubFolder+'/xgen'

                    # remove useless folder
                    for folder in os.listdir(assetPubFolder+'/xgen'):
                        if folder not in ['collections', 'mel']:
                            print ' delete useless folder: ', assetPubFolder+'/xgen/'+folder
                            shutil.rmtree(assetPubFolder+'/xgen/'+folder)
                            
                    for palette in os.listdir(assetPubFolder+'/xgen/collections'):
                        if palette not in self.dialog.l_palettes:
                            print ' delete useless folder: ', assetPubFolder+'/xgen/collections/'+palette
                            shutil.rmtree(assetPubFolder+'/xgen/collections/'+palette)

                # export xgen patch info
                xc.export_xgen_patch_info(self.dialog.l_palettes, assetPubFolder)

                l_xgen_files = []
                #3 set the xgDataPath to absolute path
                for palette in self.dialog.l_palettes:
                    currentxgDataPath = xg.getAttr( 'xgDataPath', str(palette) )
                    self.dialog.d_currentxgDataPathAll[palette] = currentxgDataPath
                    absPath = currentxgDataPath.replace('${PROJECT}', assetPubFolder+'/')
                    xg.setAttr( 'xgDataPath', str(absPath), str(palette))

                    #3.1 change the aux render patchs
                    abcName = palette.xgFileName.get().split('.')[0]
                    abcName = xg.buildFileName(palette, abcName, "") + '.abc'
                    patchFilePath = assetPubFolder + '/xgen/patchs/' + abcName
                    xc.export_XG_Patches_Abc('', '', patchFilePath, palette, None, None)
                    print '  export xgen:', patchFilePath
                    # setAuxPachesFile(patchFilePath,palette)
                    setAuxPachesRestore(palette)

                    target_xgenName = xg.buildFileName(palette, self.dialog.entity['name'], "")
                    palettePathFix = assetPubFolder +'/'+  target_xgenName+'.xgen'
                    l_xgen_files.append(palettePathFix)

                    #4 export xgen XML file
                    descriptions = []
                    for description in listRelatives( palette, type="xgmDescription", ad=True):
                        descrName = description.getParent()
                        descriptions.append(str(descrName))
                        xg_xml_dir = assetPubFolder+'/xgen/collections/'+str(palette)+'/'+str(descrName)+"/xml"
                        if os.path.isdir(xg_xml_dir):
                            shutil.rmtree(xg_xml_dir)
                        os.makedirs(xg_xml_dir)
                        main_xgen_xml_path = os.path.join(xg_xml_dir, str(descrName)+'.xml')
                        xc.export_XG_Main_XML_multiPatch(main_xgen_xml_path, description, palettePathFix, patchFilePath)
                        print '  export xgen:', main_xgen_xml_path

                    # remove useless description
                    usefull_folder = ['paintmaps','DC']
                    for description in os.listdir(assetPubFolder+'/xgen/collections/'+palette):
                        if description not in descriptions and description not in usefull_folder:
                            _remove_path = assetPubFolder+'/xgen/collections/'+palette+'/'+description
                            if os.path.isdir(_remove_path):
                                print ' delete useless folder: ', _remove_path
                                shutil.rmtree(_remove_path)
                            else:
                                # print ' delete useless folder: ', '"%s" is not a folder, skinpping...'%description
                                print ' delete useless file: ', _remove_path
                                os.remove(_remove_path)

                    #5 export xgen file.  when use exportXgenFile function xg will auto change the xgFileName parameter

                #set the 'xgProjectPath' value
                xgProjectPath_orient={}
                for palette in self.dialog.l_palettes:
                    xgProjectPath_orient[str(palette)]=base.getAttr( 'xgProjectPath', str(palette) )
                    base.setAttr( 'xgProjectPath', assetPubFolder , str(palette) )

                xc.export_XG_Palettes(self.dialog.version_dir, self.dialog.d_xgFileNameOreint, self.dialog.l_palettes)
                print '  export xgen:', ' '.join(l_xgen_files)
                for palette in self.dialog.l_palettes:
                    base.setAttr( 'xgProjectPath', xgProjectPath_orient[str(palette)] , str(palette) )

                # send export proxy job
                import production.python_job as ppj
                import production.pipeline.utils as pplu

                rendergeo_py = '{}/tools/cfx/exportXgenCurve/rendergeo.py'.format(os.getenv('LC_TOOLSET'))
                cmd = rendergeo_py + ' ' + assetPubFolder + ' ' + self.dialog.entity['name'] + ' 0.1'
                job_id = ppj.send_job('',
                    args=cmd,
                    proj=self.dialog.project['name'].upper(),
                    job_name_prefix='[Export Xgen Proxy]'+os.path.basename(assetPubFolder)+' by '+self.dialog.user_name,
                    step='CFX',
                    user=self.dialog.user_name,
                    url=LcaFarmIPManage().MASTERCACHE,
                    submitdl=True,
                    python_exe=pplu.get_dcc_launcher(proj=self.dialog.project['name'].lower(),dcc='mayapy')
                )
                if job_id == -1:
                    print 'Farm submit xgen proxy error: ', self.dialog.entity['name']
                else:
                    print 'Farm submit xgen proxy Job: ', str(job_id)                    

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

