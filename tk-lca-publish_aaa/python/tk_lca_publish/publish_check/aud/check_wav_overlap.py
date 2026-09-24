# -*- coding:utf-8 -*-
__author__ = 'haojia'

import traceback
import os
import sys

import edt.aaf_analyse.aaf_funcs as aaff


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的seq wav文件帧数是否重叠（只有勾选了Sequence wav才会生效）"
        self.description = u"检查AAF文件中所有音频片段的时间轴帧数范围，确保没有重叠区间（只有勾选了Sequence wav才会生效）。"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def extract_intervals(self, data):
        """
        从AAF数据中提取所有时间区间

        Args:
            data: AAF解析后的字典数据

        Returns:
            list: 包含所有区间信息的列表
        """
        all_intervals = []

        for filename, tracks in data.iteritems():
            for track_id, segments in tracks.iteritems():
                for segment in segments:
                    # segment格式: (start, end, offset1, offset2, duration, flag)
                    start = segment[0]
                    end = segment[1]

                    all_intervals.append({
                        'start': start,
                        'end': end,
                        'filename': filename,
                        'track_id': track_id,
                        'segment': segment
                    })

        return all_intervals

    def find_overlaps(self, intervals):
        """
        查找所有重叠的区间对

        Args:
            intervals: 区间列表

        Returns:
            list: 重叠区间对的列表
        """
        overlaps = []
        count = len(intervals)

        for i in range(count):
            for j in range(i + 1, count):
                item1 = intervals[i]
                item2 = intervals[j]

                s1, e1 = item1['start'], item1['end']
                s2, e2 = item2['start'], item2['end']

                # 检查是否重叠: s1 < e2 and s2 < e1
                if s1 < e2 and s2 < e1:
                    overlap_start = max(s1, s2)
                    overlap_end = min(e1, e2)
                    overlap_duration = overlap_end - overlap_start

                    overlaps.append({
                        'item1': item1,
                        'item2': item2,
                        'overlap_range': (overlap_start, overlap_end),
                        'overlap_duration': overlap_duration
                    })

        return overlaps

    def format_overlap_report(self, overlaps):
        """
        格式化重叠报告

        Args:
            overlaps: 重叠区间列表

        Returns:
            str: 格式化的报告文本
        """
        if not overlaps:
            return u"✓ 未发现任何帧数重叠区间"

        report_lines = [
            u"",
            u"=" * 80,
            u"发现 %d 处帧数重叠问题！" % len(overlaps),
            u"=" * 80,
            u""
        ]

        for idx, overlap in enumerate(overlaps, 1):
            item1 = overlap['item1']
            item2 = overlap['item2']
            overlap_range = overlap['overlap_range']
            overlap_duration = overlap['overlap_duration']

            report_lines.extend([
                u"【重叠 %d】" % idx,
                u"  片段A: %s (Track %s)" % (item1['filename'], item1['track_id']),
                u"         帧范围: [%d - %d]" % (item1['start'], item1['end']),
                u"  片段B: %s (Track %s)" % (item2['filename'], item2['track_id']),
                u"         帧范围: [%d - %d]" % (item2['start'], item2['end']),
                u"  重叠区间: [%d - %d]，重叠帧数: %d 帧" % (
                    overlap_range[0], overlap_range[1], overlap_duration
                ),
                u"-" * 80,
                u""
            ])

        report_lines.extend([
            u"",
            u"请修正以上重叠问题后重新提交。",
            u"=" * 80
        ])

        return u"\n".join(report_lines)

    def run_check(self):
        if not self.dialog.w_publish_file.seq_checkbox.isChecked():  # sequence mode
            return ''
        try:
            aaf_file_path = self.dialog.aaf_file
            #     aaf_file_path = "/mnt/work/projects/tst/preproduction/p70/story/aud/task/final_cut/20250825/p70_lay_20250815.aaf"

            if not os.path.exists(aaf_file_path):
                return u"错误：找不到AAF文件: %s" % aaf_file_path


            aaf_obj = aaff.AAF_Object(aaf_file_path)
            composition_data = aaff.get_CompositionMobs_dict(aaf_obj)
            data = composition_data[0]


            all_intervals = self.extract_intervals(data)

            if not all_intervals:
                return u"警告：AAF文件中未找到任何音频片段"


            overlaps = self.find_overlaps(all_intervals)


            report = self.format_overlap_report(overlaps)


            if overlaps:
                return report  # 有重叠，返回错误报告
            else:
                return ''  # 无重叠，检查通过

        except Exception as e:
            return u"检查过程中发生错误:\n%s" % traceback.format_exc()

    def run_fix(self):
        """自动修复（此检查不支持自动修复）"""
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty