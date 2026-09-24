# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.05
#
# Description:
#
############################################

import traceback
import subprocess
import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"mov文件需要从对应版本的 Maya 文件拍屏而来。"
        self.description = u"剪辑曾经投诉有时候拿到名为 a00000.abc.aabbcc.v007.mov 的文件，是从 a00000.abc.aabbcc.v005.ma 文件拍屏而来。\n为了避免这种情况，我们现在的拍屏工具写入了拍屏的文件源，保证publish v007版所用的预览一定是从 .v007.ma文件而来。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            for data in self.dialog.shots_preview_data:
                result = u'镜头: ' + data['shot_info']['code'] + u', '
                if not data['preview']:
                    return result+u'未选择预览文件。'

                if not os.path.isfile(data['preview']):
                    return result+u"预览文件不存在：%s"%data['preview']

                cmd_str = '"' + self.dialog.rvls_path + '" -x '+ data['preview']
                p = subprocess.Popen(cmd_str,
                                     shell=self.dialog.process_shell,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                out, err = p.communicate()
                if not out or len(out) == 0:
                    return result+u"无法读取镜头 mov 文件信息。请确认RV可以正常运行，并用 LCA Tools 中 Playblaster 工具拍屏。"

                mov_info = out.split()
                if not 'Comment' in mov_info and not 'Movie/Comment' in mov_info:
                    return result+u"无法获得镜头预览内的 Comment 信息。请用 LCA Tools 中 Playblaster 工具拍屏。"

                i = mov_info.index('Comment') if 'Comment' in mov_info else mov_info.index('Movie/Comment')
                if len(mov_info) < i+2:
                    return result+u"无法获得有效的 镜头mov 文件相关信息。请用 LCA Tools 中 Playblaster 工具拍屏。"

                version = mov_info[i+2].split('.')[-2][1:]
                if version != self.dialog.version_num:
                    return result+u"提交版本预览的 镜头mov 文件是从 " + version + u"而来，请使用 "+self.dialog.version_num + u"拍屏"
                data['preview_info'] = mov_info
                
                # topview check
                if data['topview']:     # Daily mode may do not have top view mov
                    topview_cmd_str = '"' + self.dialog.rvls_path + '" -x '+ data['topview']
                    tp = subprocess.Popen(topview_cmd_str, shell = self.dialog.process_shell, 
                                                             stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    tp_out, tp_err = tp.communicate()
                    if not tp_out or len(tp_out) == 0:
                        return result+u"无法读取 topview mov 文件信息。请确认RV可以正常运行，并用 LCA Tools 中 Playblaster 工具拍屏。"
    
                    mov_info = tp_out.split()
                    if not 'Comment' in mov_info and not 'Movie/Comment' in mov_info:
                        return result+u"无法获得 topview 预览内的 Comment 信息。请用 LCA Tools 中 Playblaster 工具拍屏。"

                    i = mov_info.index('Comment') if 'Comment' in mov_info else mov_info.index('Movie/Comment')
                    if len(mov_info) < i+2:
                        return result+u"无法获得有效的 topview mov 文件相关信息。请用 LCA Tools 中 Playblaster 工具拍屏。"
    
                    version = mov_info[i+2].split('.')[-2][1:]
                    if version != self.dialog.version_num:
                        return result+u"提交版本预览的 topview mov 文件是从 " + version + u"而来，请使用 " + self.dialog.version_num + u"拍屏"
                
            
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

