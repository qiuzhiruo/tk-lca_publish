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
        self.process_name = u"3th_恢复rig文件保存"
        self.description = u"3th_恢复rig文件保存"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            import maya.cmds as cmds
            try:

                path_name = cmds.file(q=True, sceneName=True)

                # 打开备份的文件
                list_path = path_name.split("/")
                maya_file_name=list_path.pop()

                for i in list_path:
                    if (list_path.index(i) == 0):
                        path_w = i + "/"
                    else:
                        path_w = path_w + i + "/"

                backup_path = path_w+"backup"

                work_scene_path = backup_path + "/" + maya_file_name[0:-3] + "_backup.ma"

                cmds.file(work_scene_path, open=True, force=True)

                # 保存文件
                cmds.file(rename=path_name)
                cmds.file(save=True, force=True, type="mayaAscii")

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


