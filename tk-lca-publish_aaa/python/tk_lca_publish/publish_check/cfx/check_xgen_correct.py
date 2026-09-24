# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.02
#
# Description: As the description shows below
#
############################################
import os
import traceback
import datetime
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查xgen正确性"
        self.description = u"强制刷新xgen是否有报错"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            bad_str = ''
            if 'cloth' in self.dialog.task['name']:
                return ''

            version_key = self.dialog.version_key

            tmp_file = "/home/tmp/%s.txt" % (
                    datetime.datetime.now().strftime("%Y%m%d%H%M") + '.' + version_key)
            pm.scriptEditorInfo(historyFilename=tmp_file, writeHistory=True)

            node = []
            for yeti_node in pm.ls(type='pgYetiMaya'):
                node.append(yeti_node)
            if len(node) > 0:
                return ''
            else:
                import xgenm.xgGlobal as xgg
                de = xgg.DescriptionEditor
                old_mode = de.previewMode
                de.previewMode = 2  # preview all collections
                de.updatePreviewControls()
                de.preview(clean=False, progress=True, idle=False)  # Force update all collections

                de.previewMode = old_mode
                de.updatePreviewControls()

                pm.scriptEditorInfo(historyFilename=tmp_file, writeHistory=False)
                with open(tmp_file, 'r') as f:
                    data = f.readlines()
                error = [d for d in data if "Error: XGen:" in d]

                os.remove(tmp_file)
                if error:
                    return ''.join(error)
                else:
                    return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
