# -*- coding:utf-8 -*-

import traceback
import os
import maya.cmds as cmds

import xml.etree.ElementTree as ET
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查缩放'
        self.description = u'检查bbx缩放相校于粗模是否超过10%  skip tag: skip_bbx_check'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def get_xml(self):
        versions = self.dialog.sg.find("Version", [['project', 'is', self.dialog.project],
                                            ['entity','is', self.dialog.entity],
                                            ["sg_task", "name_is", "model"],
                                            ["tags", "name_contains", "粗模"]

                                        ], [
                                            "code",
                                            "sg_task",
                                            "tags",
                                            "sg_version_folder"
                                        ])

        if versions:
            cu_version_path = versions[-1]['sg_version_folder']['local_path']
            xml_path = os.path.join(cu_version_path, 'scene_graph_xml', self.dialog.entity['name'] + '.xml')
            return xml_path
        else:
            return

    @record_time(__file__)
    def run_check(self):

        if self.dialog.version_tag == u'粗模' or self.dialog.project['name'].lower() == 'sgl':
            return ''

        asset_info = self.dialog.sg.find_one("Asset",[['project', 'is', self.dialog.project],
                                                      ['code', 'is', self.dialog.entity['name']]],
                                             ['sg_asset_type', 'tag_list'])

        print(asset_info['tag_list'])

        if not asset_info or asset_info not in ['prp'] or 'skip_bbx_check' in asset_info['tag_list']:
            return ''

        xml_path = self.get_xml()
        # 没有粗模不进行对比
        if not xml_path:
            return ''

        xml_tree = ET.parse(xml_path)
        xml_root = xml_tree.getroot()
        hi_instance = xml_root.find(".//instance[@name='hi']")
        bounds = hi_instance.find("bounds")

        if bounds is None:
            return ''

        # 计算粗模和当前精模的bbx的体积
        try:
            hi_v = (float(bounds.get('maxx')) - float(bounds.get('minx'))) * \
                   (float(bounds.get('maxy')) - float(bounds.get('miny')))  * \
                   (float(bounds.get('maxz'))  - float(bounds.get('minz')))
        except Exception as e:
            return ''

        cur_bbox = [float(format(n, '.6g')) for n in cmds.xform('hi', query=True, boundingBox=True, worldSpace=True)]
        cur_hi_v = (cur_bbox[3] - cur_bbox[0]) * (cur_bbox[4] - cur_bbox[1]) * (cur_bbox[5] - cur_bbox[2])

        if hi_v / cur_hi_v < 0.9:
            return u'当前场景中hi 组的物体整体上相较于粗模的boundingBox增大超过了10%。\n 若确认没问题：跳过tag  "skip_bbx_check"'

        if hi_v / cur_hi_v > 1.1:
            return u'当前场景中hi 组的物体整体上相较于粗模的boundingBox缩小超过了10%。\n 若确认没问题：跳过tag  "skip_bbx_check"'

        return ''


    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
