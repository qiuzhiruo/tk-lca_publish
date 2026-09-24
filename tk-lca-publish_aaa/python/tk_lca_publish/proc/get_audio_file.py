# -*- coding:utf-8 -*-

import os

def get_audio(root, proj, shot_name):
    if not len(shot_name) == 6:
        return u'错误: 无效的镜头号 '+shot_name

    seq_name = shot_name[:3]
    audio_file = root + '/projects/' + proj.lower() + '/preproduction/'+seq_name+'/story/aud/publish/' + seq_name + '.aud.audio/' + shot_name + '.wav'

    if not os.path.isfile(audio_file):
        return '错误: 无法找到音频文件 ' + audio_file

    return audio_file

