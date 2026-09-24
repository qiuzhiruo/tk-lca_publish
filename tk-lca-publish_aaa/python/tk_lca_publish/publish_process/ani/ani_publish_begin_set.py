# -*- coding:utf-8 -*-
import traceback

import pymel.core as pm
import maya.mel as mel


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"优化ANI Publish Process的maya设置修改"
        self.description = u"为防止ANI publish崩溃, 在publish之前对maya做一些设置, 最后在ani_publish_end_set.py再还原"
        return

    def proceed(self):
        try:
            # 以防万一, 在此增量保存一版文件
            # force to save the original file and incremental file
            try:
                mel.eval('incrementalSaveScene;')
            except:
                mel.eval('file -force -save -options "v=0";')

            # 如果MG的动画备份打开了备份约束, 则会导致导出相机这一步崩溃, 所以需要在导出相机前关闭, 最后再打开就好了
            self.dialog.old_mg_real_time_save_setting = pm.language.optionVar(q='MGrealTimeSaveAnimEnable')
            if self.dialog.old_mg_real_time_save_setting == 1:
                mel.eval('MGTools_Source "miniToolBox_WrittenByMiguel.mel";')
                mel.eval('turnOnOffAnimRescueAutoSaveInMinitoolBox 0 0;')

            # check pbcam and delete
            pb_cameras_grp = '|pb_cameras'
            if pm.objExists(pb_cameras_grp):
                pb_nodes = pm.listRelatives(pb_cameras_grp, allDescendents=True)
                pb_nodes.append(pb_cameras_grp)
                for node in pb_nodes:
                    pm.lockNode(node, lock=False)
                pm.delete(pb_cameras_grp)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
