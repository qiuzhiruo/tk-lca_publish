# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback

import os
import re
import sys

import edt.edt_cut_xml.cut_xml_main as cxm;reload(cxm)
import edt.aaf_analyse.utilities as aaf_util;reload(aaf_util)
import production.audio as audio

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"比较xml/aaf中时长和wav时长"
        self.description = u"比较xml/aaf中镜头时长和wav时长是否一致/整场时长和wav时长在切分前是否一致"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
    
    def compare_wav_duration(self, shot_name, wav_full_path):
        """
        """
        wav_dur = int(round(audio.getDuration(wav_full_path)))
        file_dur = self.dialog.edit_status_dict[shot_name][2]               # from tech_summary.py
        return file_dur == wav_dur, file_dur

    def run_check(self):
        try:

            if not self.dialog.xml_file and not self.dialog.aaf_file:
                return ''

            if self.dialog.lack_of_shots:
                return u'xml/aaf中缺少以下镜头:\n %s' % str(self.dialog.lack_of_shots)
            
            if self.dialog.w_publish_file.stb_checkbox.isChecked():         # do not compare wav xml in storyboard mode
                return ''
            
            if self.dialog.w_publish_file.seq_checkbox.isChecked():             # if sequence mode
                if not self.dialog.edit_status_dict:
                    return u'已选择Sequence Mode，但self.dialog.edit_status_dict 不存在, 可能是上一步tech_summary检查未通过导致的!'

                if self.dialog.xml_file:
                    split_shots, _ = cxm.get_orignal_xml_shot_splits(self.dialog.video_file_nodes,
                                                                     self.dialog.shot_items_dict,
                                                                     self.dialog.entity['name'])
                    seq_length = cxm.get_xml_original_length(split_shots)

                elif self.dialog.aaf_file:
                    seq_length = aaf_util.get_aaf_original_length(self.dialog.aaf_no_track_merge_result)

                audio_dur_int = int(round(audio.getDuration(self.dialog.wav_files[0])))
                if seq_length != audio_dur_int: 
                    return u'Sequence wav 时长和 xml/aaf 中的时长不一致, 相差 %d 帧.\nSequence wav时长: %d; xml/aaf时长: %d.' %\
                           (seq_length - audio_dur_int, seq_length, audio_dur_int)
                return ''
            else:
                diff_shots = {}
                for wav_item_path in self.dialog.wav_files:             # from publish_process/aud/cut_seq_wav.py
                    shot_name = os.path.basename(wav_item_path)[:6]
                    audio_dur_int = int(round(audio.getDuration(wav_item_path)))
                    the_same, file_dur= self.compare_wav_duration(shot_name, wav_item_path)
                    if not the_same:
                        diff_shots[shot_name] = (audio_dur_int, file_dur)
                
                if diff_shots:
                    pattern = u'wav时长和xml/aaf中的时长不一致(镜头号 wav时长 xml中时长)： %s %d %d\n'
                    msg = ''
                    for shot_name in diff_shots:
                        msg += pattern % (shot_name, diff_shots[shot_name][0], diff_shots[shot_name][1])
                    msg += u'\n请艺术家自行检查xml/aaf文件和wav文件！'
                    return msg

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


