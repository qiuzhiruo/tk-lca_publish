#! -*- coding:utf-8 -*-
import traceback

import maya.cmds as cmds
import pymel.core as pm


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查场景中各Chr,Prp,Veh资产Rig的global_ctrl,root_ctrl缩放"
        self.description = u"检查场景中各Chr,Prp,Veh资产Rig的global_ctrl,root_ctrl缩放是否是1,若不为1需要lay和mod沟通改资产大小."
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        self.bad_global_ctrls = []
        self.shot_data = {'scale_assets': [], 'shots': {}}
        return

    def get_shot_data(self):
        from lay.lca_asset_scale_tag.functions import AssetScaleTagCore
        self.shot_data = {'scale_assets': [], 'shots': {}}
        for i in cmds.ls(type='shot'):
            if i.startswith('pasted__'):
                cmds.lockNode(i, lock=False)
                cmds.delete(i)
                continue
            shot = i.split('_')[0]
            self.shot_data['shots'].setdefault(shot, {'start': 0, 'end': 0, 'assets': []})
            shot_info = self.dialog.sg.find_one('Shot', [['project', 'name_is', self.dialog.project['name'].lower()], ['code', 'is', shot]], ['tag_list'])
            cur_assets = []
            if shot_info['tag_list']:
                for tag in shot_info['tag_list']:
                    cur_assets = AssetScaleTagCore.filter_tag_assets(tag)
            self.shot_data['scale_assets'].extend(cur_assets)
            self.shot_data['shots'][shot]['start'] = cmds.getAttr('{}.startFrame'.format(i))
            self.shot_data['shots'][shot]['end'] = cmds.getAttr('{}.endFrame'.format(i))
            self.shot_data['shots'][shot]['assets'].extend(cur_assets)

    def check_global_ctrl_scale(self, ns):
        glo_ctrl_name = 'global_ctrl'
        glo_ctrl = '{}:{}'.format(ns, glo_ctrl_name)
        glo_ctrl_scale = '{}.scale'.format(glo_ctrl)
        # root_ctrl_name = 'root_ctrl'
        # root_ctrl = '{}:{}'.format(ns, root_ctrl_name)
        # root_ctrl_scale = '{}.scale'.format(root_ctrl)
        asset_name = ns.lstrip(':').rstrip('1234567890')
        cur_scale = cmds.getAttr(glo_ctrl_scale)[0]
        # rot_scale = cmds.getAttr(root_ctrl_scale)[0]

        in_cons = set()
        for i in ['scaleX', 'scaleY', 'scaleZ']:
            cur_con = cmds.listConnections('{}.{}'.format(glo_ctrl, i), s=True, d=False)
            if cur_con:
                in_cons.add(cur_con[0])

        if in_cons:
            invalid_shots = set()
            anim_curves = []
            for i in in_cons:
                con_obj_type = cmds.objectType(i)
                if 'animCurve' in con_obj_type:  # is animated
                    anim_curves.append(i)
                elif 'Constraint' in con_obj_type:  # is constraint
                    src_obj = cmds.listConnections('{}.target[0].targetScale'.format(i), s=True, d=True)[0]
                    for attr in ['scaleX', 'scaleY', 'scaleZ']:
                        src_cur_con = cmds.listConnections('{}.{}'.format(src_obj, attr), s=True, d=False)
                        if src_cur_con:
                            src_con_type = cmds.objectType(src_cur_con[0])
                            if 'animCurve' in src_con_type:  # is animated
                                anim_curves.append(src_cur_con[0])
                        elif cmds.getAttr('{}.{}'.format(src_obj, attr)) != 1 and asset_name not in self.shot_data['scale_assets']:
                            self.bad_global_ctrls.append(u'{} 约束它缩放的物体 "{}" 有缩放'.format(glo_ctrl, src_obj))

            for i in anim_curves:
                vals = cmds.keyframe(i, q=True, vc=True)
                sca_val_indexs = [vals.index(x) for x in vals if x != 1]
                if sca_val_indexs:
                    frames = cmds.keyframe(i, q=True, tc=True)
                    for index in sca_val_indexs:
                        cur_frame = frames[index]
                        for k, v in self.shot_data['shots'].iteritems():
                            if int(v['start']) <= cur_frame <= int(v['end']) and asset_name not in v['assets']:
                                invalid_shots.add(k)

            for i in invalid_shots:
                self.bad_global_ctrls.append(u'{} 在镜头 "{}" 帧范围不能有缩放'.format(glo_ctrl, i))
        else:
            # cur_scale = cmds.getAttr(glo_ctrl_scale)[0]
            # rot_scale = cmds.getAttr(root_ctrl_scale)[0]
            if cur_scale != (1.0, 1.0, 1.0) and asset_name not in self.shot_data['scale_assets']:
                self.bad_global_ctrls.append(u'{} 不能缩放,当前缩放为:{}'.format(glo_ctrl, cur_scale))
            # if rot_scale != (1.0, 1.0, 1.0) and asset_name not in self.shot_data['scale_assets']:
            #     self.bad_global_ctrls.append(u'{} 不能缩放，当前缩放为:{}'.format(root_ctrl, rot_scale))

    def run_check(self):
        try:
            self.get_shot_data()
            self.bad_global_ctrls = []
            # check reference asset
            for i in cmds.ls(type='reference'):
                if i in ['sharedReferenceNode']:
                    continue
                ns = cmds.referenceQuery(i, ns=True).lstrip(':').rstrip('1234567890')
                master_node = '{}:master'.format(ns)
                if not cmds.objExists(master_node):
                    continue
                full_path = cmds.ls(master_node, long=True)[0]
                # lic项目道具放开缩放检查
                if self.dialog.project['name'].lower() == 'lic' and (full_path.startswith('|assets|prp') or full_path.startswith('|assets|veh')):
                    continue
                if cmds.objExists(master_node) and not full_path.startswith('|assets|lay|'):
                    if full_path.startswith('|assets|chr') or full_path.startswith('|assets|prp'):
                        print '>>>>>>>>>>>>>>>'
                        print ns
                        self.check_global_ctrl_scale(ns)
                if full_path.startswith('|assets|veh'):
                    glo_ctrl_name = 'global_ctrl'
                    glo_ctrl = '{}:{}'.format(ns, glo_ctrl_name)
                    glo_ctrl_scale = '{}.scale'.format(glo_ctrl)
                    # root_ctrl_name = 'root_ctrl'
                    # root_ctrl = '{}:{}'.format(ns, root_ctrl_name)
                    # root_ctrl_scale = '{}.scale'.format(root_ctrl)
                    asset_name = ns.lstrip(':').rstrip('1234567890')
                    asset_name = ns
                    cur_scale = cmds.getAttr(glo_ctrl_scale)[0]
                    # rot_scale = cmds.getAttr(root_ctrl_scale)[0]
                    if cur_scale != (1.0, 1.0, 1.0) and asset_name not in self.shot_data['scale_assets']:
                        self.bad_global_ctrls.append(u'{} 不能缩放,当前缩放为:{}'.format(glo_ctrl, cur_scale))
                    # if rot_scale != (1.0, 1.0, 1.0) and asset_name not in self.shot_data['scale_assets']:
                    #     self.bad_global_ctrls.append(u'{} 不能缩放，当前缩放为:{}'.format(root_ctrl, rot_scale))

            # check assembly reference # TODO may use in futhure
            # for i in cmds.ls(type='assemblyReference', long=True):
            #     if not i.startswith('|assets|lay|') and not i.endswith('_scn_AR') and not i.endswith('_asb_AR'):
            #         p_ns = i.split('|')[-1].split(':')[:-1]
            #         p_ns.append(cmds.getAttr('{}.repNamespace'.format(i)))
            #         ns = ':'.join(p_ns)
            #         self.check_global_ctrl_scale(ns)
            if self.bad_global_ctrls:
                return u'以下资产的Global Ctrl不为(1, 1, 1):\n{}'.format('\n'.join(self.bad_global_ctrls))
            else:
                return u''
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

