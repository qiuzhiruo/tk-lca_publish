# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2016.01
#
# Description: See Ticket #2829
#
############################################

import traceback

from sgtk.platform.qt import QtCore, QtGui
if False:
    from PySide import QtCore, QtGui

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"是否需要通知并Retake下游动画任务"
        self.description = (u"提交chr类资产时，要根据修改内容判断：\n"
                            u"已经完成的下游动画任务，是否需要重新提交。\n\n"
                            u"注：一般情况下，绑定功能性的修改，不需要；\n"
                            u"而模型更新、或CFX需求导致的修改，需要。")
        return

    def proceed(self):
        try:
            self.dialog.note_and_retake_animation = False
            if self.dialog.version_tag != u"成品":
                return ""

            asset = self.dialog.sg.find_one(
                'Asset',
                [['id', 'is', self.dialog.entity['id']]],
                ['sg_asset_type'],
            )
            # Only consider characters for now
            if asset['sg_asset_type'] != 'chr':
                return ""

            # Target animation tasks
            animation_tasks = self.dialog.sg.find(
                'Task',
                [['entity.Shot.assets', 'in', self.dialog.entity],
                 ['step', 'name_is', 'ani'],
                 ['content', 'is', 'animation'],
                 {
                     'filter_operator': 'any',
                     'filters': [
                         ['sg_status_list', 'is', 'sc'],
                         ['sg_status_list', 'is', 'da']
                     ],
                 }],
                ['entity'],
            )
            if not animation_tasks:
                self.dialog.print_log('No matching downstream tasks, skipping...')
                return ""

            # Skip if lighting is already finished
            lighting_tasks = self.dialog.sg.find(
                'Task',
                [['entity.Shot.assets', 'in', self.dialog.entity],
                 ['step', 'name_is', 'lgt'],
                 ['content', 'is', 'lighting'],
                 {
                     'filter_operator': 'any',
                     'filters': [
                         ['sg_status_list', 'is', 'da'],
                         ['sg_status_list', 'is', 'fin'],
                         ['sg_status_list', 'is', 'omt']
                     ],
                 }],
                ['entity'],
            )
            skipping_shots = [t['entity'] for t in lighting_tasks]
            tasks = []
            for task in animation_tasks:
                shot = task['entity']
                if shot not in skipping_shots:
                    tasks.append(task)

            # Skip if no matching tasks found
            if not tasks:
                self.dialog.print_log('No matching downstream tasks, skipping...')
                return ""

            # Skip if user decided to
            result = QtGui.QMessageBox.question(
                self.dialog,
                self.process_name,
                self.description,
                buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
            )
            if result == QtGui.QMessageBox.Yes:
                self.dialog.note_and_retake_animation = True
                self.dialog.note_and_retake_animation_tasks = tasks
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
