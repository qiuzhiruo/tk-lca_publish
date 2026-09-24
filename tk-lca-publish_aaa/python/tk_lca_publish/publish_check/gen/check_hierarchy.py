# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm
import maya.cmds as cmds

import lay.utilities.read_config_funcs as rcf; reload(rcf)

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否存在assets和cameras组，并且assets组下的chr, prp, asb等组是否存在位移"
        self.description = u"assets组下chr, asb, prp, crd, veh, env, scn不可以有位移信息"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            if not pm.objExists("|cameras"):
                return u"没有找到最高层级的 |cameras 组。"

            if not pm.objExists("|assets"):
                return u"没有找到最高层的 |assets 组。"

            if self.dialog.entity['type'] == 'Shot':
                shot_name = self.dialog.entity['name']
                sg_pivot = self.dialog.sg.find_one('Shot', [['project',  'is', self.dialog.project], ['code', 'is', shot_name]], ['sg_stage_pivot'])['sg_stage_pivot']
                self.dialog.print_log('%s sg_pivot: %s' % (shot_name, str(sg_pivot)))

                if sg_pivot is None:
                    self.pivot_trans = (0.0, 0.0, 0.0)
                    if self.dialog.project['name'].upper() == 'CAT':
                        self.special_shot_info = rcf.read_cat_shift_shot_config()
                        if self.special_shot_info.has_key(shot_name):
                            self.pivot_trans = self.special_shot_info[shot_name]
                else:
                    self.pivot_trans = [-float(t) for t in sg_pivot['name'].split(' ')]

                pivot_trans_v = pm.dt.Vector(self.pivot_trans)
                if not pm.PyNode('|assets').getTranslation().isEquivalent(pivot_trans_v):
                    return u'%s 的 |assets 组位移应该为%s' % (shot_name, str(self.pivot_trans))

            root = '|assets|'
            illegal_group = []
            for g in ['chr', 'asb', 'prp', 'crd', 'veh', 'env', 'scn']:
                if not pm.objExists(root+g):
                    continue
                try:
                    if not pm.PyNode(root+g).getTransformation().isEquivalent( pm.dt.TransformationMatrix.identity ):
                        illegal_group.append(root+g)
                except:
                    print traceback.format_exc()

            if illegal_group:
                return u"以下组存在位移信息: " + '\n'.join(illegal_group)

            return ""

        except:
            return traceback.format_exc()


    def rest_grp_trans(self, grp, trans_value):

        return


    def run_fix(self):
        '''Auto Fix'''
        self.dialog.print_log(u'注意！自动修复只修改assets位置不对的情况，其他错误请艺术家自行修复')
        grp = pm.PyNode('|assets')
        # z1* 场次，会将 assets 组位移值同步给下面资产的大环，包括相机大环
        if self.dialog.step['name'] == 'ani' and self.dialog.entity['name'].startswith('z1'):
            # 获取其实结束帧，用于bake约束
            start_frame = cmds.playbackOptions(q=True, min=True)-51 # 18
            end_frame = cmds.playbackOptions(q=True, max=True) # 117
            # 所有大环
            all_global_ctrls = cmds.ls('*:global_ctrl',long=1)
            # all_global_ctrls = cmds.ls('pCube1',long=1)
            need_move_attrs = ['tx','ty','tz']
            if all_global_ctrls!=[]:
                for global_ctrl_full_path in all_global_ctrls:
                    # 只处理 assets 组下面的
                    if '|assets|' in global_ctrl_full_path:
                        global_ctrl = cmds.ls(global_ctrl_full_path)[0]
                        print global_ctrl
                        # 获取大环是否有约束
                        global_ctrl_parents = cmds.listConnections(global_ctrl,s=1,d=0)
                        if global_ctrl_parents:
                            for i in global_ctrl_parents:
                                if 'Constraint' in pm.PyNode(i).type():
                                    print i,pm.PyNode(i).type()
                            cons_parents = list(set([i for i in global_ctrl_parents if 'Constraint' in pm.PyNode(i).type()]))
                            print '   Constraint >',cons_parents
                            # 有，bake 大环
                            if cons_parents!=[]:
                                cmds.bakeResults(global_ctrl,simulation=True,t=(start_frame,end_frame),sampleBy=1,oversamplingRate=1,disableImplicitControl=True,preserveOutsideKeys=True,sparseAnimCurveBake=False,removeBakedAttributeFromLayer=False,removeBakedAnimFromLayer=False,bakeOnOverrideLayer=False,minimizeRotation=True,controlPoints=False,shape=True)
                        # 将大环偏移
                        # 有 key 帧
                        # 无 key 帧
                        for need_move_attr in need_move_attrs:
                            global_ctrl_need_move_attr = global_ctrl+'.'+need_move_attr
                            # print '   ',global_ctrl_need_move_attr
                            assets_grp_attr_value = grp.getAttr(need_move_attr)
                            # print '   ',global_ctrl_need_move_attr,assets_grp_attr_value
                            global_ctrl_need_move_attr_parent = cmds.listConnections(global_ctrl_need_move_attr,s=1,d=0)
                            if global_ctrl_need_move_attr_parent:
                                print '   ',global_ctrl_need_move_attr,assets_grp_attr_value,global_ctrl_need_move_attr_parent
                                cmds.keyframe(global_ctrl_need_move_attr_parent[0],e=1,iub=True,r=1,o='over',vc=assets_grp_attr_value)
                            else:
                                global_ctrl_need_move_attr_value = cmds.getAttr(global_ctrl_need_move_attr)
                                cmds.setAttr(global_ctrl_need_move_attr,(global_ctrl_need_move_attr_value+assets_grp_attr_value))
        pm.lockNode(grp, lock = False)
        grp.setAttr('visibility', 0)
        grp.setAttr('translateX', lock = False)
        grp.setAttr('translateY', lock = False)
        grp.setAttr('translateZ', lock = False)
        grp.setAttr('translateX', self.pivot_trans[0])
        grp.setAttr('translateY', self.pivot_trans[1])
        grp.setAttr('translateZ', self.pivot_trans[2])
        grp.setAttr('translateX', lock = True)
        grp.setAttr('translateY', lock = True)
        grp.setAttr('translateZ', lock = True)
        grp.setAttr('visibility', 1)
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

