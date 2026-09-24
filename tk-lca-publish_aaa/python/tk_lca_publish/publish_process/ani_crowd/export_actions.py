# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.10
#
# Description: export action nodes for use in Miarmy
#
############################################
import traceback
import sys
import os

import maya.cmds as mc
import json

import production.mayautils.decorators as md
import production.mayautils as mu
import crd.export_action.submit as submit
reload(md)

# DEFAULT_AGENT_NAME = 'loco'
# DEFAULT_CYCLE_FILTER = 10
# DEFAULT_TRANS_IN = 10
# DEFAULT_TRANS_OUT = 80
# SKELETON_GROUP_NAME = 'anim_skeletons_grp'

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"分段输出行为数据。"
        self.description = u"分段输出Miarmy行为数据。"
        return

    @md.d_disableViews
    def proceed(self):
        try:
            publishRoot = '/mnt/proj/projects/'
            if sys.platform.startswith('win'):
                trashDir = 'Z:/trash/jingwei_crontab/crd/action_submit/log/'
            elif sys.platform.startswith('linux'):
                trashDir = '/mnt/proj/trash/jingwei_crontab/crd/action_submit/log/'


            proj = self.dialog.project['name'].lower()
            task = self.dialog.task['name']
            step = self.dialog.step['name']
            userName = self.dialog.user['name']
            assetName = self.dialog.entity['name']

            motionType = self.dialog.actions_data
            sceneName = mc.file(q=1, sceneName=1, shortName=1)
            scene = mc.file(q=1, sceneName=1)
            baseName = sceneName.replace('.ma', '')

            start = motionType[0]['start']
            end = motionType[0]['end']
            is_cycle = motionType[0]['is_cycle']
            name = motionType[0]['name'] + "_action_" + assetName
            action_type = motionType[0]['action_type']

            mu.log(proj)
            mu.log(assetName)
            mu.log(step)
            mu.log(baseName)

            outputDir = os.path.join(publishRoot, proj, 'asset/crd/', assetName, step, 'publish', baseName, 'actions')
            outFileName = assetName + "_" + motionType[0]['name'] + "_action.ma"
            output = os.path.join(outputDir, outFileName) 

            job = {"project_name":proj, "start": start, "end": end, "cycle": is_cycle, 
                    "name": name, "actionType": action_type, "output": output, 
                    "file": scene, "asset_name": assetName, "user": userName}

            # logPath = 'Z:/trash/jingwei_crontab/crd/action_submit/log/'
            logFileName = "%s_%s.log" % (baseName, userName)
            logFile = trashDir + logFileName
            with open(logFile, 'w') as json_file:
                json.dump(job, json_file, ensure_ascii=False, indent=4)

            os.chmod(logFile, 0777)
            # json.dump(job)
            # submit.main(jobs)
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
