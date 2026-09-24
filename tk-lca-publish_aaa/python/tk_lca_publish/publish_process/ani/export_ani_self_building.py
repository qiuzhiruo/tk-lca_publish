# -*- coding:utf-8 -*-

import os
import shutil
import traceback

import sgtk
import maya.cmds as cmds
import maya.mel as mel


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出动画自己创建的道具到版本文件夹"
        self.description = u"导出动画自己创建的道具到版本文件夹。"
        return

    def proceed(self):
        try:
            engine = sgtk.platform.current_engine()
            shot_name = engine.context.entity["name"]

            ani_ref = "|assets|lay|ANI_REF"
            if cmds.objExists(ani_ref):
                if os.path.isdir(self.dialog.version_dir + '/ani_ref_cache'):
                    shutil.rmtree(self.dialog.version_dir + '/ani_ref_cache')

                os.makedirs(self.dialog.version_dir + '/ani_ref_cache')
                os.system("chmod 777 -R * %s" % self.dialog.version_dir)
                if cmds.listRelatives(ani_ref, children=True):
                    start_frame = cmds.playbackOptions(q=True, minTime=True)
                    end_frame = cmds.playbackOptions(q=True, maxTime=True)
                    abc_name = "{}.ani.reference.abc".format(shot_name)
                    abc_file = "{}/{}/{}".format(self.dialog.version_dir, "ani_ref_cache", abc_name)
                    _mel = 'AbcExport -j "-frameRange {start_f} {enf_f} -uvWrite -worldSpace -writeVisibility ' \
                           '-eulerFilter -writeUVSets -dataFormat ogawa -root {group} -file {abc_file}";'
                    cmd = _mel.format(start_f=start_frame, enf_f=end_frame, group=ani_ref, abc_file=abc_file)
                    # print cmd
                    mel.eval(cmd)
                    os.system("chmod 777 -R * %s" % self.dialog.version_dir)
                    return ""
                else:
                    return ""

            else:
                return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description