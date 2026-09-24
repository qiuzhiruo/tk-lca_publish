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
#export xgen file need to change 1 the "xgFileName" 2 the datapath 3 export the ma file 4 restore the oreint state
#
#
#
#
#
#
############################################

import os
import sys
import shutil
import traceback
import threading
pythonMode = 0
try:
    from pymel.mayautils import getMayaLocation
    xgenModelPath=getMayaLocation()+'/plug-ins/xgen/scripts'
    sys.path.append(xgenModelPath)
    #import maya.cmds as cmds
    import xgenm as xg
    import xgenm.xgGlobal as xgg
    import xgenm.XgExternalAPI as base
    import pymel.core as pmt
    import maya.mel as mel
except:
    pythonMode = 1

#import production.shotgun_connection as sgc

def setActive( palette, description, subtype, previewer=False ):
    cmd = 'xgmSetActive -d "'+description+'" -o "'+subtype+'" '
    if subtype == 'GLRenderer':
        previewer = True
    if previewer:
        cmd += '-p true'
    return mel.eval(cmd)


def exportProx(desc,fileDir):
    palette = xg.palette(str(desc))
    abcDir=fileDir+'/'+str(palette)+'/'+str(desc)+"/prox/"
    if os.path.isdir(abcDir):
        shutil.rmtree(abcDir)
    os.makedirs(abcDir)
    xg.setAttr("outputDir", abcDir, palette, desc, "ABCProxRenderer")
    cmd = 'xgmExport -x ABCProxRenderer -pb {"'+desc+'"}'
    mel.eval(cmd)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出植被分布 Prox文件。"
        self.description = u"输出植被分布 Prox文件。"
        return
    def export_proxy(self, mayaFile,export_path):
        #export xgen proxy
        import cfx.lcaCfxCache.xgen_Proxy_submit_muster  as submit
        start_frame = 1000
        end_frame = 1000
        job = submit.SubmitCFXMaya(mayaFile, export_path, '', start_frame, end_frame)
        jobId = job.submit_job()
        return jobId
    def onBuildCommandLine(self, mayaFile,export_path ):
        TOOL_ROOT = os.getenv('LC_UTILITY')
        toolset = os.getenv('LC_TOOLSET')
        renderCmd =  "{}/lca_launchers/maya/mayapy2015_CFX  {}/tools/cfx/lcaCfxCache/xgen_Proxy_cmd.py  ".format(TOOL_ROOT, toolset)
        file_name = mayaFile
        assetsName = ''
        start_frame = 1
        end_frame = 1
        renderCmd += "\"" + file_name + "\" "
        renderCmd += "\"" + export_path+ "\" "
        renderCmd += "\"" + assetsName + "\" "
        renderCmd += " " + '%d' % start_frame
        renderCmd += " " + '%d' % end_frame
        os.system(renderCmd)
    def proceed(self):
        try:
            if pythonMode == 0:
                assetPubFolder = self.dialog.version_dir
                mayaFile = pmt.sceneName()
                self.export_proxy(mayaFile, assetPubFolder)
                #new_thread = threading.Thread(target=self.onBuildCommandLine, args=(mayaFile, assetPubFolder))
                #new_thread.start()
            else:
                from PyQt4.QtGui import *
                assetPubFolder = self.dialog.version_dir
                basicFilter = "*.ma"
                stringD=assetPubFolder.split('publish')[0].replace('proj','work',1)+'task/maya'
                mayaFile =  QFileDialog.getOpenFileName(QWidget(), 'Select the maya file which you will publish', stringD,basicFilter)
                self.export_proxy( mayaFile, assetPubFolder)
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

