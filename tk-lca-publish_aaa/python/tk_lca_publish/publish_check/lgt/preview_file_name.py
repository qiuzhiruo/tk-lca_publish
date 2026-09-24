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
import os
import re
import traceback
import production.pipeline.utils as pplu
from handle_frame import HandlePreviewFile


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的预览文件的路径和命名。"
        self.description = u"提交的预览文件名由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成。\n文件路径所在的各级文件夹命名不能有中文和空格。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        self.proj_name = ''
        self.shot_name = ''
        return

    def get_audio_file(self):
        current_shot = self.dialog.entity['name']
        proj = self.dialog.project['name']
        if not proj:
            self.dialog.print_log(
                'Dialog shot attr missing. Got "{0}"\nGet project name from imgs "{1}".'.format(proj, self.proj_name))
            proj = self.proj_name
        if not current_shot:
            self.dialog.print_log(
                'Dialog shot attr missing. Got "{0}"\nGet shot name from imgs "{1}".'.format(current_shot,
                                                                                             self.shot_name))
            current_shot = self.shot_name
        seq_auds = os.extsep.join([current_shot[:3], 'aud', 'audio'])
        audio_name = os.extsep.join([current_shot, 'wav'])
        audio_wave = os.sep.join([os.getenv('LC_PROJ_PATH', '/mnt/proj/projects'),
                                  proj.lower(),
                                  'preproduction',
                                  current_shot[:3],
                                  'story', 'aud', 'publish',
                                  seq_auds,
                                  audio_name])

        if audio_wave and os.path.isfile(audio_wave):
            self.dialog.shot_audio_file = audio_wave
            self.dialog.print_log('Audio file : ' + self.dialog.shot_audio_file)

    def run_check(self):
        try:
            l_preview_files = [str(self.dialog.w_file.listWidget_preview.item(i).text()) for i in
                               xrange(self.dialog.w_file.listWidget_preview.count())]
            l_preview_files = sorted(l_preview_files)
            if len(l_preview_files) == 0:
                return u"还没有选择文件。"
            frame_range_shotgun = None
            try:
                frame_range_shotgun = HandlePreviewFile.get_shot_framerange(self.dialog)
            except:
                return u'Shotgun 镜头信息获取失败'

            if not frame_range_shotgun[0] or not frame_range_shotgun[1]:
                return u'问题：shotgun上找不到frame range信息！\n解决办法：请联系PC填写cut in和cut out信息！'
            # del the preview files cut frames
            if self.dialog.version_tag in HandlePreviewFile.TAIL_FRAME:
                l_preview_files = HandlePreviewFile.cut_frame_upload(frame_range_shotgun, l_preview_files)
                if l_preview_files is None:
                    return u"请重新选择上传文件的分辨率 R1 or R2"

            self.dialog.l_preview_files = l_preview_files
            proj_ptn = re.compile(r'projects[/\\]([a-z]{3})[/\\]shot')
            shot_ptn = re.compile(r'shot[/\\][a-z][0-9]{2}[/\\]([a-z][0-9]{5})')
            is_proj = proj_ptn.search(l_preview_files[0])
            is_shot = shot_ptn.search(l_preview_files[0])
            if is_proj:
                self.proj_name = is_proj.group(1)
            if is_shot:
                self.shot_name = is_shot.group(1)

            frame_len_shotgun = int(frame_range_shotgun[1]) - int(frame_range_shotgun[0]) + 1
            if frame_len_shotgun == len(l_preview_files):
                try:
                    self.get_audio_file()

                except:
                    self.dialog.print_log(
                        u'Shotgun 未知错误,在当前Task Actions中 Launch Maya 或者在任意shot 的 Task Actions中 Create Folder 可解决问题.')
                    return traceback.format_exc()
            # publish 2026年3月19日 注释掉，不然影响了publish阶段的检查
            # if self.dialog.publish_mode == 1:
            #     return ''
            resolution_tag = ''
            if 'R1' in self.dialog.version_tag:
                resolution_tag = 'R1'
            elif 'R2' in self.dialog.version_tag:
                resolution_tag = 'R2'
            elif 'R3' in self.dialog.version_tag:
                return ''

            version_name = str(self.dialog.w_ver.lineEdit_version_name.text())[1:]
            preview_versoin = os.path.basename(os.path.dirname(os.path.dirname(l_preview_files[0])))
            if version_name != preview_versoin:
                return u'Preview序列的版本号与publish版本号不一致. Publish Version: ' + version_name + ' ,Preview Version: ' + preview_versoin

            l_exr_path = os.path.dirname(self.dialog.l_preview_files[0])
            l_jpg_dir = os.path.dirname(l_exr_path) + '/jpg_L'
            if not os.path.isdir(l_jpg_dir):
                return u'找不到对应的jpg L序列帧'
            self.dialog.l_jpg_seqs = pplu.findFiles(l_jpg_dir, '.jpg')

            if self.dialog.version_tag in HandlePreviewFile.TAIL_FRAME:
                self.dialog.l_jpg_seqs = HandlePreviewFile.cut_frame_upload(frame_range_shotgun, self.dialog.l_jpg_seqs)
                if self.dialog.l_jpg_seqs is None:
                    return u"请重新选择上传文件的分辨率 R1 or R2"

            if resolution_tag != '' and ('/' + resolution_tag + '/') not in l_preview_files[0]:
                return u'Tag中选择的分辨率是 ' + resolution_tag + u'，而Preview的分辨率与其不符。'

            invalid_exr = []
            for f in l_preview_files:
                if not re.match(str(self.dialog.entity['name']) + '\.lgt\.comp\.\d{4}\.exr$', \
                                os.path.basename(f)):
                    invalid_exr.append(f)
            if invalid_exr:
                return u'Preview的exr序列名称不合格，应该是 ' + self.dialog.entity['name'] + '.lgt.comp.####.exr ' + '\n'.join(
                    invalid_exr)

            if l_preview_files:
                frame_start = os.path.basename(l_preview_files[0]).split('.')[-2]
                frame_end = os.path.basename(l_preview_files[-1]).split('.')[-2]
                frame_range = [frame_start, frame_end]
                frame_len = len(l_preview_files)
                jpg_len = len(self.dialog.l_jpg_seqs)

                '''if frame_range_shotgun and frame_range and \
                    (int(frame_range[0]) != int(frame_range_shotgun[0]) or \
                     int(frame_range[1]) != int(frame_range_shotgun[1]) or \
                    frame_len_shotgun != frame_len ):
                    return u'Preview 下的序列帧起始结束帧不匹配,或者序列帧数量不对,exr: '+\
                           str(frame_range)+' shotgun: '+str(frame_range_shotgun)+\
                           u' 需要帧数 '+str(frame_len_shotgun)+u' 实际帧数 '+str(frame_len_shotgun)'''

                if int(frame_range[0]) != int(frame_range_shotgun[0]):
                    return u'Preview 下的序列帧起始帧不匹配, exr: ' + str(frame_range[0]) + ' shotgun: ' + str(
                        frame_range_shotgun[0])

                if int(frame_range[1]) != int(frame_range_shotgun[1]):
                    return u'Preview 下的序列帧结束帧不匹配, exr: ' + str(frame_range[1]) + ' shotgun: ' + str(
                        frame_range_shotgun[1])

                if frame_len_shotgun != frame_len:
                    return u'Preview 下的序列帧序列帧数量不对, 需要帧数 ' + str(frame_len_shotgun) + u' 实际帧数 ' + str(frame_len)

                if frame_len != jpg_len:
                    return u'jpg L与exr L长度不匹配, jpg: ' + str(jpg_len) + ' exr: ' + str(frame_len)
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
