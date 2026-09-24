# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset model group hierarchy
#
############################################

import traceback
import os
import re
import maya.mel as mel
import pymel.core as pm
import maya.cmds as mc

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产模型层级命名,mesh数量。"
        self.description = u"模型最上层组为master,其次为poly,再次为hi, md, lo 等表示精细度的组。\n如果是USD标准项目，在hi,md,lo下需要一个mesh组\nhi组必须有且不能是空的。lo/md 组现在不是必须的，但如果有了这样的组，组内不能为空。\n如果有多个组(hi,md,lo),需要按照 hi, md, lo 这样的次序上下排列。\nUSD标准项目中 hi/md/lo 之下必须先有一个 mesh_grp 组。(tag:'skip_skin_grp' 'skip_eyeball')"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def set_flg_lod(self,assets_info):
        from production.shotgun_connection import Connection
        sg = Connection('get_project_info').get_sg()
        asset_id=assets_info['asset']['id']
        sg.update('Asset', asset_id, {'sg_manual_lod':True})
    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    def check_all_skin_group(self,grp_skin):

        skin_get_children = grp_skin.getChildren()

        for grp in skin_get_children:
            if grp.getShapes():
                self.all_mesh.append(grp)
                self.all_mesh.append(str(grp.nodeName()))

            else:
                self.check_all_skin_group(grp)

    def run_check(self):
        self.auto = True
        try:
            asset_type_list=[self.dialog.d_assets_info[key]['type'] for key in self.dialog.d_assets_info.keys()]
            for asset_name in self.dialog.d_assets_info.keys():

                root = self.dialog.d_assets_info[asset_name]['node']
                root_name = root.fullPath()
                asset_type = self.dialog.d_assets_info[asset_name]['type']
                lod = self.dialog.d_assets_info[asset_name]['lod']

                mesh_grp_l = []
                hi_l = []
                poly_l = []
                for hier in pm.listRelatives(root, type='transform', ad=True):
                    hier = hier.name().split('|')[-1]
                    if 'mesh_grp' in hier:
                        mesh_grp_l.append(hier)
                    if 'hi' == hier.replace(hier.replace('hi', ''), '') and hier.replace('hi', '').isdigit() or 'hi' == hier:
                        hi_l.append(hier)
                    if 'poly' == hier.replace(hier.replace('poly', ''), '') and hier.replace('poly', '').isdigit() or 'poly' == hier:
                        poly_l.append(hier)

                if len(mesh_grp_l) < 1:
                    return u'{}下面缺少{}组'.format(asset_name, 'mesh_grp')
                if len(mesh_grp_l) > 1:
                    mesh_grp_l.remove('mesh_grp')
                    return u'这些组名字内包含"mesh_grp", 需要改掉:\n{}'.format('\n'.join(mesh_grp_l))

                if len(hi_l) < 1:
                    return u'{}下面缺少{}组'.format(asset_name, 'hi')
                if len(hi_l) > 1:
                    return u'{}下面存在多个 hi 组'.format(asset_name)

                if len(poly_l) < 1:
                    return u'{}下面缺少{}组'.format(asset_name, 'poly')
                if len(poly_l) > 1:
                    return u'{}下面存在多个 poly 组'.format(asset_name)

                if not pm.objExists(root):
                    return u"资产" + asset_name + u"没有找到最高层的 " + root_name + u" 组。"

                if not pm.objExists(root_name + "|poly"):
                    return u"资产" + asset_name + u"没有找到次高层的 " + root_name + u"|poly 组。"

                for grp in pm.listRelatives(root_name, c=True):
                    if not grp.nodeName() in ['poly', 'shape', 'misc']:
                        return u"资产" + asset_name + u"的第二层只能有 poly shape 和 misc 组。现在发现了" + grp.nodeName()

                l_res = pm.listRelatives(root_name + '|poly', c=True)
                if not 'hi' in [res.nodeName() for res in l_res]:
                    return u"资产" + asset_name + u"没有找到高模存放的 " + root_name + u"|poly|hi 组"

                if asset_type in ['chr'] and 'asm' not in asset_type_list:
                    if not pm.objExists('body_geo') and not pm.objExists('head_geo'):
                        return u'chr资产找不到名为： body_geo 的模型  或者  head_geo 的模型【2者必存其1】'

                if asset_type in ['crd']:
                    if not pm.objExists('body_geo'):
                        return u'crd资产找不到名为： body_geo 的模型 '

                if asset_type in ['asm']:
                    mod_asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                                ['sg_asset_type', 'assets','parents'])

                    if len(mod_asset['parents'])==0 and not pm.objExists('body_geo') and not pm.objExists('head_geo'):
                        return u'asm 母体资产找不到名为： body_geo 的模型  或者  head_geo 的模型【2者必存其1】'

                group_mesh_l=[n.name() for n in pm.ls('*group*',type='mesh')]
                if len(group_mesh_l)>0:
                    pm.select(group_mesh_l)
                    return u'模型名字不能有group: '+u''.join(group_mesh_l)
                error_name_meshes=[]
                for res in l_res:

                    if not res.nodeName() in ['hi', 'md', 'lo', 'proxy']:
                        return u"资产" + asset_name + u"下的精度组，只能有 hi, md, lo, proxy，现在发现了" + res.name()

                    l_meshes = pm.listRelatives(res, ad=True, type='mesh')
                    if len(l_meshes) == 0:
                        return u"资产" + asset_name + u"下" + res.name() + u"组不能为空。请在这个组下建模或者把空组删了。"

                    if not lod and asset_type == 'flg' :
                        self.set_flg_lod(self.dialog.d_assets_info[asset_name])
                        lod=True
                    if not lod and res.nodeName() in ['md', 'lo']:
                        return u"资产" + asset_name + u"在 shotgun 没有勾选 Manual LOD (手工低模) ，所以不能 publish md/lo 模。"

                    if self.dialog.usd and res.nodeName() in ['hi', 'md', 'lo','proxy']:
                        for n in pm.listRelatives(res, c=True):
                            if n.nodeName() != 'mesh_grp':
                                return u"因为这是一个 USD 标准项目，资产" + asset_name + u"在 "+ res.nodeName() +u"下只能有一个组，且组节点名称必须是 mesh_grp。现在这个组名为" + n.nodeName()

                    print 'check '+res
                    if asset_type == 'flg':
                        if 'md' in res.nodeName() or 'lo' in res.nodeName():
                            l_meshes = pm.listRelatives(res, ad=True, type='mesh')
                            error_meshes=[m for m in l_meshes if ('_'+res) not in  m.nodeName()]
                            error_name_meshes.extend(error_meshes)


                if len(error_name_meshes)>0:
                    pm.select(error_name_meshes)
                    return u"flg 资产md/lo模型的mesh需要加 (md/lo) 的后缀:"+u" ,".join([n.nodeName() for n in error_name_meshes])

                l_meshes = pm.listRelatives('|{}|poly'.format(asset_name), ad=True, type='mesh')
                mesh_cnt = len(l_meshes)

                if mesh_cnt > 3000:
                    return u"资产:" + asset_name + u"资产模型数不能超过3000个，请合并同类的模型。"


                self.all_mesh = []
                if asset_type in ['chr'] and self.dialog.version_tag == u"精模":
                    sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                    if 'skip_skin_grp' in sg_info['tag_list']:
                        print "skin_grp skip"
                        return ''
                    if pm.objExists('|master|poly|hi|mesh_grp|skin_grp|'):

                        grp_skin = pm.ls('|master|poly|hi|mesh_grp|skin_grp|')[0]

                        self.check_all_skin_group(grp_skin)

                    else:
                        return u"没找到skin_grp组，请检查"

                    if self.all_mesh:
                        if 'skip_eyeball' in sg_info['tag_list']:
                            print "eyeball skip"
                            return ''
                        if "L_eyeball_geo" not in self.all_mesh:
                            return u'请检查左眼球晶状体是否缺失, 或者左眼球晶状体命名是否错误，名字应该是  L_eyeball_geo'

                        if "R_eyeball_geo" not in self.all_mesh:
                            return u'请检查右眼球晶状体是否缺失, 或者右眼球晶状体命名是否错误，名字应该是  R_eyeball_geo'

                    else:
                        return u"skin组是空的，请检查"
                if asset_type == 'flg':
                    if not mc.objExists('|master|poly|proxy|mesh_grp'):
                        return u'flg 类型资产，必须要有proxy，请手动创建或自动修复'
                    if len(mc.listRelatives('|master|poly|proxy|mesh_grp',ad=1,type ='mesh'))!=1:
                        return u'flg类型资产的proxy层级只能有一个mesh，以防maya2019xgen崩溃，' \
                               u'\n请combine为一个mesh并放到|master|poly|proxy|mesh_grp下'

            return ""

        except:
            return traceback.format_exc()

    def create_flg_proxy(self):
        if not self.auto:
            return '需要手动修复。'
        hi_grp_bbx = mc.xform('|master|poly|hi', q=1, bb=1)
        print 'bbx:  ', hi_grp_bbx
        proxy_x = hi_grp_bbx[3] - hi_grp_bbx[0]
        proxy_y = hi_grp_bbx[4] - hi_grp_bbx[1]
        proxy_z = hi_grp_bbx[5] - hi_grp_bbx[2]
        proxy_mesh = mc.polyCube(name='auto_proxy', width=proxy_x, depth=proxy_z, height=proxy_y)[0]
        trans_x, trans_y, trans_z = [(hi_grp_bbx[3] + hi_grp_bbx[0]) / 2,
                                     (hi_grp_bbx[4] + hi_grp_bbx[1]) / 2,
                                     (hi_grp_bbx[5] + hi_grp_bbx[2]) / 2]
        mc.setAttr(proxy_mesh + '.translateX', trans_x)
        mc.setAttr(proxy_mesh + '.translateY', trans_y)
        mc.setAttr(proxy_mesh + '.translateZ', trans_z)
        # pPlatonic1.scalePivot','pPlatonic1.rotatePivot
        mc.move(-trans_x, -trans_y, -trans_z, proxy_mesh + '.scalePivot', proxy_mesh + '.rotatePivot', r=1)
        proxy_grp = mc.group(name='proxy', parent='|master|poly', empty= 1)
        mc.group(proxy_mesh, name='mesh_grp', parent=proxy_grp)
        mc.select(proxy_grp,replace=1)
        mel.eval('FreezeTransformations;')
        mel.eval('DeleteHistory;')

    def run_fix(self):
        '''Auto Fix'''
        try:
            if not mc.objExists('|master|poly|proxy|mesh_grp'):
                self.create_flg_proxy()
                return ' '
            return ' '
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


