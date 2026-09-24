# -*- coding: utf-8 -*-
# @Time    : 18-5-8 下午3:03
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'



import traceback
import os
import pymel.core as pm


def check_master_mater(master):
    check = False
    master = pm.PyNode(master)
    anim_nodes = master.crd_srfrandid.listConnections(d=1, s=0, type='animCurveUU')
    maters = []
    if len(anim_nodes) == 0:
        return check
    else:
        for anim in anim_nodes:
            m = anim.listConnections(d=1, s=0)
            if m not in maters:
                maters.append(m)
    if len(maters) == 0:
        return check
    else:
        check = True
    return check


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查oat资产的子资产是否正确"
        self.description = u"文件内必须有对应的oat的子资产，且资产版本及链接信息必须正确!!!"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            assets = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                           ['code','assets'])
            #{'code': 'snakeman_norm_oat', 'type': 'Asset', 'id': 11861, 'assets': [{'type': 'Asset', 'id': 11577, 'name': 'snake_man_norm_a_crd'}]}
            oat_message = {}
            # oat_message = {'snake_man_stro_a_crd': {'modVersion': '004', 'rigVersion': '002'},
            #                'snake_man_stro_b_crd': {'modVersion': '003', 'rigVersion': '007'}}
            # get sub assets list and oat message dict
            sub_assets = []
            for sub in assets['assets']:
                sub_assets.append(sub['name'])
                sub_name = sub['name']
                modvs = self.dialog.sg.find('Version', [['project','is',self.dialog.project],
                                                  ['entity', 'name_is', sub_name],
                                                  ['sg_task.Task.content','is','model'],
                                                  ['sg_version_type','is','Downstream']],
                                        ['code'])
                modVersion = modvs[-1]['code'][-3:]
                rigvs = self.dialog.sg.find('Version', [['project','is',self.dialog.project],
                                                  ['entity', 'name_is', sub_name],
                                                  ['sg_task.Task.content','is','rigging'],
                                                  ['sg_version_type','is','Downstream']],
                                        ['code'])
                rigVersion = rigvs[-1]['code'][-3:]

                oat_message[sub_name] = {'modVersion': modVersion, 'rigVersion': rigVersion}
                print 'oat message is \n\t',oat_message
                # get scene master and checked
            masters = pm.ls('*_master')
            if len(masters) == 0:
                return u'没有发现资产模型请确认有模型存在!!!'
            if len(masters) < len(sub_assets):
                err_message = ','.join([i for i in sub_assets if
                                        i not in [j.name().replace('_master', '') for j in masters]])
                return u'缺少必要的子资产请找PC或组长确认!!!\n' + err_message

            err_masters = []
            check_attr = [u'modVersion', u'rigVersion']
            look_attr = u'crd_srfrandid'
            err_log_text = ''
            for master in masters:
                user_attrs = master.listAttr(userDefined=True)
                if len(user_attrs) == 0:
                    err_masters.append(master)
                    err_log_text = err_log_text + u'资产组没有自定义属性请确认 !!!\n\t' + master.name() + '\n'
                    continue
                user_attr_names = [i.attrName(longName=True) for i in user_attrs]
                if len([i for i in check_attr if i not in user_attr_names]):
                    err_masters.append(master)
                    err_log_text = err_log_text + u'缺少必要资产属性 !!!\n\t' + master.name() + '\n'
                for attr in user_attrs:
                    if attr.attrName(longName=True) in check_attr:
                        attr_value = attr.get()
                        sub_name = master.name().replace('_master', '')
                        check_value = oat_message[sub_name][attr.attrName(longName=True)]
                        if attr_value != check_value:
                            err_log_text = err_log_text + u'资产版本不对请更新资产 !!!\n\t' + master.name() + '\n'
                if look_attr in user_attr_names:
                    check_look = check_master_mater(master)
                    if not check_look:
                        err_log_text = err_log_text + u'master组没有到对应的材质球,请检查 !!!\n\t' + master.name() + '\n'
                    meshs = master.listRelatives(ad=1, type='mesh')
                    for mesh in meshs:
                        if mesh.intermediateObject.get() == 1:
                            continue
                        if not mesh.hasAttr('lca_crd_srfrandid'):
                            err_log_text = err_log_text + u'模型没有预设属性请检查模型是否正确  !!!\n\t' + str(
                                mesh.getParent()) + '\n'
                            continue
                        if len(mesh.lca_crd_srfrandid.inputs()) == 0 \
                                or mesh.lca_crd_srfrandid.inputs()[0] != master:
                            err_log_text = err_log_text + u'模型的预设属性lca_crd_srfrandid\n\t没有被%s组关联请检查!!!\n' % master.name()

            if err_log_text != '':
                return err_log_text
            else:
                return ''
            # Copy ma file
                
        except:
            return traceback.format_exc()

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
