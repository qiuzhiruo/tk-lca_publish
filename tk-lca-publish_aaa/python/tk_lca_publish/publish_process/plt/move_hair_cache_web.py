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

import logging
import os
import re
import shutil
import traceback


# pythonMode=0
# try:
#     from pymel.core import *
#     from pymel.mayautils import getMayaLocation
#     xgenModelPath=getMayaLocation()+'/plug-ins/xgen/scripts'
#     sys.path.append(xgenModelPath)
#     import xgenm as xg
#     import production.CacheUtils.XgenCacheExporter as xgEx
# except:
#     pythonMode = 1


#reload(xgEx)

# logxgenEx = logging.getLogger('xgenExpoter')
# hdlr = logging.FileHandler('/home/zhixiang/Desktop/xgenex.log')
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# hdlr.setFormatter(formatter)
# logxgenEx.addHandler(hdlr)
# logxgenEx.setLevel(logging.DEBUG)



def changeGuidePath(description,guideABCPath):
    pass


def exportXgen(palettes,paletteBelongTo):
    """
    export .Xgen file
    """
    palettePathDic={}
    for palette in palettes :
        palettePath=self.__basedir + paletteBelongTo[palette] +'/xgen/collections/'+palette.replace(':','_')+'/'+palette.replace(':','_')+'.xgen'
        xg.exportPalette(str(palette),str(palettePath))



def getNeedPublishAssetDescriptions(assetName):
    # RootAssets=PyNode('|assets')
    # assetType=RootAssets.getChildren()[0]
    # descrations=[]
    # if assetType=='chr':
    #     descrations=listRelatives('|assets|chr|%s:master' % assetName.replace('.',':'), c=1, ad=1, typ='xgmDescription')
    # elif assetType=='prp':
    #     descrations=listRelatives('|assets|prp|%s:master' % assetName.replace('.',':'), c=1, ad=1, typ='xgmDescription')

    descrations = listRelatives('|assets' , c=1, ad=1, typ='xgmDescription')
    return descrations


def setAuxPachesFile(ABCpath,palette):
    descShapes = listRelatives( palette, type="xgmDescription", ad=True )
    for d in range(len(descShapes)):
        descShapes[d].aiUseAuxRenderPatch.set(1)
        descShapes[d].aiAuxRenderPatch.set(ABCpath)  

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

def chmod_dir(path):
    try:
        if os.path.isdir(path):
            for root, dirnames, files in os.walk(path):
                os.chmod(root, 0o777)
                for f in files:
                    os.chmod(root + '/' + f, 0o777)
    except:
        print "Encountered Error during chmod cache files"

def web_publish( publishPath):
    replace = publishPath
    for root,dirs,files in os.walk(publishPath+'/cache'):
        for fileFullName in files:
            #fix xgen file
            if fileFullName.endswith('xgen'):
                realPath= root + '/' + fileFullName
                old_data=[]
                with open(realPath,'r') as f:
                    old_data.extend(f.readlines())
                with open(realPath,'w') as f:
                    for line in old_data:
                        lineList = line.split()
                        if len(lineList)>1:
                            if lineList[0]=='cacheFileName':
                                orient = lineList[1].split('/cache/')[0]
                                if orient.split('/')[1]=='output':
                                    line = line.replace(orient, replace)
                                f.write(line)
                            else:
                                f.write(line)
                        else:
                            f.write(line)

            #fix xml file
            if fileFullName.endswith('xml'):
                realPath= root + '/' + fileFullName
                old_data=[]
                with open(realPath,'r') as f:
                    old_data.extend(f.readlines())
                with open(realPath,'w') as f:
                    for line in old_data:
                        if len(line.split())>2:
                            if line.split()[1]=='name=\"data\"':
                                for str in line.split():
                                    if len(str.split('/'))>2:
                                        if str.split('/')[1]=='output':
                                            orient=str.split('/cache/')[0]
                                            line = line.replace(orient, replace)

                                f.write(line)
                            else:
                                f.write(line)
                        else:
                            f.write(line)


# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"移动Cache"
        self.description = u"移动所选cache目录到publish文件夹"


    def proceed(self):
        try:
            for i in range(self.dialog.w_publish_file.listWidget_cache.count()):
                dir_path = self.dialog.w_publish_file.listWidget_cache.item(i).text()
                sub_path = dir_path.split('/plt/output/')[1]
                if sub_path.endswith('/'):
                    sub_path = sub_path[:-1]
                sub_path_tokens = sub_path.split('/')
                sub_path = '/'.join(sub_path_tokens[1:])
                if not os.path.isdir(dir_path):
                    return dir_path+u'不是文件夹.'
                target_dir = self.dialog.version_dir +'/'+ sub_path
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                for f in list(set(os.listdir(dir_path))):
                    src = dir_path+'/'+f
                    dst = self.dialog.version_dir +'/'+ sub_path+ '/'+f

                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                        #os.system("cp -r -f %s %s"%(src+'/*', dst))
                    else:
                        shutil.copy2(src, dst)
                    chmod_dir(dst)
                web_publish( self.dialog.version_dir)
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description







    #
    # #----------------------------fix xgen  things ------------------------
    #             if pythonMode==0:
    #                 cache_dir=dir_path+'/cache'
    #                 assetsNames = [x[1] for x in os.walk(cache_dir)][0]
    #                 for assetsName in assetsNames :
    #                     descriptions=getNeedPublishAssetDescriptions(assetsName)
    #                     #change guide animation cache path
    #                     if descriptions:
    #                         palettes=[]
    #                         for description in descriptions:
    #                             children =listRelatives(description, p=1)[0]
    #                             pal = xg.palette(str(children))
    #                             if pal and not (  pal in palettes) :
    #                                 palettes.append(pal)
    #                         #set guides path
    #                         for description in descriptions:
    #                             if description.type() != 'transform':
    #                                 description = description.getParent()
    #                             pal = xg.palette(str(description))
    #                             xg_guides_dir = self.dialog.version_dir +'/cache/'+ assetsName +'/xgen/collections/' + pal.split(':')[-1]+'/'+description.split(':')[-1]+'/guides'
    #                             modules=xg.fxModules( str(pal), str(description))
    #                             if modules :
    #                                 for mod in modules:
    #                                     if xg.fxModuleType(str(pal), str(description),mod) =='AnimWiresFXModule':
    #                                         abcName= description.split(':')[-1]+mod+'.abc'
    #                                         abcPath = xg_guides_dir+"/"+abcName
    #                                         xg.setAttr( 'liveMode'  ,'off'    ,str(pal), str(description),mod )
    #                                         xg.setAttr("wiresFile", str(abcPath) ,str(pal), str(description), mod)
    #
    #                             useAnimation=xg.getAttr( 'useCache',str(pal), str(description),'SplinePrimitive' )
    #                             if useAnimation :
    #                                 paletteP=PyNode(pal)
    #                                 abcName= description.split(':')[-1]+'.abc'
    #                                 abcPath = xg_guides_dir+"/"+abcName
    #                                 if os.path.exists(abcPath):
    #                                     xg.setAttr( 'cacheFileName',str(abcPath)  ,str(pal), str(description),'SplinePrimitive' )
    #
    #
    #                         #export .xgen file to the exactly path
    #                         abcPath=''
    #                         for palette in palettes :
    #                             #setPathce path
    #                             xg_patches_dir = self.dialog.version_dir +'/cache/' + assetsName +'/xgen/collections/' + palette.split(':')[-1]+"/patches"
    #                             palette=PyNode(palette)
    #                             abcName=palette.split(':')[-1]+'.abc'
    #                             abcPath = xg_patches_dir+"/"+abcName
    #                             #setAuxPachesFile(abcPath,palette)
    #                             #export .xgen
    #                             palettePath    = self.dialog.version_dir  +'/cache/'+ assetsName +'/xgen/collections/'+palette.split(':')[-1]+'/'+palette.split(':')[-1]+'.xgen'
    #                             xg.exportPalette(str(palette),str(palettePath))
    #
    #
    #                         #export Main xml
    #                         for description in descriptions:
    #                             if description.type() != 'transform':
    #                                 descrName = description.getParent()
    #                             pal=xg.palette(str(children))
    #                             xg_xml_dir = self.dialog.version_dir +'/cache/' + assetsName +'/xgen/collections/'+pal.split(':')[-1]+'/'+descrName.split(':')[-1]+"/xml"
    #                             main_xgen_xml_path = os.path.join(xg_xml_dir, descrName.split(':')[-1]+'.xml')
    #                             #--------need get the true palettePath
    #                             palettePathFix = self.dialog.version_dir  +'/cache/'+ assetsName +'/xgen/collections/'+pal.split(':')[-1]+'/'+pal.split(':')[-1]+'.xgen'
    #                             xgEx.export_XG_Main_XML_multiPatch(main_xgen_xml_path,description,palettePathFix,abcPath)
    #
