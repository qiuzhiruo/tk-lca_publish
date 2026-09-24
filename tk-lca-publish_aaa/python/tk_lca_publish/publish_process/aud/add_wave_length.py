# -*- coding: utf-8 -*-
import os
import sys


from .wave_tools import add_wave_length

class StdProcess(object):
    def __init__(self, dialog):
        self.dialog = dialog

    def get_process_name(self):
        return u'Add Wave Length'

    def get_description(self):
        return u'给每个镜头wav末尾补1个采样帧静音，修复RV帧数显示bug'

    def proceed(self):
        dialog = self.dialog
        if not getattr(dialog, 'is_add_wave_length', False):
            return ''

        # dialog.wav_files 是 list，每个元素是 wav 文件路径
        wav_files = getattr(dialog, 'wav_files', [])
        if not wav_files:
            return ''

        # 统一临时目录：原目录 + '_auto_fix_wav' 后缀
        # 例: /proj/seq/story/aud/task/final_cut/ → /proj/seq/story/aud/task/final_cut_auto_fix_wav/
        first_wav_dir = os.path.dirname(wav_files[0])
        output_dir = first_wav_dir + '_auto_fix_wav'
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        else:
            for f in os.listdir(output_dir):
                fp = os.path.join(output_dir, f)
                if os.path.isfile(fp):
                    os.remove(fp)

        new_wav_files = []
        for wav_path in wav_files:
            if not os.path.isfile(wav_path):
                new_wav_files.append(wav_path)
                continue
            try:
                wav_name = os.path.basename(wav_path)
                out_path = os.path.join(output_dir, wav_name)
                add_wave_length(wav_path, extra_samples=1, output_file=out_path)
                new_wav_files.append(out_path)
            except Exception as e:
                print(e)
                return u'Add wave length failed for %s: %s' % (wav_path, str(e))

        # 更新 dialog.wav_files 指向临时目录的新文件
        dialog.wav_files = new_wav_files
        return ''
