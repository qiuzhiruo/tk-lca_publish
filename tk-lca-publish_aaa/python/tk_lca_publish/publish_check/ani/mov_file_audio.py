# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.09
#
# Description:  http://wiki.zhuiguang.com/x/RxvQ
#
############################################

import os
import traceback
import subprocess
import hashlib
import sys

import production.audio as audio

COMMON_PATTERNS = ['Comment', 'Info', 'Movie/Comment']


# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
    http://wiki.zhuiguang.com/x/RxvQ
    """

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"mov文件中的声音。"
        self.description = u"mov文件中的声音必需是标注路径中的声音，" \
                           u"声音文件的起始要和镜头的起始帧一致，且长度一致。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_possible_duration(self):
        """

        Returns (list): [112]
        """
        durations = []
        shot = self.dialog.sg.find_one(
            'Shot',
            [['id', 'is', self.dialog.entity['id']]],
            ['sg_cut_in', 'sg_cut_out', 'sg_cut_duration', 'sg_ani_cut_in', 'sg_ani_cut_out']
        )

        if shot['sg_ani_cut_in'] is not None \
                and shot['sg_ani_cut_out'] is not None \
                and self.dialog.step['name'] == 'ani':
            durations.append(shot['sg_ani_cut_out'] - shot['sg_ani_cut_in'] + 1)

        elif shot['sg_cut_in'] is not None \
                and shot['sg_cut_out'] is not None:
            durations.append(shot['sg_cut_out'] - shot['sg_cut_in'] + 1)
        return durations

    def run_check(self):

        try:
            shot_name = self.dialog.entity['name']
            seq_name = shot_name[:3]

            # for some ani test seq, we ignore the audio check
            if self.dialog.step['name'] == 'ani' \
                    and seq_name in ['z88']:
                return ""

            versions = self.dialog.sg.find(
                'Version',
                [['project', 'is', self.dialog.project],
                 ['entity', 'name_is', seq_name],
                 ['sg_task', 'name_is', 'audio']],
                ['code', 'sg_version_folder'],
                order=[{'field_name': 'created_at', 'direction': 'desc'}, ]
            )
            if not versions:
                return ""

            # latest audio file, -- *.wav  latest_wav_file
            latest_wav_file = os.path.join(
                versions[0]['sg_version_folder']['local_path'],
                shot_name + '.wav')
            if not os.path.isfile(latest_wav_file):
                self.dialog.print_log(u"这个镜头剪辑没有提供音频文件。")
                return ""

            latest_wav_file = latest_wav_file.replace('\\', '/')

            # print 'self.dialog.l_mov_info: ', self.dialog.l_mov_info
            if 'Comment' in self.dialog.l_mov_info:
                i = self.dialog.l_mov_info.index('Comment')
            elif 'Movie/Comment' in self.dialog.l_mov_info:
                i = self.dialog.l_mov_info.index('Movie/Comment')
            # from mov commit..
            wav_path_from_mov = self.dialog.l_mov_info[i + 3].replace('\\', '/')
            if sys.platform == 'linux2':
                wav_path_from_mov = wav_path_from_mov.replace('Z:/', '/mnt/proj/')
            else:
                wav_path_from_mov = wav_path_from_mov.replace('/mnt/proj/', 'Z:/')

            if not wav_path_from_mov.endswith('.wav'):
                return u"Preview Mov必需带上这个镜头的声音文件: " + latest_wav_file

            if not os.path.isfile(wav_path_from_mov):
                return u"Preview Mov使用的音频已经不存在： " + wav_path_from_mov

            if not latest_wav_file == wav_path_from_mov:
                with open(latest_wav_file, 'rb') as f:
                    data = f.read()
                    md5 = hashlib.md5(data)
                    hash_latest = md5.hexdigest()

                self.dialog.print_log(u'Audio file( latest): %s, hash value: %s' % (latest_wav_file, hash_latest))

                with open(wav_path_from_mov, 'rb') as f:
                    data = f.read()
                    md5 = hashlib.md5(data)
                    hash_value = md5.hexdigest()

                self.dialog.print_log(u'Audio file( in use): %s, hash value: %s' % (wav_path_from_mov, hash_value))

                # 文件名不一致的时候，判断俩音频文件是不是同一个文件
                if hash_value != hash_latest:
                    return u"Preview Mov使用的音频文件不是最新的\n当前是: " + wav_path_from_mov + \
                           u' \n请使用: ' + latest_wav_file + u' 重新拍屏或预渲染。'

            cut_in, cut_out = self.dialog.l_mov_info[i + 1].split('-')
            durations = self.get_possible_duration()
            # durations.insert(0, int(audio.getDuration(wav_path_from_mov)) )
            duration_video = int(float(cut_out) - float(cut_in)) + 1

            if duration_video not in durations:
                return u"Preview Mov使用的音频时长与视频时长不一致。" \
                       u"\n视频时长：%s, 音频及shotgun上时长：%s" % (duration_video, durations)

            try:
                # get audio offset from mov commit info
                aof = str(int(float(self.dialog.l_mov_info[i + 4])))
            except:
                print 'No valid audio offset info. Skip'
                return ""

            if aof != cut_in and \
                    self.dialog.step['name'] != 'ani':
                return u"音频在" + aof + u"帧开始。视频在" + cut_in + \
                       u"帧开始。\n在Downstream Publish过程中要求音频视频起始一致。" \
                       u"制作人员不能自己调整音频文件起始时间。" \
                       u"\n如果音频不满足要求，需要找剪辑人员重新publish该镜头的音频文件。"

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
