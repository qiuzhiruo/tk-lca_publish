# coding:utf-8
# @Author: xiangquan
# @Date:
# @Last Modified by:   tanghaojia
# @Last Modified time:  2022-06-20
# @Last Commit:fix:1.大场景预警从20000000改成50000000;2.修正统计面数bug;
# @Function:flo publish 检查项面数统计
import traceback
import os
import sys
import pymel.core as pm
import maya.cmds as cmds
from sgtk.platform.qt import QtCore, QtGui
from collections import Counter
import json

# if os.name == "posix":
#     sys.path.append('/mnt/utility/toolset/tools/lay/lca_sel_cam_outside_ass')
# else:
#     sys.path.append('U:/toolset/tools/lay/lca_sel_cam_outside_ass')

toolset = os.getenv('LC_TOOLSET')
sys.path.append(os.path.join(toolset, 'tools/lay/lca_sel_cam_outside_ass'))

import select_cam_outside_assets as scoa

reload(scoa)

# import publish_process.gen.sg_asset_links as sal; reload(sal)

LIMITED_POLY_COUNT = 50000000


# All system check classes will use StdCheck as the class name.
class StdCheck():
    """
    """

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"场景面数不能超过5000万"
        self.description = u"场景面数不能超过5000万，否则lgt可能无法渲染。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            self.dialog.send_note = False
            self.dialog.note_content = ''

            assembly_name = pm.ls(type='assemblyReference')

            asb_exist = cmds.objExists('|assets|asb')
            scn_exist = cmds.objExists('|assets|scn')

            if asb_exist and scn_exist:
                scn_asb_node = pm.listRelatives('|assets|scn', '|assets|asb', c=True)
            elif scn_exist:
                scn_asb_node = pm.listRelatives('|assets|scn', c=True)
            elif asb_exist:
                scn_asb_node = pm.listRelatives('|assets|asb', c=True)
            else:
                scn_asb_node = []

            all_ass_name = list(set(assembly_name) ^ set(scn_asb_node))

            all_ass_count_list = []
            ass_count_list = []
            ass_count_dict = {}
            hi_face_json_dict = {}

            if os.name == 'posix':
                json_path = '/mnt/proj/projects/{proj}/asset/{type}/{ass}/mod/publish/{ass}.mod.model/faces_count.json'
            else:
                json_path = 'Z:/projects/{proj}/asset/{type}/{ass}/mod/publish/{ass}.mod.model/faces_count.json'

            # 获取资产个数，json文件路径
            for ass in all_ass_name:
                ass_path = ass.getAttr('definition')
                ass_type = ass_path.split('/asset/')[-1].split('/')[0]
                ass_name = os.path.basename(cmds.getAttr(ass + '.definition'))[:-3]
                current = ass.getActiveLabel()

                if ass_type != 'flg':
                    all_ass_count_list.append(ass)
                    if current == '' or current.endswith('.locator'):
                        hi_face_json_path = json_path.format(proj='can', type=ass_type, ass=ass_name)
                        hi_face_json_dict[ass_name] = hi_face_json_path
                        ass_count_list.append(ass_name)

            # 有json读取json，没有就读取shotgun上的高模面数，这样速度应该会快点
            ass_count_dict = Counter(ass_count_list)
            none_loc_count = 0
            for k, v in ass_count_dict.items():
                if v > 1:
                    poly_hiface_json_path = hi_face_json_dict[k]
                    if os.path.exists(poly_hiface_json_path):
                        with open(poly_hiface_json_path, 'r') as load_re:
                            hi_face = json.load(load_re)
                            none_loc_count += v * hi_face['face']
                    else:
                        try:
                            none_loc_count += v * self.get_poly_count_hi(k)
                        except:
                            print u'shotgun上没有高模面数资产:{}'.format(k)
                            pass
                else:
                    poly_hiface_json_path = hi_face_json_dict[k]
                    if os.path.exists(poly_hiface_json_path):
                        with open(poly_hiface_json_path, 'r') as load_re:
                            hi_face = json.load(load_re)
                            none_loc_count += hi_face['face']
                    else:
                        try:
                            none_loc_count += self.get_poly_count_hi(k)
                        except:
                            print u'shotgun上没有高模面数资产:{}'.format(k)
                            pass

            self.all_ass_sum = self.get_scn_asb_count(scn_asb_node)  # 总面数
            self.none_loc_sum = none_loc_count  # 隐藏面数
            total_mesh_count = self.all_ass_sum - self.none_loc_sum  # 优化后面数
            self.hide_count = len(ass_count_list)  # 隐藏个数
            self.all_ass = len(all_ass_count_list)  # 总个数

            if total_mesh_count > LIMITED_POLY_COUNT:
                try:
                    scoa.sel_out_ass()
                except:
                    pass
                result = self.fill_in_reson(total_mesh_count)
                return result
            return ''
        except:
            return traceback.format_exc()

    def get_poly_count_hi(self, assets):
        file_name = cmds.file(q=True, location=True)
        proj = file_name.split('/projects/')[1].split('/')[0]
        ass_info = self.dialog.sg.find('Asset', [('project', 'is', self.dialog.project), ('code', 'is', assets)],
                                       ['sg_poly_count_hi'])

        return ass_info[0]['sg_poly_count_hi']

    def get_scn_asb_count(self, scn_asb_name=None):
        if scn_asb_name is None:
            scn_asb_name = []
        ass_count_sum = 0
        for ass in scn_asb_name:
            ass_name = os.path.basename(cmds.getAttr(ass + '.definition'))[:-3]
            ass_count_sum += self.get_poly_count_hi(ass_name)

        return ass_count_sum

    def get_unit(self, int):
        # 个 十 百 千 万 十万 百万 千万 亿 十亿 百亿
        unit_dict = {1: u'个', 2: u'十', 3: u'百', 4: u'千', 5: u'万', 6: u'十万', 7: u'百万', 8: u'千万', 9: u'亿', 10: u'十亿',
                     11: u'百亿'}
        unit = unit_dict[len(str(int))]
        return unit

    def fill_in_reson(self, total_mesh_count):
        """
        """
        msg = u'场景面数过多，需要优化。\n优化前总面数:{:,}({})\n优化后总面数:{:,}({})\n总共优化减少面数:{:,}({})\n隐藏资产数(不包括flg类型):{}(个)\n没隐藏资产数(不包括flg类型):{}(个)\n\nFLO艺术家描述（必须填写）:\n'.format(
            self.all_ass_sum, self.get_unit(self.all_ass_sum),
            total_mesh_count, self.get_unit(total_mesh_count),
            self.none_loc_sum, self.get_unit(self.none_loc_sum),
            self.hide_count, self.all_ass - self.hide_count)
        self.dialog.note_content, option = QtGui.QInputDialog.getText(self.dialog, "Warning", msg,
                                                                      QtGui.QLineEdit.Normal, u'已优化')
        # print 'result', self.dialog.note_content , option
        if not option:  # if cancel, cannot pass the check
            self.dialog.print_log(msg)
            return msg
        else:
            if not self.dialog.note_content:
                QtGui.QMessageBox.warning(self.dialog, 'Warning', u'必须填入场景过大的原因')
                result = self.fill_in_reson(total_mesh_count)
                return result
            else:
                self.dialog.send_note = True
                self.dialog.note_content = msg + self.dialog.note_content
                return ''

    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
