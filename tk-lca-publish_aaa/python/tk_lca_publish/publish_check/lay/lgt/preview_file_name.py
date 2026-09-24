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

def get_shot_framerange(dialog):
    projFilter = [ ['name', 'is', str(dialog.project['name'])] ]
    shotgunProjInfo = dialog.sg.find_one('Project', projFilter)

    shotFilter = [
        ['code', 'is', dialog.entity['name']],
        ['project', 'is', {'type': 'Project', 'id': shotgunProjInfo['id']}]
        ]
    info = dialog.sg.find_one('Shot', shotFilter, ['sg_sequence', 'sg_cut_in', 'sg_cut_out','sg_head_in', 'sg_tail_out'])


    frame_range=[]
    if info:
        cut_in=info['sg_cut_in']
        head_in=info['sg_head_in']
        if head_in:
            frame_range.append( head_in)
        else:
            frame_range.append( cut_in)

        cut_out=info['sg_cut_out']
        tail_out=info['sg_tail_out']
        if tail_out:
            frame_range.append( tail_out)
        else:
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


    def run_check(self):
        l_preview_files = [str(self.dialog.w_file.listWidget_preview.item(i).text()) for i in xrange(self.dialog.w_file.listWidget_preview.count())]
        l_preview_files=sorted(l_preview_files)
        if len(l_preview_files) == 0:
            return u"还没有选择文件。"
        self.dialog.l_preview_files = l_preview_files

        try:
            if self.dialog.publish_mode==1:
                return ''
            version_name=str(self.dialog.w_ver.lineEdit_version_name.text())[1:]
            preview_versoin = os.path.basename(os.path.dirname(os.path.dirname(l_preview_files[0])))
            if version_name!=preview_versoin:
                return u'Preview序列的版本号与publish版本号不一致. Publish Version: '+version_name+' ,Preview Version: '+preview_versoin

            resolution_tag=''
            if 'R1' in self.dialog.version_tag:
                resolution_tag='R1'
            elif 'R2' in self.dialog.version_tag:
                resolution_tag='R2'
            elif 'R3' in self.dialog.version_tag:
                resolution_tag='R3'
            if ('/'+resolution_tag+'/') not in l_preview_files[0]:
                return u'Tag中选择的分辨率是 '+resolution_tag+u'，而Preview的分辨率与其不符。'

            frame_range_shotgun=None
            try:
                frame_range_shotgun = get_shot_framerange(self.dialog)
            except:
                return u'Shotgun 镜头信息获取失败'

            if not frame_range_shotgun:
                return u'找不到shotgun的frame range信息'

            frame_len_shotgun=int(frame_range_shotgun[1])-int(frame_range_shotgun[0])+1

            invalid_exr=[]
            for f in l_preview_files:
                if not re.match(str(self.dialog.entity['name'])+'\.lgt\.comp\.\d{4}\.exr$',\
                   os.path.basename(f)):
                    invalid_exr.append(f)
            if invalid_exr:
                return u'Preview的exr序列名称不合格，应该是 '+self.dialog.entity['name']+'.lgt.comp.####.exr '+'\n'.join(invalid_exr)

            frame_range=[]
            if l_preview_files:
                frame_start=os.path.basename(l_preview_files[0]).split('.')[-2]
                frame_end=os.path.basename(l_preview_files[-1]).split('.')[-2]
                frame_range=[frame_start,frame_end]
                frame_len=len(l_preview_files)

                if frame_range_shotgun and frame_range and \
                    (int(frame_range[0]) != int(frame_range_shotgun[0]) or \
                     int(frame_range[1]) != int(frame_range_shotgun[1]) or \
                    frame_len_shotgun != frame_len ):
                    return u'Preview 下的序列帧起始结束帧不匹配,或者序列帧数量不对,exr: '+\
                           str(frame_range)+' shotgun: '+str(frame_range_shotgun)+\
                           u' 需要帧数 '+str(frame_len_shotgun)+u' 实际帧数 '+str(frame_len_shotgun)

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


