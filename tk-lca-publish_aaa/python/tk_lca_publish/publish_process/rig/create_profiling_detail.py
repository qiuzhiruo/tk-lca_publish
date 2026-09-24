# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Edward Sun
#
# Date: 2014.05
#
# Description: 
#
############################################
import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

#edo_getLastVersionStr()
def edo_getLastVersionStr(root,task):
    #root=root
    #task=bodyrigtask
    alldirs=os.listdir(root)
    version=-1
    maxversion=''
    for dir in alldirs:
        #dir=alldirs[11]
        if task in dir:
            #print dir
            vstr=dir.replace(task,'')
            vid=int(vstr.replace('v',''))
            #print vid
            if vid>version:
                version=vid
                maxversion=vstr
    print maxversion
    return maxversion

def edo_getPublishDir():
    #pubfn='Z:/projects/tpr/asset/chr/golden_pig/rig/publish/golden_pig.rig.rigging/anim_rig/'
    fn=cmds.file(q=1,sn=1)
    pubfn=''
    pubfn=fn.replace('W:/','Z:/').replace('/task/maya/','/publish/').replace('.ma','/')+'anim_rig/'
    return pubfn

def edo_getProfilingData(pd):
    #pd='Z:/projects/tpr/asset/chr/atang/rig/publish/atang.rig.rigging/anim_rig/profilingData.txt'
    f=open(pd,'r')
    txs=f.read()
    f.close()
    txlist=txs.split('\n')
    tt=float(txlist[5].split(' ')[7])
    cm=float(txlist[6].split(' ')[5])
    dt=float(txlist[7].split(' ')[7])
    dw=float(txlist[8].split(' ')[8])
    ot=float(txlist[9].split(' ')[7])
    all=cm+dt+ot
    return [tt,all,dw]

def create_profiling_detail(pubfn):
    #pubfn='Z:/projects/tpr/asset/chr/xiaolai/rig/publish/xiaolai.rig.rigging.v041/anim_rig/'
    xlsxPath=os.path.dirname(__file__).replace('\\','/')+'/profiling_detail.xlsx'
    #xlsxPath=r'D:\program\git\tk-lca-publish\python\tk_lca_publish\publish_process\rig\profiling_detail.xlsx'
    hasdata=False
    prodata=[0,0,0,0]
    
    animrigdata=pubfn+'profilingData.txt'
    print 'anim rig profiling data path : '+animrigdata
    
    if os.path.exists(animrigdata):
        animtc=edo_getProfilingData(animrigdata)
        prodata[3]=animtc[0]
        prodata[2]=animtc[2]
        hasdata=True

    filename=cmds.file(sn=1,q=1).replace('W:/','Z:/').replace('/task/maya/','/publish/')
    sfilename=filename.split('/')[-1]
    root=filename.replace(sfilename,'')
    
    facialrigtask=sfilename.split('.rig.rigging')[0]+'.rig.rigging_facial.'
    facialrigversion=edo_getLastVersionStr(root,facialrigtask)
    facialrigdata=root+facialrigtask+facialrigversion+'/profilingData.txt'
    print 'facial rig profiling data path : '+facialrigdata
    
    if os.path.exists(facialrigdata):
        facialtc=edo_getProfilingData(facialrigdata)
        prodata[1]=facialtc[1]
        
    bodyrigtask=sfilename.split('.rig.rigging')[0]+'.rig.rigging_body.'
    bodyrigversion=edo_getLastVersionStr(root,bodyrigtask)
    bodyrigdata=root+bodyrigtask+bodyrigversion+'/profilingData.txt'
    print 'bodysys rig profiling data path : '+bodyrigdata
    
    if os.path.exists(bodyrigdata):
        bodytc=edo_getProfilingData(bodyrigdata)
        prodata[0]=bodytc[1]
    
    print 'profling data detail : '
    print prodata

    pythonexe='C:/Python27/python.exe'
    if not os.path.exists(pythonexe):
        return False
    
    pubfnxl=False
    if hasdata==True:
        localxl='D:/profiling_detail.xlsx'
        print 'copy ... '+xlsxPath+'   ---  to  ---  '+localxl
        shutil.copy(xlsxPath,localxl)

        print 'modify '+localxl
        import edo_publishListUI
        scriptpath=os.path.dirname(edo_publishListUI.__file__).replace('\\','/')+'/'
        cmd=[pythonexe , scriptpath+'edo_setExcel.py' , localxl , str(prodata[0]) , str(prodata[1]) , str(prodata[2]), str(prodata[3])]
        import subprocess
        #p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p = subprocess.Popen(cmd)
        p.communicate()
        #print err

        pubfnxl=pubfn+'profiling_detail.xlsx'
        print 'copy ... '+localxl+'   ---  to  ---  '+pubfnxl
        shutil.copy(localxl,pubfnxl)

    return pubfnxl
    
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"创建profinling detail excel 文件。"
        self.description = u"创建profinling detail excel 文件！"
        return

    def proceed(self):
        try:
            pubfn=edo_getPublishDir()
            if not pubfn==False:
                elsxpath=create_profiling_detail(pubfn)
                print elsxpath
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description