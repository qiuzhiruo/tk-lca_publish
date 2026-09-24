# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.08
#
# Description: 
#
############################################

import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"版本技术描述"
        self.description = u"版本技术描述"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:

            l_msgs = []
            l_msgs.append(u"视频总时长 " + str(self.dialog.video_length) + u"帧")
            l_msgs.append(u"声音时长 " + str(self.dialog.audio_length) + u" 帧")
            l_msgs.append(u"黑帧总时长 " + str(self.dialog.blank_jpg_length) + u" 帧")

            l_shots = []
            for i in sorted(self.dialog.edt_cuts.keys()):
                shot_name = self.dialog.edt_cuts[i]['shot_name']
                if not shot_name in l_shots:
                    l_shots.append(shot_name)
                else:
                    l_msgs.append(u"镜头 " + shot_name + u" 在全场被多次使用")

                if len(self.dialog.edt_cuts[i]['edt_info']) == 0:
                    l_msgs.append(u"镜头 " + shot_name + u" 没有剪辑信息")
                elif len(self.dialog.edt_cuts[i]['edt_info']) > 1:
                    l_msgs.append(u"镜头 " + shot_name + u" 被切割拼接使用")
                else:
                    edt_info = self.dialog.edt_cuts[i]['edt_info'][0]
                    v_name = edt_info[0]
                    #self.dialog.print_log(str(self.dialog.d_shot_versions))
                    version = self.dialog.d_shot_versions[shot_name][v_name]
                    if edt_info[1] != 0:
                        l_msgs.append(u"镜头 " + shot_name + u" 剪头" + str(edt_info[1]) + u"帧")
                    if edt_info[2] != version['frame_count']:
                        l_msgs.append(u"镜头 " + shot_name + u" 剪尾" + str(version['frame_count'] - edt_info[2]) + u"帧")
            
            self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(u"\n".join(l_msgs))
            return ""
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

