# -*- coding:utf-8 -*-
__author__ = 'xiangquan'


import traceback
import os
import pymel.core as pm

import publish_process.ani.list_ani_assets as laa;reload(laa)

from sgtk.platform.qt import QtCore, QtGui

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查镜头中ani_assets的数量'
        self.description = u'镜头中ani_assets的数量如果超过200个，需要farm负责人填Note才可以通过检查'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            if not hasattr(self.dialog, 'assetDatas'):
                laa_std = laa.StdProcess(self.dialog)
                laa_std.get_reference_assets()
                laa_std.get_assembly_assets()
                self.dialog.assetDatas = laa_std.l_assets       # a list
            
            if self.dialog.step['name'] == 'flo':
                status = ['edited']
            elif self.dialog.step['name'] == 'ani':
                status = ['animated', 'constrained']
            
            useful_assetData = [assetData for assetData in self.dialog.assetDatas if str(assetData.status) in status]
            self.dialog.print_log('self.dialog.assetDatas: %d' % len(self.dialog.assetDatas) )
            self.dialog.print_log('useful_assetData: %d' % len(useful_assetData) )
            if len(useful_assetData) > 400:
                notes = self.dialog.sg.find('Note', [['note_links', 'is', self.dialog.entity], ['created_at', 'in_last', (1, 'DAY')]], 
                                            ['content', 'user.HumanUser.login', 'user.HumanUser.permission_rule_set'])
                if len(notes) <= 0:
                    QtGui.QMessageBox.warning(self.dialog, 'Warning', u'需要出cache的资产数量超过200，请检查文件\n若确实有这么多资产，请联系程顺跳过检查。')
                    return u'Too Many assets: ', len(useful_assetData)
                else:
                    version = self.dialog.version_name[-4:]
                    for note in notes:
                        content = note['content']
                        if content is None:
                            continue
    
                        if isinstance(content, str):
                            content = content.decode('utf-8')
                        content = content.lower().replace(' ', '').replace('-', '')
                        if any(i in content for i in (u'%s%s允许发到farm' % (self.dialog.step['name'], version), u'%s%sallowsubmittofarm' % (self.dialog.step['name'], version))) and \
                           (note['user.HumanUser.login'] in ['chengshun','zhangzheng'] or note['user.HumanUser.permission_rule_set']['name'] in ['Admin', 'Manager']):
                            return ''
                    QtGui.QMessageBox.warning(self.dialog, 'Warning', u'需要出cache的资产数量超过200，请检查文件\n若确实有这么多资产，请联系程顺跳过检查。')
                    return u'Too Many assets', len(useful_assetData)
            else:
                return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            for n in pm.ls(type='assemblyDefinition'):
                pm.delete(n)
            return ''
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

