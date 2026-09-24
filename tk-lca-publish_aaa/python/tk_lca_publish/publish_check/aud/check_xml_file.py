# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import os
import re
import sys
import ast
import edt.edt_cut_xml.cut_xml_main as cxm;reload(cxm)

#sys.path.insert(0, '/mnt/work/home/zhuzichao/workspace/nza/lcatools/tools/edt/aaf_analyse/')
# import edt_funcs;reload(edt_funcs)
# import aaf_funcs;reload(aaf_funcs)
import edt.aaf_analyse.edt_funcs as edt_funcs;reload(edt_funcs)
import edt.aaf_analyse.aaf_funcs as aaf_funcs;reload(aaf_funcs)
import edt.aaf_analyse.utilities as aaf_util;reload(aaf_util)


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查xml/aaf文件"
        self.description = u"检查是否需要xml/aaf文件及文件中是否缺少镜头信息"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def check_xml_shots(self, xml_file, shot_names):
        """
        lack_of_shots: sg has them, but xml has not;
        efficient_shot_items_dict: both sg and xml have them;
        """
        seq_item = cxm.get_seq(xml_file)
        is_from_stb = self.dialog.w_publish_file.stb_checkbox.isChecked()
        lack_of_shots = []
        efficient_shot_items_dict = {}
        if not is_from_stb:
            self.dialog.video_file_nodes, self.dialog.shot_items_dict = cxm.get_video_files_and_shot_items_dict(seq_item)
            for shot_name in shot_names:
                if shot_name in self.dialog.shot_items_dict:
                    efficient_shot_items_dict[shot_name] = self.dialog.shot_items_dict[shot_name]
                else:
                    lack_of_shots.append(shot_name)
        else:
            self.dialog.shot_ranges, _ = cxm.get_orignal_xml_shot_range(self.dialog.xml_file , step = 'storyboard')
            for shot_name in shot_names:
                if shot_name in self.dialog.shot_ranges:
                    efficient_shot_items_dict[shot_name] = self.dialog.shot_ranges[shot_name]
                else:
                    lack_of_shots.append(shot_name)
                
        return lack_of_shots, efficient_shot_items_dict

    def check_aaf_shots(self, sg_shots):
        """

        :param aaf_file:
        :param shot_names: list, contains all shots of a sequence from shotgun.
        :return:
        """
        lack_of_shots = edt_funcs.get_unused_shots(self.dialog.aaf_no_track_merge_result, sg_shots, sequence = '', task = '')
        return lack_of_shots

    # def get_exclusive_shots(self):
    #     """
    #     return a shot string list, e.g ['m20005', 'm20010']
    #     """
    #     exclusive_shots_str = str(self.dialog.w_publish_file.exclusive_lineEdit.text())
    #     exclusive_shots = [shot for shot in exclusive_shots_str.split(' ') if shot]
    #
    #     return exclusive_shots
    #
    # def get_inclusive_shots(self):
    #     """
    #     获取只需要更新的镜头号列表
    #     return a shot string list, e.g ['m20005', 'm20010']
    #     """
    #     inclusive_shots_str = str(self.dialog.w_publish_file.inclusive_lineEdit.text())
    #     inclusive_shots = [shot for shot in inclusive_shots_str.split(' ') if shot]
    #     return inclusive_shots
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
    def init_vars(self):
        """

        :return:
        """
        self.dialog.xml_file = ''
        self.dialog.aaf_file = ''
        self.dialog.lack_of_shots = ''
        text = str(self.dialog.w_publish_file.xml_lineEdit.text())
        if text.endswith('.xml'):
            self.dialog.xml_file = text
        elif text.endswith('.aaf'):
            self.dialog.aaf_file = text
            self.dialog.aaf_obj = aaf_funcs.AAF_Object(self.dialog.aaf_file)
            if self.dialog.w_publish_file.stb_checkbox.isChecked():                 # if "is from stb" is checked:
                self.dialog.aaf_no_track_merge_result = edt_funcs.stb_prepare_work(self.dialog.aaf_obj)
            else:
                self.dialog.aaf_no_track_merge_result = edt_funcs.prepare_work(self.dialog.aaf_obj)

    def run_check(self):
        try:
            proj_name = self.dialog.project['name']
            seq_name = self.dialog.entity['name']

            self.init_vars()

            if self.dialog.w_publish_file.seq_checkbox.isChecked():  # sequence mode
                if not self.dialog.xml_file and not self.dialog.aaf_file:
                    return u'Sequence模式下必须有该场次的xml/aaf文件'
                else:
                    sg_shots = self.dialog.sg.find('Shot', [['project', 'name_is', proj_name],
                                                            ['code', 'starts_with', seq_name],
                                                            ['sg_status_list', 'is_not', 'omt']], ['code'])
                    # 获取排除和包含的镜头
                    self.dialog.exclusive_shots = self.get_exclusive_shots()
                    self.dialog.inclusive_shots = self.get_inclusive_shots()

                    shot_names = [sg_shot['code'] for sg_shot in sg_shots]

                    # 根据两种模式确定需要处理的镜头
                    if self.dialog.inclusive_shots:
                        # 如果指定了"只更新的镜头号"，则只处理这些镜头
                        shot_names = [shot for shot in self.dialog.inclusive_shots if shot in shot_names]
                    elif self.dialog.exclusive_shots:
                        # 如果指定了"不需更新的镜头号"，则排除这些镜头
                        shot_names = list(set(shot_names) - set(self.dialog.exclusive_shots))

                    if self.dialog.xml_file:
                        self.dialog.lack_of_shots, self.dialog.efficient_shot_items_dict = self.check_xml_shots(
                            self.dialog.xml_file, shot_names)
                    elif self.dialog.aaf_file:
                        self.dialog.lack_of_shots = self.check_aaf_shots(shot_names)

                    if self.dialog.lack_of_shots:
                        return u'xml中缺少以下镜头:\n %s' % str(self.dialog.lack_of_shots)

            else:       # shot mode
                shot_names = [os.path.basename(f)[:6] for f in self.dialog.wav_files]
                if not self.dialog.xml_file and not self.dialog.aaf_file:
                    self.dialog.must_have_xml = False
                    must_have_xml_shots = []
                    for shot_name in shot_names:
                        status = self.dialog.sg.find_one('Task', [['project', 'name_is', proj_name], ['entity', 'name_is', shot_name], ['content', 'is', 'lighting']], 
                                                         ['sg_status_list'])['sg_status_list']
                        self.dialog.print_log(shot_name + ' ' + status)
                        # if status not in ['wtg', 'ip', 'rdy', 'hld', 'omt', 'rtk']:
                        #根据剪辑需求去掉rtk,rtk不在白名单，也必须提供aaf/xml
                        if status not in ['wtg', 'ip', 'rdy', 'hld', 'omt']:
                            self.dialog.must_have_xml = True
                            must_have_xml_shots.append(shot_name)

                    if self.dialog.must_have_xml:
                        return u'必须有该场次的xml/aaf文件: %s\n' % str(must_have_xml_shots)
                else:
                    if self.dialog.xml_file:
                        self.dialog.lack_of_shots, self.dialog.efficient_shot_items_dict = self.check_xml_shots(self.dialog.xml_file , shot_names)
                    elif self.dialog.aaf_file:
                        #lack_of_shots = self.check_aaf_shots(self.dialog.aaf_file, shot_names)
                        self.dialog.lack_of_shots = self.check_aaf_shots(shot_names)

                    if self.dialog.lack_of_shots:
                        return u'xml/aaf中缺少以下镜头:\n %s' % str(self.dialog.lack_of_shots)
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


