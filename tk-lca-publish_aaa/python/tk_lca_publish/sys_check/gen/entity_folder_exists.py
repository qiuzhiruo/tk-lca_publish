# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shtogun data
#
############################################

import traceback

import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查任务(Task)的publish文件夹是否建立。"
        self.description = u"在服务器上，应该已经建立了这个场/镜头/资产所用的，各个部门的publish文件夹。"
        self.auto_fix = False
        self.duty = u"流程管理。"
        return

    def write_log(self,log):
        import tempfile
        import datetime
        tmpdir = tempfile.gettempdir()
        name = os.path.basename( __file__ )
        logf = os.path.join(tmpdir, name)
        logtime =str(datetime.datetime.now())
        with open('%s.txt'%logf,'a') as f:
            f.write( '\r\n debug:'+log+'\t @'+logtime)

    def run_check(self):
        try:

            if not os.path.isdir(self.dialog.publish_root):
                return (u"Publish文件夹没有建立: " + self.dialog.publish_root)

            if not os.path.isdir(self.dialog.work_root):
                return (u"Work文件夹没有建立: " + self.dialog.work_root)

            self.dialog.print_log('Pulbish to: ' + self.dialog.publish_root )

            # If we are working in maya, get the default playblaster mov file path
            try:
                if 'KATANA_RESOURCES' not in os.environ.keys():
                    import pymel.core as pm
                    file_path = pm.sceneName()
                    file_name = os.path.basename(file_path)
    
                    default_render = self.dialog.work_root + '/render/' + file_name[:-3] + '.mov'
                    default_playblast = self.dialog.work_root + '/data/' + file_name[:-3] + '.mov'
                    if self.dialog.publish_mode == 1 and os.path.isfile(default_render):
                        self.dialog.default_preview_mov = default_render
                    else:
                        if os.path.isfile(default_render):
                            if not os.path.isfile(default_playblast):
                                self.dialog.default_preview_mov = default_render
                            else:
                                mtime_pb = os.path.getmtime(default_playblast)
                                mtime_rd = os.path.getmtime(default_render)
                                if mtime_pb > mtime_rd:
                                    self.dialog.default_preview_mov = default_playblast
                                else:
                                    self.dialog.default_preview_mov = default_render
                        else:
                            self.dialog.default_preview_mov = default_playblast

            except:
                print 'Cant find the default preview mov file path since the publish tool is not activated in Maya.'
            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        return ""


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

