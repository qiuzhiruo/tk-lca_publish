# -*- coding:utf-8 -*-
import re
import traceback
import os
import maya.mel as mel
import maya.cmds as cmds
# import pymel.core as pm
import production.mayautils as mutils


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产pass"
        self.description = u"检查资产pass与shotgun镜头记录是否一致(自动修复之前会自动增量保存文件)"
        self.auto_fix = True
        self.duty = u"艺术家本人和PC。"
        return

    def run_check(self):
        try:
            rig_passes = self.dialog.sg.find_one('Shot', [['project', 'is', self.dialog.project],
                                                          ['code', 'is', self.dialog.entity['name']]],
                                                 ['sg_rig_passes'])['sg_rig_passes']
            errorLog = ''
            print "rig_passes: ", rig_passes
            for rig_pass in rig_passes:
                passInfo = self.dialog.sg.find_one('CustomEntity10', [['project', 'is', self.dialog.project],
                                                                      ['id', 'is', rig_pass['id']]],
                                                   ['sg_asset', 'sg_value', 'sg_attribute'])

                asset = passInfo['sg_asset']['name']
                attr = passInfo['sg_attribute']
                if not attr.endswith('rigPass') and not attr.endswith('rig_pass'):
                    attr = attr.rsplit('.',1)[0]
                if not attr.startswith('visibility'):
                    attr = attr.split('.',1)[-1]
                value = passInfo['sg_value']
                print "asset, attr, value: ", str([asset, attr, value])

                # get all assets under assets group
                assets_exists_all = cmds.ls("{0}*:master".format(asset))
                print "assets_attr_all: ", str(assets_exists_all)
                assets_filter = "{}[0-9]*:master".format(asset)
                if assets_exists_all:
                    for asset_exist_alone in assets_exists_all:
                        if not re.search(assets_filter, asset_exist_alone):
                            continue
                        asset_a = str(asset_exist_alone).split(":master")[0]
                        asset_a_attr = "{0}:{1}".format(asset_a, attr)
                        if not cmds.objExists(asset_a_attr):
                            asset_a_attr = asset_a_attr.replace('rigPass','rig_pass')
                        if cmds.objExists(asset_a_attr):
                            if cmds.getAttr(asset_a_attr) != value:
                                errorLog += '资产%s的%s属性值与shotgun信息不符，shotgun上记录显示该值应为%s，请修正属性值，如有疑问请与pc或总监沟通。\n' % (
                                    asset_a, attr, value)
                        else:
                            errorLog += '资产%s的%s属性没有找到，请检查资产%s上的pass相关属性是否与shotgun上记录相符。\n' % (
                                asset_a, attr, attr.split('.')[0])

            if errorLog:
                return errorLog

            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        # 以防万一, 在此增量保存一版文件
        # force to save the original file and incremental file
        try:
            mel.eval('incrementalSaveScene;')
        except:
            mel.eval('file -force -save -options "v=0";')

        rig_passes = self.dialog.sg.find_one('Shot', [['project', 'is', self.dialog.project],
                                                      ['code', 'is', self.dialog.entity['name']]],
                                             ['sg_rig_passes'])['sg_rig_passes']

        for rig_pass in rig_passes:
            passInfo = self.dialog.sg.find_one('CustomEntity10',
                                               [['project', 'is', self.dialog.project], ['id', 'is', rig_pass['id']]],
                                               ['sg_asset', 'sg_value', 'sg_attribute'])

            asset = passInfo['sg_asset']['name']
            attr = passInfo['sg_attribute']
            value = passInfo['sg_value']

            assets_attr_all = cmds.ls("{0}*:{1}".format(asset, attr))
            assets_attr_filter = "{0}[0-9]*:{1}".format(asset, attr)

            for asset_attr_alone in assets_attr_all:
                if not re.search(assets_attr_filter, asset_attr_alone):
                    continue
                if cmds.objExists(asset_attr_alone):
                    cmds.setAttr(asset_attr_alone, value)

                    if cmds.listConnections(asset_attr_alone, d=0):
                        connections = cmds.listConnections(asset_attr_alone, d=0)
                        for connection in connections:
                            try:
                                cmds.delete(connection)
                            except:
                                pass

        cmds.confirmDialog(title='Warning', message=u'RigPass修复完成,角色样子会有变化,请重新拍屏!\n如有疑问, 请@TD!')
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
