# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import subprocess
import os
import sys
import shutil


def get_dirs():
    if sys.platform.startswith('win'):
        return 'D:', 'Z:/trash/log/edt_frame_range_control'
    elif sys.platform.startswith('linux'):
        p = subprocess.Popen('ls -d ~', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = p.communicate()
        return out[:-1], '/mnt/proj/trash/log/edt_frame_range_control'
    return None, None

# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"创建html文件"
        self.description = u"以sequence xml/aaf 和shotgun信息为基础，创建html文件，记录镜头时长变化情况"
        return
    
    def proceed(self):
        #if just normal audio task, do not need to convert anything
        try:
            if not self.dialog.xml_file and not self.dialog.aaf_file:
                return ''
            
            if self.dialog.w_publish_file.stb_checkbox.isChecked():         # storyboard mode does not need html
                return ''
            
            seq_name = self.dialog.entity['name']
            proj_name = self.dialog.project['name'].upper()
            log_dir = os.path.join(get_dirs()[1], proj_name).replace('\\', '/')
            if not os.path.exists(log_dir):
                os.mkdir(log_dir)
                os.chmod(log_dir, 0777)

            postfix = self.dialog.version_dir.split('.', 2)[-1]
            title = proj_name + '.' + seq_name + '.' + postfix + '.html'
            html_file = os.path.join(log_dir, title).replace('\\', '/')

            # 不知道为什么要备份, 但现在的问题是剪辑如果连续更新了多个版本, lgt pc没来得及更新就会错过，所以去掉remove备份html
            # self.backup_old_htmls(log_dir, title)           # backup old htmls before creating a new one
            self.write_to_html(self.dialog.edit_status_dict, proj_name, html_file, title)
            return ''
        
        except:
            return traceback.format_exc()
    
    def backup_old_htmls(self, log_dir, title):
        """
        backup old htmls before creating a new one
        """
        copyto = os.path.join(log_dir, 'used').replace('\\', '/')
        if not os.path.exists(copyto):
            os.mkdir(copyto)
            os.chmod(copyto, 0777)

        pattern = title.rsplit('.', 2)[0]
        pattern_htmls = [os.path.join(log_dir, f).replace('\\', '/') for f in os.listdir(log_dir)
                         if f.startswith(pattern) and f.endswith('.html')]
        for p_html in pattern_htmls:
            shutil.move(p_html, copyto)
    
    def write_to_html(self, shot_dict, proj_name, html_file, title):
        """
         镜头号     时长    剪头     剪尾     抽帧     延长
         m20005  0142     0000     0000     False    True
        """
        body_head ='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
        body_head +='<html xmlns="http://www.w3.org/1999/xhtml">\n'
        body_head +='<head>\n'
        body_head +='<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
        body_head +='<title>'+title+'</title>\n'
        body_head +='<style type="text/css">\n'
        body_head +='body,td,th {\n'
        body_head +='	font-family: Calibri;\n'
        body_head +='}\n'
        body_head +='</style>\n'
        body_head +='</head>\n'
        body_head +='<body>\n'
        
        body ='<table width="1600" border="0">\n'
        body += '  <tr bgcolor="#999999">\n'
        body += '    <td>镜头号</td>\n'
        body += '    <td>剪头</td>\n'
        body += '    <td>剪尾</td>\n'
        body += '    <td>抽帧</td>\n'
        body += '    <td>延长(与xml/aaf中用到的版本比较)</td>\n'
        body += '    <td>xml/aaf中用到的版本时长</td>\n'
        #body += '    <td>上次的版本时长</td>\n'
        #body += '    <td>本次的版本时长</td>\n'
        body += '    <td>原始的sg_cut_duration</td>\n'
        body += '    <td>本次的sg_cut_duration</td>\n'
        body += '    <td>制作人</td>\n'
        body += '    <td>灯光任务状态</td>\n'
        body += '  </tr>\n'
        
        #edit_status_dict = {shot_name: (source_start, source_end, length, cut_head, cut_tail, cutoff_frames, extend_frames, version_frame_count)}
        for index, shot_name in enumerate(sorted(shot_dict.keys())):
            if index == index/2*2:
                body += '  <tr bgcolor="#CCCCCC">\n'
            else:
                body += '  <tr bgcolor="#EEEEEE">\n'
            
            # write row content
            old_duration = self.dialog.sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]], 
                                             ['sg_cut_duration'])['sg_cut_duration']
            task_info = self.dialog.sg.find_one('Task', [['project', 'name_is', proj_name], ['entity', 'name_is', shot_name], ['content', 'is', 'lighting']], 
                                                ['sg_status_list', 'task_assignees'])
            
            body += '    <td>' + str(shot_name) +'</td>\n'
            body += '    <td>' + str(shot_dict[shot_name][3]) + '</td>\n'               #cut head
            body += '    <td>' + str(shot_dict[shot_name][4]) + '</td>\n'               #cut tail
            
            #cutoff_frames: True/False
            if shot_dict[shot_name][5] == True:
                body += '    <td><font color="red">' + str(shot_dict[shot_name][5]) + '</font></td>\n'
            else:
                body += '    <td>' + str(shot_dict[shot_name][5]) + '</td>\n'
            
            #extend frames: True/False
            if shot_dict[shot_name][6] == True:
                body += '    <td><font color="red">' + str(shot_dict[shot_name][6]) + '</font></td>\n'
            else:
                body += '    <td>' + str(shot_dict[shot_name][6]) + '</td>\n'
            
            body += '    <td>' + str(shot_dict[shot_name][7]) + '</td>\n'               #version_frame_count
            
            # duration before 'set_sg_duration' operation update it
            if old_duration is None:
                body += '    <td>Empty</td>\n'
            else:
                body += '    <td>' + str(old_duration) + '</td>\n'
            body += '    <td>' + str(shot_dict[shot_name][2]) + '</td>\n'
            
            # ani task assign to
            if not task_info['task_assignees']:
                body += '    <td>Empty</td>\n'
            else:
                assignees = ' '.join([assignee['name'] for assignee in task_info['task_assignees']])
                body += '    <td>' + assignees + '</td>\n'
            
            # ani task status
            if not task_info['sg_status_list']:
                body += '    <td>Empty</td>\n'
            else:
                body += '    <td>' + str(task_info['sg_status_list']) + '</td>\n'
            body += '  </tr>\n'                                                                                     # end of a row
        
        # Assume we got all shots
        body +='</table>\n'
        body +='</body>\n'
        body +='</html>'
        
        content = body_head
        content += '<p><font size=30>剪辑pa声音情况记录<font></p>'
        content += body
    
        f = open(html_file, 'w')
        f.write(content)
        f.close()
        os.chmod(html_file, 0777)

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
    
    
    



