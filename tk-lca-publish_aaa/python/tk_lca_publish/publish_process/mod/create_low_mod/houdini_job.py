# -*- coding: utf-8 -*-
import getpass

import hou
import os
import sys
OS = sys.platform
# if sys.platform.startswith("win"):
#     os.environ["PATH"] += ';W:/software/muster8.5.7_win/'
#     os.environ["MUSTER"] = 'C:/Program Files/Virtual Vertex/Muster 8/'
#     sys.path.append('U:/linked_tools/lcatools/lib/3rd_party/Muster_win/muster8sdk/libs/win64/python27')
#     sys.path.append('U:/linked_tools/lcatools/lib/3rd_party/Muster_win/')
# sys.path.insert(0, '/mnt/work/software/muster8.5.7-sdk/libs/linux64/python27')
import production.python_job as ppj
import production.lca_xmpp as lca_xmpp
from production.farm_ip import LcaFarmIPManage

houdini_abc_out = []

def output_low_abc(abc_path,save_path,abc_name):

    abc_sort_name = abc_name.split("_")[0]

    out_name = save_path + abc_sort_name + '_low.abc'

    houdini_abc_out.append(out_name)

    node = hou.node("obj/geo")

    input = hou.node('/obj/geo/INPUT')

    out = hou.node('/obj/geo/OUT')
    out.parm("filename").set(save_path + abc_sort_name + '_low.abc')

    input.setRenderFlag(1)
    input.setDisplayFlag(1)

    posx = input.position()[0]
    posy = input.position()[1]

    abc = node.createNode("alembic", "abcInput")

    abc.setPosition([posx, posy + 10])

    input.setInput(0, abc)

    filename = abc.parm("fileName")

    filename.set(abc_path)

    out.parm("execute").pressButton()

    return node


def open_file(abc_path,save_path,abc_name):

    try:

        hou.hipFile.load(os.path.dirname(__file__) + "/houdini/houdini_low.hip")

        node = output_low_abc(abc_path,save_path,abc_name)

        if not os.path.exists(save_path + "houdini/"+abc_name+".hip"):
            hou.hipFile.save(save_path + "houdini/"+abc_name+".hip")

        node.destroy()

    except:
        print("error file")


class Submit_farm_maya(object):

    def __init__(self,maya_file_name,abc_houdini,hi_abc,auto_pu_h):
        self.maya_job_py = os.path.dirname(__file__)+"/maya_merge_file_auto_publish.py"

        self.FARMTEMPLATE_ID = LcaFarmIPManage().MASTERCACHE
        self.maya_file_name = maya_file_name
        if len(abc_houdini) == 0:

            self.abc_houdini = "0"
        else:
            self.abc_houdini = abc_houdini[0]

        self.hi_abc = hi_abc

        self.auto_pu_h = auto_pu_h

        self.send_maya_jobs()


    def send_maya_jobs(self):
        lca_rez_path = os.getenv('LCA_REZ')
        job_id = ppj.send_job(self.maya_job_py,
                        args = self.maya_file_name+" "+self.abc_houdini+" "+self.hi_abc+" "+self.auto_pu_h,
                        proj = "LRS",
                        job_name_prefix = '[Mod]'+"create house low model",
                        step = 'MOD',
                        pools ='centos7',
                        url = self.FARMTEMPLATE_ID,
                        python_exe = '{}/launchers/lrs/linux/mayapy2019'.format(lca_rez_path),
                        priority = 2000,
                        user=getpass.getuser()
                        submitdl=True
                        )

        print job_id
        pidgin = lca_xmpp.Sender()
        message = 'maya文件合并   ID：'+str(job_id)
        pidgin.send(["zejie"], message)


def main(abc_path_m1,maya_file_h,abc_low_h,auto_pu):

    abc_path = abc_path_m1

    all_hi_abc = os.listdir(abc_path)

    low_model_path = os.path.dirname(os.path.dirname(abc_path))+"/wapian_low_abc/"

    if not os.path.exists(low_model_path):

         os.makedirs(low_model_path)

    for abc in all_hi_abc:

        if abc =="hi.abc":
           continue

        abc_path = abc_path + abc

        open_file(abc_path, low_model_path, abc)

    print("_____________________________________")


    print(maya_file_h, houdini_abc_out, abc_low_h,auto_pu)
    Submit_farm_maya(maya_file_h,houdini_abc_out,abc_low_h,auto_pu)
    print("_____________________________________")


main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])