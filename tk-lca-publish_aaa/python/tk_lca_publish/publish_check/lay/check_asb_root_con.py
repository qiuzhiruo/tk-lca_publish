#! -*- coding:utf-8 -*-
import traceback

import maya.cmds as cmds
import pymel.core as pm

from proc import scene_assets

reload(scene_assets)


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查场景中摆位置asb紫环"
        self.description = u"检查场景中切换是ma或mb的asb是否已添加紫环"
        self.auto_fix = True
        self.duty = u'艺术家本人。'
        self.move_asb = []
        self.ani_asb = []
        return

    def check_ref_constrain(self, asset):
        asset_ns = asset.namespace()
        constrained = False
        non_transform_constrained = False
        asset_constrained_anim = False
        start = cmds.playbackOptions(q=True, minTime=True)
        end = cmds.playbackOptions(q=True, maxTime=True)
        for constrain in pm.listRelatives(asset, ad=True, type='constraint'):
            # exclude referenced constrain:
            if constrain.isReferenced():
                continue
            if asset.nodeType() == 'assemblyReference' and constrain.name().startswith(asset_ns):
                continue
            ctrl_name = constrain.getParent().nodeName().split(':')[-1]
            for c in pm.listConnections(constrain, c=True, d=True, s=False, p=True):
                constrained = True
                attr = c[0].name().split('.')[-1]
                if not ((attr.startswith('constraintTranslate') or attr.startswith(
                        'constraintRotate')) and ctrl_name in ['global_ctrl' or 'root_ctrl']):
                    non_transform_constrained = True

            # 判断约束后, 控制器有没有数值的变化
            for trans in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                value_list = []
                if asset_constrained_anim:
                    break
                for i in range(int(start), int(end) + 1):
                    if asset_constrained_anim:
                        break
                    value = cmds.getAttr(constrain.getParent().nodeName() + '.' + trans, time=i)
                    if not value_list:
                        value_list.append(value)
                    if value_list and value not in value_list:
                        asset_constrained_anim = True

        if constrained:
            if non_transform_constrained:
                return 'constrained', asset_constrained_anim
            else:
                return 'constrained_trans', asset_constrained_anim
        else:
            return '', asset_constrained_anim

    # ma或mb，使用以下函数判断是静止不动，摆位置，动画提示或修复
    def find_static_obj(self, objs, assembly=True):
        obj_data = {}
        start = cmds.playbackOptions(q=True, minTime=True)
        end = cmds.playbackOptions(q=True, maxTime=True)
        for frame in [start, int((end - start) / 4 + start), int((end - start) / 2 + start),
                      int(end - (end - start) / 4), end]:
            cmds.currentTime(frame)
            for o in objs:
                name = o.name()
                if assembly:
                    mesh_grp = '{}{}:mesh_grp'.format(o.namespace(), cmds.assembly(name, q=True, rns=True))
                else:
                    mesh_grp = '{}mesh_grp'.format(o.namespace())
                obj_data.setdefault(name, {})
                if cmds.objExists(mesh_grp):
                    # check all mesh children whether moved
                    child_mesh = cmds.listRelatives(mesh_grp, ad=True, type='mesh')
                    children = [mesh_grp] + [cmds.listRelatives(i, parent=True)[0] for i in
                                             child_mesh] if child_mesh else [mesh_grp]
                    for child in children:
                        obj_data[name].setdefault(child, set())
                        obj_data[name][child].add(str(cmds.xform(child, q=True, bb=True, ws=True)))
                else:
                    # unexpand AR, check the AR node whether moved
                    obj_data[name].setdefault(name, set())
                    obj_data[name][name].add(str(cmds.xform(name, q=True, bb=True, ws=True)))

        static_objs = set()
        for k, v in obj_data.iteritems():
            is_static = True
            for i in v:
                if len(v[i]) > 1:
                    is_static = False
                    break
            if is_static:
                static_objs.add(k)

        return static_objs

    def run_check(self):
        try:
            topNode = ['|assets|scn', '|assets|asb']
            self.move_asb = []
            self.ani_asb = []
            all_asset_ar = []
            for topN in topNode:
                if cmds.objExists(topN):
                    l_asset_ar, l_unload_ar, l_asb_ar = scene_assets.getAssemblyReferenceAssets(topN)
                    all_asset_ar = all_asset_ar + l_asset_ar
            static_assembly_objs = self.find_static_obj(all_asset_ar)
            ma_mb_lish = []
            if all_asset_ar:
                for x in all_asset_ar:
                    if cmds.assembly(x.name(), q=True, al=True).endswith('.ma') or cmds.assembly(x.name(), q=True, al=True).endswith(
                            '.mb'):
                        ma_mb_lish.append(x)
                        if x.name() in static_assembly_objs:
                            if cmds.getAttr('%s.t' % x.name()) != [(0.0, 0.0, 0.0)] or cmds.getAttr('%s.r' % x.name()) != [
                                (0.0, 0.0, 0.0)] or cmds.getAttr('%s.s' % x.name()) != [(1.0, 1.0, 1.0)]:
                                root_con_name = '%s:global_ctrl' % x.name()[:-3]
                                con_name = '_'.join(root_con_name.rsplit(':', 2)[-2:] + ['asb', 'con'])
                                if not cmds.objExists('|assets|lay|ctrl'):
                                    self.move_asb.append(x.name())
                                else:
                                    if con_name not in cmds.listRelatives('|assets|lay|ctrl'):
                                        self.move_asb.append(x.name())
                        else:
                            self.ani_asb.append(x.name())
            if self.move_asb or self.ani_asb:
                return u'以下asb有位移没有创建紫环:\n{}\n以下asb有动画需转reference（请使用工具处理）:\n{}'.format('\n'.join(self.move_asb), '\n'.join(self.ani_asb))
            else:
                return u''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        # change asb ma.hi
        for obj in self.move_asb:
            root_con_name = '%s:global_ctrl' % obj[:-3]
            if cmds.objExists(root_con_name):
                # update con name
                con_name = '_'.join(root_con_name.rsplit(':', 2)[-2:] + ['asb', 'con'])
                cmds.select(root_con_name, r=1)
                bb_list = cmds.xform(q=1, bb=1)
                h = bb_list[1] - bb_list[4]
                w = bb_list[3] - bb_list[0]
                d = bb_list[5] - bb_list[2]
                buf = [h, w, d]
                buf.sort()
                maxDem = buf[-1]
                con_r = maxDem / 2 * 1.2
                if cmds.objExists(con_name):
                    cmds.delete(con_name)
                cmds.circle(ch=1, o=1, nr=(0, 1, 0), n=con_name, r=con_r)
                cmds.delete(cmds.pointConstraint(root_con_name, con_name))
                cmds.delete(cmds.orientConstraint(root_con_name, con_name))
                cmds.parentConstraint(con_name, root_con_name, mo=1, w=1)
                con_shape = cmds.listRelatives(con_name, s=1)[0]
                cmds.setAttr('%s.overrideEnabled' % con_shape, 1)
                cmds.setAttr('%s.overrideColor' % con_shape, 30)
                cmds.addAttr(con_name, ln='asbname', nn='Asbname', dt='string')
                cmds.setAttr('%s.asbname' % con_name, root_con_name, type='string')
                cmds.delete(con_shape, ch=True)
                if cmds.objExists('|assets|lay|ctrl'):
                    cmds.parent(con_name, '|assets|lay|ctrl')
                else:
                    cmds.group(em=True, name='ctrl', parent='|assets|lay')
                    cmds.parent(con_name, '|assets|lay|ctrl')
        # if self.ani_asb:
        #     return u'以下asb有动画需转reference:\n{}'.format('\n'.join(self.ani_asb))
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

