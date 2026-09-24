# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Xiangquan
#
# Date: 2016.01
#
# Description:
#
############################################

import os
import traceback
import shutil

import production.audio as audio

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"设定镜头剪辑时长"
        self.description = u"确定每个镜头的剪辑时长。"
        return

    def clear_ani_inout(self, shot_name, shot_id):
        """
        if shot's sg_ani_cut_in/sg_ani_cut_out is not empty, then set it to.
        """
        result = self.dialog.sg.find_one('Shot', [['project', 'name_is', self.dialog.project['name']],
                                                  ['code', 'is', shot_name]],
                                         ['sg_ani_cut_in', 'sg_ani_cut_out'])
        if result.has_key('sg_ani_cut_in'):
            self.dialog.sg.update('Shot', shot_id, {'sg_ani_cut_in': None})
        if result.has_key('sg_ani_cut_out'):
            self.dialog.sg.update('Shot', shot_id, {'sg_ani_cut_out': None})

    def compare_shot_range(self, shot_name, new_dur):
        """
        compare old shot cut duration with new values, if they are different, record it to description
        return a list or None: [shot_name, old_dur ,new_dur]
        """
        result = self.dialog.sg.find_one('Shot', [['project', 'name_is', self.dialog.project['name']],
                                                  ['code', 'is', shot_name]],
                                         ['sg_cut_duration'])
        if not result['sg_cut_duration']:
            return None

        old_dur = int(result['sg_cut_duration'])
        if old_dur != int(new_dur):
            return [shot_name, old_dur, new_dur]
        else:
            return None

    def write_diff_shots_description(self, diff_shots):
        """
        """
        version_info = self.dialog.sg.find_one('Version', [['project', 'is', self.dialog.project],
                                                           ['code', 'is', self.dialog.version_name]],
                                               ['id', 'description'])
        if not diff_shots:
            desc = version_info['description'].decode('utf-8') + '\n{无时长变化}'
        else:
            txt = u'镜头号 旧时长 新时长\n'
            for shot_name in sorted(diff_shots.keys()):
                txt += u' %s    %d    %d\n' % \
                       (shot_name, int(diff_shots[shot_name][0]), int(diff_shots[shot_name][1]))

            desc = version_info['description'].decode('utf-8') + '\n{' + txt + '}'
        self.dialog.description = desc
        self.dialog.sg.update('Version', version_info['id'], {'description': desc})

    def proceed(self):
        try:
            task_name = self.dialog.version_name.split('.')[-2]
            l_seq_shots = self.dialog.sg.find('Shot', [['project', 'name_is', self.dialog.project['name']],
                                                       ['sg_status_list', 'is_not', 'omt'],
                                                       ['sg_sequence', 'is', self.dialog.entity]],
                                              ['code', 'sg_cut_in', 'sg_cut_out', 'sg_cut_duration'])
            d_seq_shots = {}
            for shot in l_seq_shots:
                # if the cut_in of the shot is None, set it to 1001
                if shot['sg_cut_in'] == None:
                    self.dialog.sg.update('Shot', shot['id'], {'sg_cut_in': 1001})
                # apply to the dict
                d_seq_shots[shot['code']] = shot

            modify_duration = True
            wrong_shots = []
            diff_shots = {}
            self.dialog.confirmed_by_pc = False
            for wav_item_path in self.dialog.wav_files:  # from publish_process/aud/cut_seq_wav.py
                shot_name = os.path.basename(wav_item_path)[:6]
                audio_dur_int = int(round(audio.getDuration(wav_item_path)))
                audio_duration = str(audio_dur_int)
                self.dialog.print_log('audio_duration ' + audio_duration)
                self.dialog.print_log('sg_cut_duration ' + str(d_seq_shots[shot_name]['sg_cut_duration']))
                if d_seq_shots[shot_name]['sg_cut_duration'] != audio_dur_int:
                    lgt_status = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name']],
                                                                  ['entity', 'name_is', shot_name],
                                                                  ['content', 'is', 'lighting']],
                                                         ['sg_status_list'])['sg_status_list']
                    # if ani status is not in the list, modifying shot duration should be confirmed by pc
                    if lgt_status not in ['wtg', 'ip', 'rdy', 'hld','omt'] and \
                            self.dialog.project['name'].upper() not in ['YZC']:
                        self.dialog.print_log(shot_name + ' need to be confirmed by pc:' + lgt_status)
                        self.dialog.confirmed_by_pc = True
                        continue

                    self.dialog.print_log(shot_name + ' reset shot duration:' + lgt_status)
                    if task_name == 'audio':
                        result = self.compare_shot_range(shot_name, audio_duration)
                        self.dialog.print_log(u'result: ' + str(result))
                        if result:
                            diff_shots[result[0]] = result[1:]

                        self.dialog.sg.update('Shot', d_seq_shots[shot_name]['id'], {'sg_cut_duration': audio_dur_int})
                        self.dialog.print_log(u'镜头' + shot_name + u'更新 Duration为 ->' + audio_duration)
                    else:  # elif task_name in ['xiaolai', 'head']
                        self.dialog.print_log(
                            u'镜头' + shot_name + u'音频 Duration ->' + audio_duration + u'; Shotgun时长 ->' + str(
                                d_seq_shots[shot_name]['sg_cut_duration']))
                        modify_duration = False
                        wrong_shots.append(shot_name)

                # clear ani in/out data
                if task_name == 'audio':
                    self.clear_ani_inout(shot_name, d_seq_shots[shot_name]['id'])

            if not modify_duration:
                return u'当前的任务%s无法更新以下镜头的Duration：\n' % task_name + '\n'.join(wrong_shots)

            if diff_shots:
                self.write_diff_shots_description(diff_shots)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description


