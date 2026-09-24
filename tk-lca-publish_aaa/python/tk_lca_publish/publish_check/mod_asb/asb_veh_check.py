# -*- coding:utf-8 -*-

__author__ = 'wangxueqiang'

import os
import traceback
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查大环(root_ctrl)对道具组(inside_grp)的约束是否失效。"
        self.description = u"检查大环(root_ctrl)对道具组(inside_grp)的约束是否失效。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @staticmethod
    def test_constraint_is_invalid(global_ctr_node):
        # 3 constraint whether or not invalid
        t_value = 1
        r_value = 10
        inside_node = pm.PyNode('inside_grp')
        global_ctr_node.t.set(t_value, t_value, t_value)
        global_ctr_node.r.set(r_value, r_value, r_value)
        constraint_obj_tr = inside_node.t.get()
        constraint_obj_ro = inside_node.r.get()
        #
        if constraint_obj_tr[0] - t_value < 0.00001 and constraint_obj_ro[0] - r_value < 0.00001:
            return True
        else:
            return False

    @staticmethod
    def reset_global_ctr_zero(global_ctr_node):
        global_ctr_node.t.set(0, 0, 0)
        global_ctr_node.r.set(0, 0, 0)

    @staticmethod
    def get_asset_name():
        file_path = pm.sceneName()
        file_name = os.path.split(file_path)[1]
        asb_file_name = file_name.split('.')[0]
        return asb_file_name

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list', 'sg_remark', 'sg_chinese'])
        return asset_info

    @staticmethod
    def clean_inside_constraint():
        input_nodes = list(set(pm.PyNode('inside_grp').inputs()))
        for in_node in input_nodes:
            if not 'Constraint' in in_node.type():
                continue
            # print in_node
            try:
                pm.lockNode(in_node, lock=False)
                pm.delete(in_node)
            except:
                pass

    def run_check(self):

        try:
            import pymel.core as pm

            # 1.find tag:VEH_ASB
            sg_info = self.get_asset_shotgun_info(asset_name=self.get_asset_name())
            if 'VEH_ASB' not in sg_info['tag_list']:
                print u'shotgun上没有发现该资产的VEH_ASB标签，请联系PC或者TD添加VEH_ASB标签.'
                return ''
            # 2.find global_ctr
            global_ctr_node = pm.ls('*root_ctrl', r=True, long=True, type='transform')
            if not global_ctr_node:
                return u'没有发现root_ctrl控制器，要使用该资产的大环约束inside组，请确认该AR资产是否展开？'
            # 3.查inside上的约束有没有，有的或连接物体存不存在，存在在去判断约束是否失效
            if not pm.objExists('inside_grp'):
                return u'没有发现{}资产的inside组,请检查该资产内道具组的命名'.format(self.get_asset_name)
            # 4.fin global if connect_constraint
            parent_constraint_list = list(set(global_ctr_node[0].outputs(type='parentConstraint')))
            if not parent_constraint_list:
                return u'{}与inside组之间的约束不存在，请检查文件，可以使用自动修复功能'.format(global_ctr_node.name())
            # 5.find constraint target if is inside grp
            constraint_obj = parent_constraint_list[0].constraintTranslateZ.outputs(type='transform')
            if not constraint_obj:
                return u'{}与inside组之间的约束不存在，请检查文件，可以使用自动修复功能'.format(global_ctr_node.name())
            if constraint_obj[0].name() != 'inside_grp':
                return u'{}与inside组之间的约束不存在，请检查文件，可以使用自动修复功能'.format(global_ctr_node.name())
            # 6
            if not self.test_constraint_is_invalid(global_ctr_node=global_ctr_node[0]):
                return u'{}与inside组之间的约束失效，请检查文件，可以使用自动修复功能'.format(global_ctr_node.name())
            #
            self.reset_global_ctr_zero(global_ctr_node=global_ctr_node[0])
            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            # clean inside constraint  if constraint exists
            self.clean_inside_constraint()
            # add constraint
            global_ctr_node = pm.ls('*root_ctrl', r=True, long=True, type='transform')
            pm.parentConstraint(global_ctr_node[0], 'inside_grp', mo=True)

            return u"重新添加约束修复成功！"
        except:
            return u"自动修复失败！"

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
