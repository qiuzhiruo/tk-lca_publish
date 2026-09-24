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

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的预览文件的路径和命名。"
        self.description = u"提交的预览文件名由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成，英文字母全小写。\n文件路径所在的各级文件夹命名不能有中文和空格。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            desp =u"提交图片: "
            
            l_preview_files = [self.dialog.w_file.listWidget_preview.item(i).text() for i in xrange(self.dialog.w_file.listWidget_preview.count())]

            if len(l_preview_files) == 0:
                return u"还没有选择文件。"

            basename_list = []
            unique_list = []

            p1 = re.compile("[\w\.-]*$")
            p2 = re.compile("[\w\.]*$")
            for file_path_qtstr in l_preview_files:
                file_path = str(file_path_qtstr)

                if not os.path.isfile(file_path): 
                    return u"找不到这个文件:\n  " + file_path 

                tokens = file_path.replace(":", "\\").replace("/", "\\").split("\\")
                for token in tokens[:-1]:
                    if not p1.match(token):
                        return u"各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"，中划线\"-\"和点\".\"组成:\n  " + "\"" + token + "\" in " + file_path

                if not p2.match(tokens[-1]):
                    return u"文件名需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + tokens[-1]

                if tokens[-1] != tokens[-1].lower():
                    return u"\n文件名必须全小写:" + tokens[-1]

                if not '.' in tokens[-1]:
                    return u"\n文件名必须有扩展名:" + tokens[-1]
                
                if tokens[-1].rsplit('.',1)[0].isdigit() :
                    return u"\n文件名不能是纯数字:" + tokens[-1]

                basename=os.path.basename(file_path)
                if basename in basename_list:
                    unique_list.append(file_path)
                else:
                    basename_list.append(basename)
                    
                if unique_list:
                    return u"\n提交文件名不能重名:" + '\n'.join(unique_list)
                
                
                desp+=tokens[-1]+','

            self.dialog.l_preview_files = l_preview_files

            image_num = self.dialog.image_layout.count()
            del_image_list = []
            for i in range(image_num):
                image_item = self.dialog.image_layout.itemAt(i)
                image_item_wedget = image_item.widget()
                if image_item_wedget.isDel:
                    del_image_list.append(image_item_wedget.image_path)
            
            if len(del_image_list)>0:
                desp += u'\n从综合版本删除图片:'+u',  '.join([os.path.basename(del_img)[:-4] for del_img in del_image_list])
            
            
            self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(desp)

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


