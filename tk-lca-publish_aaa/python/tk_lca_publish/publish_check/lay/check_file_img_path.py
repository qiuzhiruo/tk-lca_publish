# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import sys
import shutil
import traceback

import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查文件中file节点的图片路径及是否有中文'
        self.description = u'非work盘和proj盘的图片路径，在farm预渲染时有可能读不出来，需要避免。'
        self.auto_fix = True
        self.duty = u'艺术家本人'
        return

    def run_check(self):
        try:
            file_nodes = pm.ls(type = 'file')
            # legal_paths = ['/mnt/work/projects', '/mnt/proj/projects'] if sys.platform.startswith('linux') else ['W:/projects', 'Z:/projects']
            legal_paths = ['/mnt/work/projects', '/mnt/proj/projects', '/mnt/work/layProjects', 'W:/projects', 'Z:/projects', 'W:/layProjects']

            self.illegal_images = {}
            self.contain_bad_char_images = {}
            for file_node in file_nodes:
                if self.dialog.step['name'] == 'ani' and pm.referenceQuery(file_node, inr=True):  # for referenced node, ani skip
                    continue
                image_path = file_node.attr('fileTextureName').get().replace('\\', '/')
                is_sequence = file_node.attr('useFrameExtension').get()
                print image_path, is_sequence
                illegal = True
                for legal_path in legal_paths:
                    if legal_path in image_path:
                        illegal = False
                        break
                for i in image_path:
                    if u'\u4e00' <= i <= u'\u9fff':
                        self.contain_bad_char_images[file_node] = (image_path, is_sequence)
                        break

                if illegal:
                    self.illegal_images[file_node] = (image_path, is_sequence)
            
            if self.illegal_images:
                msg = u'以下file节点中图片路径不在work盘或proj盘下，艺术家可以点自动修复或自己手动修改：\n'
                for file_node in self.illegal_images:
                    file_path, is_sequence = self.illegal_images[file_node]
                    msg += str(file_node) + ': ' + file_path
                    if is_sequence:
                        msg += u'（图片序列）\n'
                    else:
                        msg += u'（单帧）\n'
                return msg

            if self.contain_bad_char_images:
                msg = u'以下file节点中图片路径包含"中文"字符, 请改为"拼音"或"英文":\n'
                for i in self.contain_bad_char_images:
                    file_path, is_sequence = self.contain_bad_char_images[i]
                    msg += u'{}: {}'.format(str(i), file_path)
                    msg += u'(图片序列)\n' if is_sequence else u'(图片)\n'
                return msg

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            root_dir = os.path.dirname(pm.sceneName()).replace('\\', '/') + '/textures'
            if not os.path.exists(root_dir):
                os.mkdir(root_dir)

            cannot_be_fix = {}
            for file_node in self.illegal_images:
                file_path, is_sequence = self.illegal_images[file_node]
                if not os.path.exists(file_path):
                    cannot_be_fix[str(file_node)] = str(file_node) + ': ' + file_path
                    continue

                if is_sequence:
                    copy_dir = os.path.dirname(file_path).replace('\\', '/')
                    crnt_img_name = os.path.basename(file_path)
                    paste_dir = os.path.join(root_dir, str(file_node).split(':')[0]).replace('\\', '/')

                    index = 0
                    tmp = paste_dir
                    while os.path.exists(tmp):
                        index += 1
                        tmp = paste_dir+str(index)
                    paste_dir = tmp
                    shutil.copytree(copy_dir, paste_dir)
                    
                    new_file = os.path.join(paste_dir, crnt_img_name).replace('\\', '/')
                    file_node.attr('fileTextureName').set(new_file)
                    file_node.attr('useFrameExtension').set(True)
                else:
                    copy_file = file_path.replace('\\', '/')
                    crnt_img_name = os.path.basename(file_path)
                    shutil.copy2(copy_file, root_dir)
                    
                    new_file = os.path.join(root_dir, crnt_img_name).replace('\\', '/')
                    file_node.attr('fileTextureName').set(new_file)
                    file_node.attr('useFrameExtension').set(False)

            if cannot_be_fix:
                if self.dialog.step['name'] == 'ani':
                    # if the file path is not exists, delete
                    for i in cannot_be_fix:
                        pm.delete(i)
                        print u'删除了图片不存在的file节点： {}'.format(i)
                else:
                    msg = u'以下节点里的图片路径不存在，请手动修改file节点里的图片路径，然后再次 检查->自动修复：\n'
                    msg += ' \n'.join(cannot_be_fix.values())
                    msg += '\n'
                    return msg

            return ''
        except:
            return traceback.format_exc()

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

