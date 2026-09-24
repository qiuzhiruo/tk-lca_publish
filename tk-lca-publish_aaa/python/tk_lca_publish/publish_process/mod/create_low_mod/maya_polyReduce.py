# -*- coding: utf-8 -*-
############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: guanzejie
#
# Date: 2022.05
#
# Description:
#
############################################
import getpass

import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import os
import sys
# if sys.platform.startswith("win"):
#     os.environ["PATH"] += ';W:/software/muster8.5.7_win/'
#     os.environ["MUSTER"] = 'C:/Program Files/Virtual Vertex/Muster 8/'
#     sys.path.append('U:/linked_tools/lcatools/lib/3rd_party/Muster_win/muster8sdk/libs/win64/python27')
#     sys.path.append('U:/linked_tools/lcatools/lib/3rd_party/Muster_win/')
# sys.path.insert(0, '/mnt/work/software/muster8.5.7-sdk/libs/linux64/python27')
import production.python_job as ppj
import production.lca_xmpp as lca_xmpp
from production.farm_ip import LcaFarmIPManage
OS = sys.platform

cmds.loadPlugin('AbcExport.mll')

cmds.loadPlugin('AbcImport.mll')

def make_low_mod():

    cmds.file(sys.argv[1], open=True, force=True)
    list_all_transform = cmds.ls(type="transform")

    cmds.select(cl=True)

    for i in list_all_transform:

        if i=="wapian_hi_grp" or i=="wa_hi_grp":

            cmds.select(i)
            group_path=cmds.ls(sl=True,l=True)[0]
            export_note = "-frameRange 1 1 -uvWrite -writeUVSets -dataFormat ogawa -root "+group_path+" -file "+ sys.argv[2] + i + ".abc"
            cmds.AbcExport(j=export_note)

        cmds.select(cl=True)

    for j in list_all_transform:
        if j=="wapian_hi_grp" or j=="wa_hi_grp":
            cmds.delete(j)

    list_all = cmds.ls(type="mesh")

    for i in list_all:

        face_f = cmds.polyEvaluate(i, f=True)

        cmds.polySoftEdge(i, a=0, ch=1)

        if face_f > 1000:
            cmds.polyReduce(i, ver=1, trm=0, shp=0, keepBorder=1, keepMapBorder=1, keepColorBorder=1, keepFaceGroupBorder=1,
                            keepHardEdge=1, keepCreaseEdge=1, keepBorderWeight=0.5, keepMapBorderWeight=0.5,
                            keepColorBorderWeight=0.5, keepFaceGroupBorderWeight=0.5, keepHardEdgeWeight=0.5,
                            keepCreaseEdgeWeight=0.5, useVirtualSymmetry=0, symmetryTolerance=0.01, sx=0, sy=1, sz=0, sw=0,
                            preserveTopology=1, keepQuadsWeight=1, vertexMapName="", cachingReduce=1, ch=1, p=70, vct=0,
                            tct=0, replaceOriginal=1)

            cmds.delete(i, constructionHistory=True)

    #cmds.file(force=True,save=True,options="v=0")
    hi_grp=sys.argv[2] + "hi.abc"
    export_note = "-frameRange 1 1 -uvWrite -writeUVSets -dataFormat ogawa -root |master|poly|hi -file " + hi_grp
    cmds.AbcExport(j=export_note)

    return hi_grp


class Submit_farm(object):

    def __init__(self,maya_file_m,abc_path_m,hi_grp_a,auto_pu_linux):
        self.houdini_job_py = os.path.dirname(__file__)+"/houdini_job.py"

        self.FARMTEMPLATE_ID = LcaFarmIPManage().MASTERCACHE
        self.abc_name_m = abc_path_m

        self.maya_file_m = maya_file_m

        self.hi_grp_a = hi_grp_a

        self.auto_pu_linux = auto_pu_linux

        self.send_houdini_jobs()

    def send_houdini_jobs(self):
        lca_rez_path = os.getenv('LCA_REZ')
        job_id = ppj.send_job(self.houdini_job_py,
                        args =self.abc_name_m+" "+self.maya_file_m+" "+self.hi_grp_a+" "+self.auto_pu_linux,
                        proj = "LRS",
                        job_name_prefix = '[Mod]'+"create house low model",
                        step = 'MOD',
                        pools ='centos7',
                        url = self.FARMTEMPLATE_ID,
                        python_exe = '{}/launchers/lrs/linux/hython18.5.596'.format(lca_rez_path),
                        priority = 2000,
                        user=getpass.getuser()
                        submitdl=True
                        )

        print job_id
        pidgin = lca_xmpp.Sender()
        message = 'SRF PUBLISH UV 在减面_houdini    ID：'+str(job_id)
        pidgin.send(["zejie"], message)


hi_grp_a = make_low_mod()

print("_____________________________________")
print(sys.argv[1],sys.argv[2],hi_grp_a,sys.argv[3])
print("_____________________________________")
Submit_farm(sys.argv[1],sys.argv[2],hi_grp_a,sys.argv[3])





