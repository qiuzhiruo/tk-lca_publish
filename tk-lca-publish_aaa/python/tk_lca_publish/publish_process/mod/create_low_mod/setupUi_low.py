# -*- coding: utf-8 -*-
import getpass
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

class Submit_farm(object):

    def __init__(self,file_name,file_path,auto_pu_linux):
        WORK_ROOT = os.getenv('LC_WORK')
        TOOL_ROOT = os.getenv('LC_UTILITY')
        if sys.platform.startswith("win"):
            if os.path.dirname(__file__)[0] == "W" or os.path.dirname(__file__)[0] == "w":
                self.maya_job_py = (WORK_ROOT+os.path.dirname(__file__)[2:]+"/maya_polyReduce.py").replace("\\", "/")
            if os.path.dirname(__file__)[0] == "U" or os.path.dirname(__file__)[0] == "u":
                self.maya_job_py = (TOOL_ROOT+os.path.dirname(__file__)[2:]+"/maya_polyReduce.py").replace("\\", "/")
        else:

            self.maya_job_py = os.path.dirname(__file__)+"/maya_polyReduce.py"

        self.FARMTEMPLATE_ID = LcaFarmIPManage().MASTERCACHE
        self.file_name = file_name
        self.file_path = file_path
        self.auto_pu = auto_pu_linux

        self.send_maya_jobs()


    def send_maya_jobs(self):
        lca_rez_path = os.getenv('LCA_REZ')
        job_id = ppj.send_job(self.maya_job_py,
                        args =self.file_name+" "+self.file_path+" "+self.auto_pu,
                        proj = "LRS",
                        job_name_prefix = '[Mod]'+"create house low model",
                        step = 'MOD',
                        pools ='centos7',
                        url = self.FARMTEMPLATE_ID,
                        python_exe = '{}/launchers/can/linux/mayapy2019'.format(lca_rez_path),
                        priority = 2000,
                        user=getpass.getuser(),
                        submitdl=True,
                        )

        print job_id
        pidgin = lca_xmpp.Sender()
        message = 'SRF PUBLISH UV 在减面_maya   ID：'+str(job_id)
        pidgin.send(["zejie"], message)


def setupUi(file_name, file_path, auto_pu):
    file_name_linux = file_name
    file_path_linux = file_path

    auto_pu_linux = auto_pu

    print(file_name_linux, file_path_linux, auto_pu_linux)

    Submit_farm(file_name_linux, file_path_linux, auto_pu_linux)

