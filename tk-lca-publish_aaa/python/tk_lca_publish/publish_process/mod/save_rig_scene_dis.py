# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil
from proc.function_running_time import record_time



# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"3th_保存到publish盘"
        self.description = u"3th_保存到publish盘"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            import maya.cmds as cmds
            import pymel.core as pm
            try:
                # # 隐藏物体
                # geo_name_list=['head_grp', 'head_low_eyeopen_geo','head_geo']
                #
                # for child in cmds.listRelatives('mesh_grp', c=True):
                #
                #     if child not in geo_name_list:
                #         geo_str=child+".visibility"
                #         cmds.setAttr(geo_str, 0)

                # 保存备份文件到work服务器
                path_name = cmds.file(q=True,sceneName=True)
                scene_name = path_name.split("/")[-1]
                rig_name = scene_name.split(".")[0]+"_rig_facial_builder"

                # save to publish disk
                cmds.file(rename=self.dialog.version_dir + '/' + rig_name)
                cmds.file(save=True, force=True, type="mayaAscii")

                # 备份文件backup,移动备份文件到动备文件夹
                list_path = path_name.split("/")
                maya_file_name=list_path.pop()

                for i in list_path:
                    if (list_path.index(i) == 0):
                        path_w = i + "/"
                    else:
                        path_w = path_w + i + "/"

                backup_path = path_w+"backup"

                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)

                work_scene_path =backup_path+"/"+ maya_file_name[0:-3] + "_backup"
                cmds.file(rename=work_scene_path)
                cmds.file(save=True, force=True, type="mayaAscii")

                # save to work disk
                cmds.file(rename=path_name)
                cmds.file(save=True, force=True, type="mayaAscii")

                # 选择需要删除历史的文件
                cmds.select("master", r=True)
                cmds.delete(ch=True)

                mesh_list = cmds.ls(type="mesh")
                for mesh_l in mesh_list:
                    if "Orig" in mesh_l:
                        cmds.delete(mesh_l)

                unknown_nodes = pm.ls(type='unknown')
                if unknown_nodes:
                    pm.delete(unknown_nodes)

                import maya.mel as mel
                mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')

                cmds.delete("rig")


                #删除多余文件
                # for child in cmds.listRelatives('mesh_grp', c=True):
                #
                #     if child not in geo_name_list:
                #         cmds.delete(child)
                #
                # cmds.group('head_geo', parent='master', name="shape")
                # cmds.setAttr('head_geo.visibility', 0)

                print("____________________________________________3dh_________________________________________________")




            except:
                print traceback.format_exc()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


