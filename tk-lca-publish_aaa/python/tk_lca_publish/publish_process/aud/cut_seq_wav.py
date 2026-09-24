# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import subprocess
import os
import sys
import shutil

import edt.edt_cut_xml.cut_xml_main as cxm; reload(cxm)
import edt.edt_analyse.processAudio as processAudio; reload(processAudio)
import edt.aaf_analyse.aaf_funcs as aaf_funcs;reload(aaf_funcs)
import edt.aaf_analyse.utilities as aaf_util;reload(aaf_util)

# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"切分sequence wav"
        self.description = u"切分sequence wav"
        return

    def cut_wav_from_xml(self):
        is_from_stb = self.dialog.w_publish_file.stb_checkbox.isChecked()  # check if the wav and xml are from a storyboard fcp
        shots_ordered = {}
        if not is_from_stb:
            # e.g. split_shots = {'b60190': [('b60190.lgt.lighting.v006.mov', (0, 117), (1658, 1775), 'mov'), ('b60190.lgt.lighting.v006.mov', (33, 34),(1697, 1826),  'stillframe')]}
            split_shots, _ = cxm.get_orignal_xml_shot_splits(self.dialog.video_file_nodes,
                                                             self.dialog.efficient_shot_items_dict,
                                                             specific_key = self.dialog.entity['name'])
            for shot_name in split_shots:
                xml_start = split_shots[shot_name][0][2][0]
                shots_ordered[xml_start] = shot_name
        else:
            # e.g. {'c30010': [0, 140], 'c30020': [140, 201], ...,  'c30950': [6738, 6848]}
            self.dialog.print_log('storyboard mode')
            split_shots = self.dialog.shot_ranges  # self.dialog.shot_ranges is from publish_check/aud/check_xml_file.py
            for shot_name in split_shots:
                xml_start = split_shots[shot_name][0]
                shots_ordered[xml_start] = shot_name

        return shots_ordered, split_shots


    def cut_wav_from_aaf(self):
        """

        :return:
        """
        shots_ordered = {}

        # self.dialog.aaf_no_track_merge_result: from publish_check/aud/check_xml_file.py, init_vars()
        shot_ranges = aaf_util.get_orignal_shot_range(self.dialog.aaf_no_track_merge_result, task = '')
        self.dialog.print_log('shot_ranges\n' + str(shot_ranges) )
        # shot_ranges = {u'c30030': [(177, 300)], u'c30020': [(116, 177)], u'c30010': [], u'c30070': [(453, 465)], u'c30060': [(300, 453)]}
        for shot_name in shot_ranges:
            aaf_start = shot_ranges[shot_name][0][0]
            shots_ordered[aaf_start] = shot_name

        return shots_ordered, shot_ranges

    def proceed(self):
        try:
            if not self.dialog.w_publish_file.seq_checkbox.isChecked():  # shot mode
                return ''

            is_from_stb = self.dialog.w_publish_file.stb_checkbox.isChecked()

            if self.dialog.xml_file:
                shots_ordered, split_shots = self.cut_wav_from_xml()
            elif self.dialog.aaf_file:
                shots_ordered, shot_ranges = self.cut_wav_from_aaf()

            clip_starts = sorted(shots_ordered.keys())
            offset = clip_starts[0] - 1
            seq_wav = self.dialog.wav_files[0]
            wav_dir = os.path.dirname(seq_wav)
            wav_dir_output = os.path.join(wav_dir + '_shots').replace('\\', '/')
            if not os.path.exists(wav_dir_output):
                os.mkdir(wav_dir_output)
                os.chmod(wav_dir_output, 0777)
            else:
                import glob
                contents = glob.glob(wav_dir_output + '/*')
                for content in contents:
                    os.remove(content)

            self.dialog.wav_files = []
            for index in clip_starts:
                shot_name = shots_ordered[index]

                # 修改过滤逻辑：同时考虑 exclusive_shots 和 inclusive_shots
                if hasattr(self.dialog, 'inclusive_shots') and self.dialog.inclusive_shots:
                    # 如果指定了"只更新的镜头号"，跳过不在列表中的镜头
                    if shot_name not in self.dialog.inclusive_shots:
                        continue
                elif hasattr(self.dialog, 'exclusive_shots') and shot_name in self.dialog.exclusive_shots:
                    # 如果指定了"不需更新的镜头号"，跳过在列表中的镜头
                    continue

                if self.dialog.xml_file:
                    shot_clips = split_shots[shot_name]
                    if not is_from_stb:
                        start = shot_clips[0][2][0] - offset
                        end = shot_clips[-1][2][1] - offset - 1
                    else:
                        self.dialog.print_log('storyboard mode split wav')
                        start = shot_clips[0] - offset
                        end = shot_clips[1] - offset - 1

                elif self.dialog.aaf_file:
                    shot_clips = shot_ranges[shot_name]
                    start = shot_clips[0][0]
                    end = shot_clips[-1][1]


                output_wav = os.path.join(wav_dir_output, shot_name + '.wav').replace('\\', '/')
                result = processAudio.cut_wav_left_closed_right_open(seq_wav, start, end, output_wav)
                if result:
                    self.dialog.print_log(shot_name + ': ' + result)
                    return result
                else:
                    self.dialog.print_log(shot_name + ': ' + output_wav)
                    self.dialog.wav_files.append(output_wav)

            return ''

        except:
            return traceback.format_exc()
    


    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
    
    
    



