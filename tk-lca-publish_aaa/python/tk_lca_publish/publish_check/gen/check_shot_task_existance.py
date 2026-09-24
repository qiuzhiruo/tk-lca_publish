# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import os
import re
import sys
import ast

from sgtk.platform.qt import QtCore, QtGui


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Shotgun镜头和任务是否缺失"
        self.description = u"检查Shotgun镜头和任务是否缺失"
        self.auto_fix = False
        self.duty = u"pc"
        return

    def get_exclusive_shots(self):
        """
        获取需要排除的镜头号列表
        支持以下输入格式:
        1. 空格分隔: 'm20005 m20010'
        2. Python列表格式: "['i70005', 'i70010', 'i70015']"
        3. 不完整的列表格式: "'i70005', 'i70010'" 或 "['i70005', 'i70010'"
        4. 混合格式: "['p70010', 'p70020', 'p70030  p70040"

        return a shot string list, e.g ['m20005', 'm20010']
        """
        exclusive_shots_str = str(self.dialog.w_publish_file.exclusive_lineEdit.text()).strip()

        if not exclusive_shots_str:
            return []

        # 尝试识别并修复 Python 列表格式
        if '[' in exclusive_shots_str or ',' in exclusive_shots_str or "'" in exclusive_shots_str:
            try:
                # 清理和标准化字符串
                cleaned = exclusive_shots_str.strip()

                # 确保有完整的方括号
                if not cleaned.startswith('['):
                    cleaned = '[' + cleaned
                if not cleaned.endswith(']'):
                    cleaned = cleaned + ']'

                # 使用 ast.literal_eval 安全解析 Python 列表字符串
                exclusive_shots = ast.literal_eval(cleaned)
                # 确保返回的是字符串列表
                return [str(shot) for shot in exclusive_shots if shot]
            except (ValueError, SyntaxError):
                # 如果解析失败,尝试混合提取方式
                import re
                result = []

                # 先提取所有引号内的内容
                matches = re.findall(r"['\"]([^'\"]+)['\"]", exclusive_shots_str)
                result.extend(matches)

                # 移除已匹配的引号部分,处理剩余的空格分隔内容
                remaining = re.sub(r"['\"][^'\"]*['\"]", '', exclusive_shots_str)
                remaining = re.sub(r'[\[\],]', ' ', remaining)  # 移除括号和逗号

                # 提取剩余的非空单词
                extra_shots = [shot.strip() for shot in remaining.split() if shot.strip()]
                result.extend(extra_shots)

                if result:
                    return result

        # 默认按空格分隔
        exclusive_shots = [shot for shot in exclusive_shots_str.split(' ') if shot]
        return exclusive_shots

    def get_inclusive_shots(self):
        """
        获取只需要更新的镜头号列表
        支持以下输入格式:
        1. 空格分隔: 'm20005 m20010'
        2. Python列表格式: "['i70005', 'i70010', 'i70015']"
        3. 不完整的列表格式: "'i70005', 'i70010'" 或 "['i70005', 'i70010'"
        4. 混合格式: "['p70010', 'p70020', 'p70030  p70040"

        return a shot string list, e.g ['m20005', 'm20010']
        """
        inclusive_shots_str = str(self.dialog.w_publish_file.inclusive_lineEdit.text()).strip()

        if not inclusive_shots_str:
            return []

        # 尝试识别并修复 Python 列表格式
        if '[' in inclusive_shots_str or ',' in inclusive_shots_str or "'" in inclusive_shots_str:
            try:
                # 清理和标准化字符串
                cleaned = inclusive_shots_str.strip()

                # 确保有完整的方括号
                if not cleaned.startswith('['):
                    cleaned = '[' + cleaned
                if not cleaned.endswith(']'):
                    cleaned = cleaned + ']'

                # 使用 ast.literal_eval 安全解析 Python 列表字符串
                inclusive_shots = ast.literal_eval(cleaned)
                # 确保返回的是字符串列表
                return [str(shot) for shot in inclusive_shots if shot]
            except (ValueError, SyntaxError):
                # 如果解析失败,尝试混合提取方式
                import re
                result = []

                # 先提取所有引号内的内容
                matches = re.findall(r"['\"]([^'\"]+)['\"]", inclusive_shots_str)
                result.extend(matches)

                # 移除已匹配的引号部分,处理剩余的空格分隔内容
                remaining = re.sub(r"['\"][^'\"]*['\"]", '', inclusive_shots_str)
                remaining = re.sub(r'[\[\],]', ' ', remaining)  # 移除括号和逗号

                # 提取剩余的非空单词
                extra_shots = [shot.strip() for shot in remaining.split() if shot.strip()]
                result.extend(extra_shots)

                if result:
                    return result

        # 默认按空格分隔
        inclusive_shots = [shot for shot in inclusive_shots_str.split(' ') if shot]
        return inclusive_shots

    # def get_inclusive_shots(self):
    #     """
    #     获取只需要更新的镜头号列表
    #     return a shot string list, e.g ['m20005', 'm20010']
    #     """
    #     inclusive_shots_str = str(self.dialog.w_publish_file.inclusive_lineEdit.text())
    #     inclusive_shots = [shot for shot in inclusive_shots_str.split(' ') if shot]
    #     return inclusive_shots
    #
    # def get_exclusive_shots(self):
    #     """
    #     return a shot string list, e.g ['m20005', 'm20010']
    #     """
    #     exclusive_shots_str = str(self.dialog.w_publish_file.exclusive_lineEdit.text())
    #     exclusive_shots = [shot for shot in exclusive_shots_str.split(' ') if shot]
    #
    #     return exclusive_shots

    def run_check(self):
        try:
            proj_name = self.dialog.project['name']
            seq_name = self.dialog.entity['name']
            sg_shots = self.dialog.sg.find('Shot', [['project', 'name_is', proj_name],
                                                    ['code', 'starts_with', seq_name],
                                                    ['sg_status_list', 'is_not', 'omt']], ['code'])
            sg_shot_names = [sg_shot['code'] for sg_shot in sg_shots]

            if self.dialog.w_publish_file.seq_checkbox.isChecked():  # sequence mode
                # 获取排除和包含的镜头
                self.dialog.exclusive_shots = self.get_exclusive_shots()
                self.dialog.inclusive_shots = self.get_inclusive_shots()

                # 根据两种模式确定需要处理的镜头
                if self.dialog.inclusive_shots:
                    # 如果指定了"只更新的镜头号"，则只处理这些镜头
                    shot_names = [shot for shot in self.dialog.inclusive_shots if shot in sg_shot_names]
                elif self.dialog.exclusive_shots:
                    # 如果指定了"不需更新的镜头号"，则排除这些镜头
                    shot_names = list(set(sg_shot_names) - set(self.dialog.exclusive_shots))
                else:
                    # 如果都没指定，处理所有镜头
                    shot_names = sg_shot_names
            else:  # shot mode
                wav_files = []
                for i in range(self.dialog.w_publish_file.listWidget_wavfiles.count()):
                    wav_files.append(str(self.dialog.w_publish_file.listWidget_wavfiles.item(i).text()))
                shot_names = [os.path.basename(f)[:6] for f in wav_files]

            self.lack_of_shot = []
            self.lack_of_task = []
            for shot_name in shot_names:
                if shot_name not in sg_shot_names:
                    self.lack_of_shot.append(shot_name)
                    continue

                tasks = self.dialog.sg.find('Task', [['project', 'name_is', proj_name],
                                                     ['entity', 'name_is', shot_name]], ['id', 'content', 'step'])
                if not tasks:
                    self.lack_of_task.append(shot_name)

            msg = ''
            if self.lack_of_shot:
                msg += u'以下镜头在shotgun上不存在，请联系pc创建镜头，任务和文件夹：\n'
                msg += '\n'.join(self.lack_of_shot)

            if self.lack_of_task:
                if msg:
                    msg += '\n'
                msg += u'以下镜头在shotgun上缺少任务，请联系pc创建任务和文件夹：\n'
                msg += '\n'.join(self.lack_of_task)

            if msg:
                QtGui.QMessageBox.warning(self.dialog, 'Warning', msg)
                return msg

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


