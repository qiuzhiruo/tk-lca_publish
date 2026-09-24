# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback

import os
import re
import sys
import edt.edt_cut_xml.cut_xml_main as cxm;reload(cxm)
import edt.aaf_analyse.edt_funcs as edt_funcs;reload(edt_funcs)

PATTERN = '^[a-z][0-9]{5}$'

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"版本技术描述"
        self.description = u"从xml/aaf中检查版本技术描述"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            if not self.dialog.xml_file and not self.dialog.aaf_file:
                self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(u"未提供sequence xml/aaf，无分析结果")
                return ''
            
            is_from_stb = self.dialog.w_publish_file.stb_checkbox.isChecked()
            if not is_from_stb:
                self.dialog.edit_status_dict = {}
                # split_shots = {'b60190': [('b60190.lgt.lighting.v006.mov', (0, 117), (1658, 1775), 'mov'),('b60190.lgt.lighting.v006.mov', (33, 34),(1697, 1826),  'stillframe')]}
                if self.dialog.xml_file:
                    split_shots, _ = cxm.get_orignal_xml_shot_splits(self.dialog.video_file_nodes, self.dialog.efficient_shot_items_dict, specific_key= self.dialog.entity['name'])

                elif self.dialog.aaf_file:
                    split_shots = edt_funcs.get_shot_items_dict(self.dialog.aaf_no_track_merge_result, self.dialog.aaf_obj.mov_urls_keys)
                    self.dialog.print_log('split_shots:' + str(split_shots))

                illegal_shot_names = []
                for key in sorted(split_shots.keys()):
                    m = re.match(PATTERN, key)
                    if m is None:
                        illegal_shot_names.append(key)

                if illegal_shot_names:
                    msg = u'xmll/aaf里有以下不规范命名：\n'
                    msg += '\n'.join(illegal_shot_names)
                    msg += '\n'
                    return msg

                self.dialog.edit_status_dict = self.check_shots_edit_status(split_shots, self.dialog.project['name'])
                self.update_edit_status_dict()
                self.tech_summary(self.dialog.edit_status_dict)
                # print message
                self.dialog.print_log("final self.dialog.edit_status_dict: \n")
                for shot_name in self.dialog.edit_status_dict:
                    self.dialog.print_log(shot_name + ': ' + str(self.dialog.edit_status_dict[shot_name]))
            else:
                    self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(u"storyboard 模式，无分析结果")
            
            return ''
        except:
            return traceback.format_exc()
    
    def check_shots_edit_status(self, split_shots, proj_name):
        """
        return a dict, e.g. edit_status_dict = {shot_name: (source_start, source_end, length, cut_head, cut_tail, cutoff_frames, extend_frames)}
        """
        edit_status_dict = {}
        for shot_name in split_shots:
            version_name = split_shots[shot_name][0][0].replace('.mov', '')
            try:
                version_frame_count = self.dialog.sg.find_one('Version', [['project', 'name_is', proj_name], ['code', 'is', version_name]], 
                                     ['frame_count'])['frame_count']
            except:
                version_frame_count = 100
                self.dialog.print_log(shot_name + ' not last version frame_count , set version_frame_cout to default 100')
            
            source_start = split_shots[shot_name][0][1][0]
            source_end = split_shots[shot_name][0][1][1]
            length = 0
            cutoff_frames = False
            extend_frames = False
            cut_head = 0
            cut_tail = 0
            for clip in split_shots[shot_name]:
                source_range = clip[1]          #e.g. (0, 117)
                # if source_end + 1 < source_range[0]:
                if source_end < source_range[0]:
                    cutoff_frames = True
                if source_range[0] < source_start:
                    source_start = source_range[0]
                if source_range[1] > source_end:
                    source_end = source_range[1]
                length += source_range[1] - source_range[0]
            
            if length > version_frame_count:
                extend_frames = True
            if source_start > 0:
                cut_head = source_start
            if source_end < version_frame_count:
                cut_tail = version_frame_count - source_end
            edit_status_dict[shot_name] = (source_start, source_end, length, cut_head, cut_tail, cutoff_frames, extend_frames, version_frame_count)
        
        return edit_status_dict


    def update_edit_status_dict(self):
        """
        keep updated wav shots only!
        :return:
        """
        if not self.dialog.w_publish_file.seq_checkbox.isChecked():
            new_dict = {}
            for wav_item_path in self.dialog.wav_files:  # from publish_process/aud/cut_seq_wav.py
                shot_name = os.path.basename(wav_item_path)[:6]
                if shot_name in self.dialog.lack_of_shots:
                    self.dialog.print_log('miss shot in xml/aaf: ' + shot_name + '\n')
                    continue
                new_dict[shot_name] = self.dialog.edit_status_dict[shot_name]
            self.dialog.edit_status_dict = new_dict


    def tech_summary(self, edit_status_dict):
        """
        e.g. edit_status_dict = {shot_name: (source_start, source_end, length, cut_head, cut_tail, cutoff_frames, extend_frames, version_frame_count)}
        """
        l_msgs = []
        l_msgs.append(u"镜头号      时长    剪头     剪尾      抽帧     延长")

        for shot_name in sorted(edit_status_dict.keys()):
            cut_head = False if edit_status_dict[shot_name][3] == 0 else True
            cut_tail = False if edit_status_dict[shot_name][4] == 0 else True
            short_mov = edit_status_dict[shot_name][5]
            extend_mov = edit_status_dict[shot_name][6]
            if cut_head or cut_tail or short_mov or extend_mov:
                msg = u'%s  %04d   %04d   %04d    %s    %s' % (shot_name, edit_status_dict[shot_name][2], edit_status_dict[shot_name][3],
                                                               edit_status_dict[shot_name][4],  str(edit_status_dict[shot_name][5]), str(edit_status_dict[shot_name][6]))
                l_msgs.append(msg)
        self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(u"\n".join(l_msgs))
        
    
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


