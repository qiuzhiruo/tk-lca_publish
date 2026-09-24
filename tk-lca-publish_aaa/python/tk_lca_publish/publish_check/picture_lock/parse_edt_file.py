# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.08
#
# Description: 
#
############################################

import traceback
import os
import sgtk
from sgtk.platform.qt import QtCore, QtGui

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"获取 Edt 文件内的素材信息"
        self.description = u"获取 Edt 文件内的素材信息"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            self.dialog.edt_file = self.dialog.w_publish_file.lineEdit_edt.text()
            if not os.path.isfile(self.dialog.edt_file):
                return u"没有找到剪辑信息文件: " + self.dialog.edt_file

            if " " in self.dialog.edt_file:
                return u"剪辑文件路径中有空格: " + self.dialog.edt_file

            f = open(self.dialog.edt_file, 'r')
            l_lines = f.readlines()
            f.close()
            
            seqs = self.get_file_seqs(l_lines)
            l_shots = self.dialog.sg.find('Shot', [['project', 'is', self.dialog.project], ['sg_sequence', 'is', self.dialog.entity ], ['sg_status_list', 'is_not', 'omt']], ['code', 'sg_cut_in', 'sg_cut_out', 'sg_cut_duration'])
            if seqs:
                btn = QtGui.QMessageBox.question(None, 'Question', 'Multi-Sequence, Continue?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if btn == QtGui.QMessageBox.No:
                    return 'Multi-Sequence Error'
                
                for seq in seqs:
                    seq_shots = self.dialog.sg.find('Shot', [['project', 'is', self.dialog.project], ['sg_sequence', 'name_is', seq], ['sg_status_list', 'is_not', 'omt']], ['code', 'sg_cut_in', 'sg_cut_out', 'sg_cut_duration'])
                    l_shots.extend(seq_shots)
            seqs.append(self.dialog.entity['name'])
            
            l_valid_shots = []
            for shot in l_shots:
                if len(shot['code']) == 6:
                    l_valid_shots.append(shot['code'])

            self.dialog.edt_cuts = {}


            shot_name = None
            edt_index = 0
            for i, line in enumerate(l_lines):
                #if line[:6].startswith(self.dialog.entity['name']) and line[1:6].isdigit():
                if line[:3] in seqs and line[1:6].isdigit():
                    shot_name = line[:6]
                    if not shot_name in l_valid_shots:
                        return u"shotgun上没有找到有效的镜头: " + shot_name
                    self.dialog.edt_cuts[edt_index] = {'shot_name':shot_name, 'edt_info':[], 'frames':{}}
                    edt_index += 1
                else:
                    if shot_name is None:
                        continue

                reformed_line = line[:-1].lstrip(' ').rstrip(' ')
                if reformed_line.startswith('(') and reformed_line.endswith(')'):
                    tokens = [ t for t in reformed_line.replace('(', ' ').replace(')', ' ').replace(',', ' ').replace('\'', ' ').split(' ') if t != '']
                    if len(tokens) < 5:
                        return u"剪辑文件: " + self.dialog.edt_file + u" 第 " + str(i+1) + u" 行有问题，不能拆成 [mov, f_start, f_end, cut_in, cut_out] 格式"
                    if not tokens[0].endswith('.mov'):
                        return u"剪辑文件: " + self.dialog.edt_file + u" 第 " + str(i+1) + u" 行有问题，没有找到mov文件"
                    if not (tokens[1].isdigit() and tokens[2].isdigit() and tokens[3].isdigit() and tokens[4].isdigit()):
                        return u"剪辑文件: " + self.dialog.edt_file + u" 第 " + str(i+1) + u" 行有问题，不能获取有效的帧数"

                    self.dialog.edt_cuts[edt_index-1]['edt_info'].append([tokens[0].rstrip('.mov'), int(tokens[1]), int(tokens[2]), int(tokens[3]), int(tokens[4])])
            return ""
        except:
            return traceback.format_exc()
    

    def get_file_seqs(self, l_lines):
        """
        """
        seqs = []
        for line in l_lines:
            if line[0].isalpha() and line[1:6].isdigit():
                seq = line[:3]
                if seq not in seqs and seq != self.dialog.entity['name']:
                    seqs.append(seq)
        return seqs

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

class FakeDialog(object):
    def __init__(self, edt_file):
        self.edt_file = edt_file


if __name__ == '__main__':
    edt_file = '/mnt/work/home/xiangquan/myWork/edt_analyse/output/TPR_c60_old.txt'
    dialog = FakeDialog(edt_file)
    stdCheck = StdCheck(dialog)
    stdCheck.run_check()
    print 'Done'
    

