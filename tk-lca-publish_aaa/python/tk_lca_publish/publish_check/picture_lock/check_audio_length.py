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

import sys
import shutil
import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查声音文件和视频是否一致"
        self.description = u"检查声音文件和视频是否一致"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        """
        """
        try:
            self.dialog.blank_jpg_length = self.check_blank_jpg()
            if self.dialog.audio_length != self.dialog.video_length + self.dialog.blank_jpg_length:
                return u"声音时长 " + str(self.dialog.audio_length) + u" 帧；视频总时长 " + str(self.dialog.video_length) + u"帧；黑帧总时长 " + str(self.dialog.blank_jpg_length) + u"帧"
            return ""
        except:
            return traceback.format_exc()

    def check_blank_jpg(self):
        """
        """
        total_blank_jpg_length = 0
        # edt_info_end = self.dialog.edt_cuts[0]['edt_info'][0][4]
        for i in sorted(self.dialog.edt_cuts.keys()):
            edt_info_end = self.dialog.edt_cuts[i]['edt_info'][-1][4]
            if i >= len(self.dialog.edt_cuts.keys()) - 1:
                break

            # e.g. [['z12020.lgt.lighting.v010', 0, 73, 352, 425], ['z12020.lgt.lighting.v010', 74, 76, 426, 428]]
            shot_info_list = self.dialog.edt_cuts[i + 1]['edt_info']
            for j, shot_info in enumerate(shot_info_list):
                next_edt_start = shot_info[3]
                if next_edt_start > edt_info_end:  # when transition between two shots, next_edt_start may < edt_info_end
                    self.dialog.print_log(shot_info[0] + ':' + str(edt_info_end) + '-' + str(next_edt_start))
                    blank_jpg_length = int(next_edt_start) - int(edt_info_end)
                    total_blank_jpg_length += blank_jpg_length
                edt_info_end = shot_info[4]

        self.dialog.print_log('total blank jpg length: %d' % total_blank_jpg_length)
        return total_blank_jpg_length

    def run_fix(self):
        """
        """
        try:
            # backup the wav
            backup_audio_file = self.dialog.audio_file.replace('.wav', '.backup.wav')
            shutil.copyfile(self.dialog.audio_file, backup_audio_file)
            
            # check if audio problem can be auto-fixed, if pass the check, then continue
            if self.dialog.audio_length > (self.dialog.video_length + self.dialog.blank_jpg_length):
                self.dialog.print_error(u'声音时长 > 视频时长，不能被自动修复')
                return u'声音时长 > 视频时长，不能被自动修复'
            else:
                import edt.edt_analyse.processAudio as processAudio
                result = processAudio.process_music(backup_audio_file, self.dialog.edt_file, self.dialog.audio_file)
                if result:
                    self.print_log(result)
                    return result
            
                import production.audio as audio
                self.dialog.audio_length = int(round(audio.getDuration(self.dialog.audio_file)))
                self.dialog.print_log('auto fix done')
                return 
        except:
            self.dialog.print_log( traceback.format_exc())
            return  traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

