# -*- coding:utf-8 -*-
import maya.cmds as cmds
# import pymel.core as pm
import traceback


# check if assets were hidden

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查assets组下的组是否被隐藏'
        self.description = u'assets组下的组不可以隐藏'
        self.auto_fix = True
        self.hidden_groups = []
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            checklist = cmds.listRelatives('|assets', f=True)
            for cl in checklist:
                if not cmds.getAttr(cl + '.visibility'):
                    self.hidden_groups.append(cl)

            if self.hidden_groups:
                return u"assets组下的组不可以隐藏，以下组是隐藏的:\n" + '\n'.join(self.hidden_groups)
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        if self.hidden_groups:
            for hg in self.hidden_groups:
                cmds.setAttr(hg + '.visibility', 1)
            self.hidden_groups = []

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
