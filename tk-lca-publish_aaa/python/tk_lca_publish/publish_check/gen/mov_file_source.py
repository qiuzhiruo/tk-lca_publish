# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description:  http://wiki.zhuiguang.com/x/QhvQ
#
############################################

import traceback
import subprocess

COMMON_PATTERNS = ['Comment', 'Info', 'Movie/Comment']


# All system check classes will use StdCheck as the class name.
class StdCheck():
    """

    http://wiki.zhuiguang.com/x/QhvQ

    """

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"mov文件需要从对应版本的 Maya 文件拍屏而来。"
        self.description = u"剪辑曾经投诉有时候拿到名为 a00000.abc.aabbcc.v007.mov 的文件，" \
                           u"是从 a00000.abc.aabbcc.v005.ma 文件拍屏而来。" \
                           u"\n为了避免这种情况，我们现在的拍屏工具写入了拍屏的文件源，" \
                           u"保证publish v007版所用的预览一定是从 .v007.ma文件而来。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            self.dialog.l_mov_info = []

            # self.dialog.l_preview_files must be a mov file
            if not (len(self.dialog.l_preview_files) and
                    self.dialog.l_preview_files[0].endswith('.mov')):
                return u"预览应该是一个 mov 文件。"

            if self.dialog.step['name'] == 'flo' and \
                    self.dialog.task['name'].lower() == 'final_layout' and \
                    '.stereo' in self.dialog.l_preview_files[0]:
                return u'预览不应为stereo mov文件'

            mov_path = self.dialog.l_preview_files[0]
            cmd_str = '"' + self.dialog.rvls_path + '" -x ' + mov_path
            print 'Cmd:', cmd_str
            p = subprocess.Popen(
                cmd_str,
                shell=self.dialog.process_shell,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            (out, err) = p.communicate()
            print 'out:', out
            print 'err:', err
            if not out or len(out) == 0:
                return u"无法读取 mov 文件信息。请确认RV可以正常运行，并用 LCA Tools 中 Playblaster 工具拍屏。"

            out = out.replace('\r', ' ').replace('\n', ' ')
            tokens = out.split(' ')

            self.dialog.l_mov_info = [t for t in tokens if t]
            cmt_str = None
            for cmt_p in COMMON_PATTERNS:
                if cmt_p in self.dialog.l_mov_info:
                    cmt_str = cmt_p
                    break
            if cmt_str is None:
                return u"无法获得预览内的 Comment 信息。请用 LCA Tools 中 Playblaster 工具拍屏。"

            i = self.dialog.l_mov_info.index(cmt_str)
            if len(self.dialog.l_mov_info) < i + 2:
                return u"无法获得有效的 mov 文件相关信息。请用 LCA Tools 中 Playblaster 工具拍屏。"

            f_name = self.dialog.l_mov_info[i + 2].split('/')[-1]
            if not f_name.endswith(self.dialog.version_name + '.ma') and not f_name.startswith(
                    self.dialog.version_name):
                return u"提交版本预览的 mov 文件是从 " + f_name + u"而来，请使用 " + self.dialog.version_name + u'.ma 拍屏'

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
