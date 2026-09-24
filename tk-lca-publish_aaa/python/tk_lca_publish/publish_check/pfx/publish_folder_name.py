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
        frame_range=[info['sg_cut_in'],info['sg_cut_out']]
        return frame_range

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的渲染文件的文件夹命名。"
        self.description = u"提交的文件夹名由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成。\n的各级文件夹命名不能有中文和空格。文件夹彼此不能重名。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            return self.do_run_check()
        except:
            return traceback.format_exc()

    def do_run_check(self):
        l_folder=str(self.dialog.w_publish_file.lineEdit_lseq.text())
        r_folder=str(self.dialog.w_publish_file.lineEdit_rseq.text())
        self.dialog.nk_file=str(self.dialog.w_publish_file.lineEdit_nk.text())

        if l_folder and not os.path.isdir(l_folder):
            return u'L 文件夹路径找不到'
        if r_folder and not os.path.isdir(r_folder):
            return u'R 文件夹路径找不到'

        ## --------------check nuke file name
        if not self.dialog.nk_file:
            return  u'必须选择nk文件'

        if self.dialog.task['name']=='paint_fix':
            if not re.match(str(self.dialog.entity['name'])+'\.pfx\.paint_fix\.v\d{3}.nk$', os.path.basename(self.dialog.nk_file)):
                return u'nk文件不合格，应该是 '+self.dialog.entity['name']+'.pfx.paint_fix.v###.nk'
        elif self.dialog.task['name']=='floating_window':
            if not re.match(str(self.dialog.entity['name'])+'\.pfx\.floating_window\.v\d{3}.nk$', os.path.basename(self.dialog.nk_file)):
                return u'nk文件不合格，应该是 '+self.dialog.entity['name']+'.pfx.floating_window.v###.nk'

        ## -----------get shotgun frame range
        frame_range_shotgun=None
        try:
            frame_range_shotgun = get_shot_framerange(self.dialog)
        except:
            return u'Shotgun 镜头信息获取失败'

        if not frame_range_shotgun:
            return u'找不到shotgun的frame range信息'

        frame_len_shotgun=int(frame_range_shotgun[1])-int(frame_range_shotgun[0])+1


        self.dialog.l_seqs=[]
        self.dialog.r_seqs=[]
        old_tag=self.dialog.version_tag

        ## -------------check l exr
        if l_folder:
            all_files=os.listdir(l_folder)
            self.dialog.l_seqs=pplu.findFiles(l_folder,'.exr')

            l_jpg_dir=os.path.dirname(l_folder)+'/jpg_L'
            if not os.path.isdir(l_jpg_dir):
                return u'找不到对应的jpg L序列帧'
            self.dialog.l_jpg_seqs=pplu.findFiles(l_jpg_dir,'.jpg')

            if len(all_files)!=len(self.dialog.l_seqs):
                for rs in self.dialog.l_seqs:
                    all_files.remove(os.path.basename(rs))
                return u'L下包含非exr序列的文件'+'\n'.join(all_files)

            invalid_exr=[]
            for f in self.dialog.l_seqs:
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
                    return u'L下的exr序列名称不合格，应该是 '+self.dialog.entity['name']+'.pfx.paint_fix.####.exr '+'\n'.join(invalid_exr)
                elif self.dialog.task['name']=='floating_window':
                    return u'L下的exr序列名称不合格，应该是 '+self.dialog.entity['name']+'.pfx.floating_window.####.exr '+'\n'.join(invalid_exr)

            frame_range=[]
            if self.dialog.l_seqs:
                frame_start=os.path.basename(self.dialog.l_seqs[0]).split('.')[-2]
                frame_end=os.path.basename(self.dialog.l_seqs[-1]).split('.')[-2]
                frame_range=[frame_start,frame_end]
                frame_len=len(self.dialog.l_seqs)
                jpg_len=len(self.dialog.l_jpg_seqs)

                if frame_range_shotgun and frame_range and \
                    (int(frame_range[0]) != int(frame_range_shotgun[0]) or \
                     int(frame_range[1]) != int(frame_range_shotgun[1]) or \
                    frame_len_shotgun != frame_len ):
                    return u'L 下的序列帧起始结束帧不匹配,或者序列帧数量不对,exr: '+str(frame_range)+' shotgun: '+str(frame_range_shotgun)
                if frame_len!=jpg_len:
                    return u'jpg L与exr L长度不匹配, jpg:'+str(jpg_len)+'exr:'+str(frame_len)

                old_tag+=' L'
                # self.dialog.print_log('L exr: '+str(frame_range)+' shotgun: '+str(frame_range_shotgun)+'\n')
            else:
                return u'没有 L 的exr序列图片'
        else:
            return u'L 指定文件夹下没有exr序列'


        ## --------------check r exr
        if r_folder :
            all_files=os.listdir(r_folder)
            self.dialog.r_seqs=pplu.findFiles(r_folder,'.exr')

            r_jpg_dir=os.path.dirname(l_folder)+'/jpg_R'
            if not os.path.isdir(r_jpg_dir):
                return u'找不到对应的jpg R序列帧'
            self.dialog.r_jpg_seqs=pplu.findFiles(r_jpg_dir,'.jpg')

            if len(all_files)!=len(self.dialog.r_seqs):
                for rs in self.dialog.r_seqs:
                    all_files.remove(os.path.basename(rs))
                return u'R下包含非exr序列的文件'+'\n'.join(all_files)

            invalid_exr=[]
            for f in self.dialog.r_seqs:
                if self.dialog.task['name']=='paint_fix':
                    if not re.match(self.dialog.entity['name']+'\.pfx\.paint_fix\.\d{4}\.exr$',\
                       os.path.basename(f)):
                        invalid_exr.append(f)
                elif self.dialog.task['name']=='floating_window':
                    if not re.match(self.dialog.entity['name']+'\.pfx\.floating_window\.\d{4}\.exr$',\
                       os.path.basename(f)):
                        invalid_exr.append(f)

            if invalid_exr:
                if self.dialog.task['name']=='paint_fix':
                    return u'R下的exr序列名称不合格，应该是 '+self.dialog.entity['name']+'.pfx.paint_fix.####.exr '+'\n'.join(invalid_exr)
                elif self.dialog.task['name']=='floating_window':
                    return u'R下的exr序列名称不合格，应该是 '+self.dialog.entity['name']+'.pfx.floating_window.####.exr '+'\n'.join(invalid_exr)

            frame_range=[]
            if self.dialog.r_seqs:
                frame_start=os.path.basename(self.dialog.r_seqs[0]).split('.')[-2]
                frame_end=os.path.basename(self.dialog.r_seqs[-1]).split('.')[-2]
                frame_range=[frame_start,frame_end]
                frame_len=len(self.dialog.r_seqs)
                jpg_len=len(self.dialog.r_jpg_seqs)

                if frame_range_shotgun and frame_range and \
                    (int(frame_range[0])!=int(frame_range_shotgun[0]) or\
                     int(frame_range[1])!=int(frame_range_shotgun[1]) or\
                    frame_len_shotgun != frame_len ):
                    return u'R 下的序列帧起始结束帧不匹配,或者序列帧数量不对,exr: '+str(frame_range)+' shotgun: '+str(frame_range_shotgun)

                if frame_len!=jpg_len:
                    return u'jpg R与exr R长度不匹配, jpg:'+str(jpg_len)+'exr:'+str(frame_len)

                old_tag+=' R'
                # self.dialog.print_log('R exr: '+str(frame_range)+' shotgun: '+str(frame_range_shotgun)+'\n')
            else:
                return u'没有 R 的exr序列图片'

        version_name_check=os.path.basename(os.path.dirname(l_folder))
        r_version_name=os.path.basename(os.path.dirname(r_folder))
        nk_version_name=re.findall('\.(v\d{3})\.nk',os.path.basename(self.dialog.nk_file))
        version_name=str(self.dialog.w_ver.lineEdit_version_name.text())

        if r_folder and version_name_check != r_version_name:
            return u'L R版本号不匹配'
        if version_name_check != nk_version_name[0]:
            return u'nuke文件版本号与左右眼序列版本号不匹配'
        if version_name_check!=version_name[1:]:
            return u'publish版本号与序列版本号不一致'

        self.dialog.version_tag=old_tag

        return ''

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


