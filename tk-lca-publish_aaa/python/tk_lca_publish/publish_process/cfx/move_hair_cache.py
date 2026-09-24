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
import sys
import sgtk
logger = sgtk.platform.get_logger(__name__)
import cfx.cfx_felt_pipeline.hair_pass_utils as hpu
import cfx.cfx_hair_pass.utils as chpu
toolset = os.getenv('LC_UTILITY')
sys.path.append('%s/linked_tools/site-packages/out_source/python/proc' % toolset)
import updater
import production.python_job as ppj
convert_usd_cache = '%s/linked_tools/usd/lcx2u/scripts/build_shot.py' % toolset
lc_py = '%s/linked_tools/lca_rez/launchers/gen/linux/lca_python' % toolset

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


def changeGuidePath(description, guideABCPath):
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


def move_hair_pass(proj, shot, publish_version_name):
    """
        move hair pass from output directory to publish directory
    :param proj: project name
    :param shot: shot code
    :param publish_version_name: the name of version to be published
    :return:
    """
    proj = proj.lower()
    pass_file = hpu.check_hair_pass_exists(proj, shot)
    publish_dir = hpu.HAIR_PASS_PUBLISH.format(proj=proj, shot=shot, seq=shot[:3], version=publish_version_name)
    publish_file = os.path.join(publish_dir, os.path.basename(pass_file))
    if not os.path.exists(publish_dir):
        os.makedirs(publish_dir)
    if pass_file:
        shutil.copyfile(pass_file, publish_file)
    output_dir = hpu.HAIR_PASS_OUTPUT.format(proj=proj,shot=shot,seq=shot[:3])
    col_vis_name = chpu.COLLECTION_VISIBILITY_FILENAME.format(shot=shot)
    collection_pass_file = os.path.join(output_dir,col_vis_name)
    if os.path.isfile(collection_pass_file):
        publish_cpf = os.path.join(publish_dir,col_vis_name)
        shutil.copyfile(collection_pass_file, publish_cpf)
    chmod_dir(publish_dir)
    return "Move hair pass completed."


def setAuxPachesFile(ABCpath, palette):
    descShapes = listRelatives(palette, type="xgmDescription", ad=True)
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


def web_publish(publishPath):
    replace = publishPath
    proj = publishPath.split('/')[4]
    shot = publishPath.split('/')[7]
    for root, dirs, files in os.walk(publishPath + '/cache'):
        for fileFullName in files:
            # fix xgen file
            if fileFullName.endswith('xgen'):
                realPath = root + '/' + fileFullName
                old_data = []
                with open(realPath, 'r') as f:
                    old_data.extend(f.readlines())
                with open(realPath, 'w') as f:
                    for line in old_data:
                        lineList = line.split()
                        if len(lineList) > 1:
                            if lineList[0] == 'cacheFileName':
                                orient = lineList[1].split('/cache/')[0]
                                if orient.split('/')[1] == 'output' or '/mnt/output/' in orient:
                                    line = line.replace(orient, replace)
                        f.write(line)

            # fix xml file
            if fileFullName.endswith('xml'):
                realPath = root + '/' + fileFullName
                old_data = []
                with open(realPath, 'r') as f:
                    old_data.extend(f.readlines())
                with open(realPath, 'w') as f:
                    for line in old_data:
                        if len(line.split()) > 2:
                            if line.split()[1] == 'name=\"data\"':
                                for str in line.split():
                                    if len(str.split('/')) > 2:
                                        if str.split('/')[1] == 'output' or '/mnt/output/' in str:
                                            orient = str.split('/cache/')[0]
                                            line = line.replace(orient, replace)
                            elif '/output/' in line:
                                if line.split('"')[-2].startswith('/mnt/output/') or line.split('"')[-2].startswith(
                                        '/output/'):
                                    orient = line.split('"')[-2].split('/cache/')[0]
                                    line = line.replace(orient, replace)
                        f.write(line)

            # remove symlink patch abc
            if fileFullName.endswith('abc') and fileFullName.startswith('__'):
                os.remove(os.path.join(root, fileFullName))

        # symlink new patch abc
        if hpu.is_felt(proj, shot):
            if root.endswith('/patches'):
                src = os.path.join(root, files[0])
                dst = os.path.join(os.path.split(root)[0], '__%s' % files[0])
                os.symlink(src, dst)


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
                if not os.path.isdir(dir_path):
                    return dir_path + u'不是文件夹.'
                sub_path = dir_path.split('/cfx/output/')[1]
                if sub_path.endswith('/'):
                    sub_path = sub_path[:-1]
                sub_path_tokens = sub_path.split('/')
                sub_path = '/'.join(sub_path_tokens[1:])
                target_dir = self.dialog.version_dir + '/' + sub_path
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                for f in list(set(os.listdir(dir_path))):
                    src = dir_path + '/' + f
                    dst = self.dialog.version_dir + '/' + sub_path + f

                    # remove output symlink patch abc
                    for root, dirnames, files in os.walk(src):
                        for fileFullName in files:
                            if fileFullName.endswith('abc') and fileFullName.startswith('__'):
                                realPath = os.path.join(root, fileFullName)
                                os.remove(realPath)

                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                        os.system("rsync -L -az %s/ %s" % (src, dst))
                    else:
                        shutil.copy2(src, dst)
                        os.system("rsync -L -az %s %s" % (src, dst))

                    # symlink output new patch abc
                    for root, dirnames, files in os.walk(src):
                        if root.endswith('/patches'):
                            _src = os.path.join(root, files[0])
                            _dst = os.path.join(os.path.split(root)[0], '__%s' % files[0])
                            os.symlink(_src, _dst)

                    chmod_dir(dst)
                web_publish(self.dialog.version_dir)

                # send vendor file
                _task = self.dialog.task['name']
                if _task == 'cloth':
                    vu = updater.VenderUpdater(self.dialog.version_dir)
                    vu.run()

            proj_name = self.dialog.project.get("name").lower()
            shot_name = self.dialog.entity_name
            me = self.dialog.user['name']
            if self.dialog.task['name'] == "hair":
                # 把 output 的 hairpass信息 pa到 proj 盘
                logger.debug("move hair pass")
                v_name = self.dialog.version_key + self.dialog.w_ver.lineEdit_version_name.text()
                print(9999999999999999999999999999999999999999999999999999999999999999,v_name)
                result = move_hair_pass(self.dialog.project.get("name"), self.dialog.entity_name, v_name)
                print(8888888888888888888888888888888888888888888888888888888888888888,result)
                logger.debug(result)

                # 往农场发一个转换镜头hair usd的任务
                hair_arg = ' cfx_hair --proj {} --shots {} --time_elapsed=0.0'.format(proj_name,shot_name)
                print(777777777777777777777777777777777777777777777777777777777777777,hair_arg)
                jb_name = 'Export USD HAIR {} {} by {}'.format(proj_name,shot_name,me)
                print(66666666666666666666666666666666666666666666666666666666666666,jb_name)
                usd_shot_hair_id = ppj.send_job(convert_usd_cache,
                                                args=hair_arg,
                                                proj=proj_name,
                                                job_name_prefix=jb_name,
                                                step='CFX',
                                                pools='centos7',
                                                user=me,
                                                python_exe=lc_py,
                                                submitdl=True
                                                )
                print 'Export USD HAIR: ',usd_shot_hair_id

            if self.dialog.task['name'] == "cloth":
                # 往农场发一个转换镜头clothr usd的任务
                cloth_arg = ' cfx_cloth --proj {} --shots {} --time_elapsed=0.0'.format(proj_name,shot_name)
                jb_name = 'Export USD CLOTH {} {} by {}'.format(proj_name,shot_name,me)
                usd_shot_clothr_id = ppj.send_job(convert_usd_cache,
                                                args=cloth_arg,
                                                proj=proj_name,
                                                job_name_prefix=jb_name,
                                                step='CFX',
                                                pools='centos7',
                                                user=me,
                                                python_exe=lc_py,
                                                submitdl=True
                                                )
                print 'Export USD CLOTH: ',usd_shot_clothr_id



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
