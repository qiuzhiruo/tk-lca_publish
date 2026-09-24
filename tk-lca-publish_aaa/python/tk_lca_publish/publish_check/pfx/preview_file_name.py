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

import traceback

import os
import re
import production.pipeline.utils as pplu

def get_shot_framerange(dialog):
    projFilter = [ ['name', 'is', str(dialog.project['name'])] ]
    shotgunProjInfo = dialog.sg.find_one('Project', projFilter)

    shotFilter = [
        ['code', 'is', dialog.entity['name']],
        ['project', 'is', {'type': 'Project', 'id': shotgunProjInfo['id']}]
        ]
    info = dialog.sg.find_one('Shot', shotFilter, ['sg_sequence', 'sg_cut_in', 'sg_cut_out'])


    frame_range=[]
    if info:
        cut_in=info['sg_cut_in']
        frame_range.append( cut_in)

        cut_out=info['sg_cut_out']
        frame_range.append( cut_out)
        return frame_range

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的预览文件的路径和命名。"
        self.description = u"提交的预览文件名由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成。\n文件路径所在的各级文件夹命名不能有中文和空格。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_audio_file(self):
        current_shot=self.dialog.entity['name']

        audio_wave=os.path.join(os.getenv('LC_PROJ_PATH')+'/'+str(self.dialog.project['name']).lower(),
                            'preproduction',
                            current_shot[:3],
                            'story/aud/publish/',
                            current_shot[:3]+'.aud.audio',
                            current_shot+'.wav')
        
        if audio_wave and  os.path.isfile(audio_wave):
            self.dialog.shot_audio_file=audio_wave
            self.dialog.print_log('Audio file : '+self.dialog.shot_audio_file)


    def run_check(self):
        try:
            l_preview_files = [str(self.dialog.w_file.listWidget_preview.item(i).text()) for i in xrange(self.dialog.w_file.listWidget_preview.count())]
            l_preview_files=sorted(l_preview_files)
            if len(l_preview_files) == 0:
                return u"还没有选择文件。"
            self.dialog.l_preview_files = l_preview_files

            frame_range_shotgun=None
            try:
                frame_range_shotgun = get_shot_framerange(self.dialog)
            except:
                return u'Shotgun 镜头信息获取失败'

            if not frame_range_shotgun:
                return u'找不到shotgun的frame range信息'

            frame_len_shotgun=int(frame_range_shotgun[1])-int(frame_range_shotgun[0])+1
            if frame_len_shotgun==len(l_preview_files):
                self.get_audio_file()


            if self.dialog.publish_mode==1:
                return ''
            version_name=str(self.dialog.w_ver.lineEdit_version_name.text())[1:]
            preview_versoin = os.path.basename(os.path.dirname(os.path.dirname(l_preview_files[0])))
            if version_name!=preview_versoin:
                return u'Preview序列的版本号与publish版本号不一致. Publish Version: '+version_name+' ,Preview Version: '+preview_versoin

            l_exr_path=os.path.dirname(self.dialog.l_preview_files[0])
            l_jpg_dir=os.path.dirname(l_exr_path)+'/jpg_L'
            if not os.path.isdir(l_jpg_dir):
                return u'找不到对应的jpg L序列帧'
            self.dialog.l_jpg_seqs=pplu.findFiles(l_jpg_dir,'.jpg')

            invalid_exr=[]
            for f in l_preview_files:
                if self.dialog.task['name']=='paint_fix':
                    if not re.match(str(self.dialog.entity['name'])+'\.pfx\.paint_fix\.\d{4}\.exr$',\
                       os.path.basename(f)):
                        invalid_exr.append(f)
                elif self.dialog.task['name']=='floating_window':
                    if not re.match(str(self.dialog.entity['name'])+'\.pfx\.floating_window\.\d{4}\.exr$',\
                       os.path.basename(f)):
                        invalid_exr.append(f)
            if invalid_exr:
                if self.dialog.task['name']=='paint_fix':
                    return u'Preview的exr序列名称不合格，应该是 '+self.dialog.entity['name']+'.pfx.paint_fix.####.exr '+'\n'.join(invalid_exr)
                elif self.dialog.task['name']=='floating_window':
                    return u'Preview的exr序列名称不合格，应该是 '+self.dialog.entity['name']+'.pfx.floating_window.####.exr '+'\n'.join(invalid_exr)

            frame_range=[]
            if l_preview_files:
                frame_start=os.path.basename(l_preview_files[0]).split('.')[-2]
                frame_end=os.path.basename(l_preview_files[-1]).split('.')[-2]
                frame_range=[frame_start,frame_end]
                frame_len=len(l_preview_files)
                jpg_len=len(self.dialog.l_jpg_seqs)
                if frame_range_shotgun and frame_range and \
                    (int(frame_range[0]) != int(frame_range_shotgun[0]) or \
                     int(frame_range[1]) != int(frame_range_shotgun[1]) or \
                    frame_len_shotgun != frame_len ):
                    return u'Preview 下的序列帧起始结束帧不匹配,或者序列帧数量不对,exr: '+\
                           str(frame_range)+' shotgun: '+str(frame_range_shotgun)+\
                           u' 需要帧数 '+str(frame_len_shotgun)+u' 实际帧数 '+str(frame_len_shotgun)

                if frame_len!=jpg_len:
                    return u'jpg L与exr L长度不匹配, jpg: '+str(jpg_len)+' exr: '+str(frame_len)
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


