#!-*- coding:utf-8 -*-
import traceback
import maya.cmds as cmds

import ani.lca_toggle_animation.functions as mute_f
reload(mute_f)


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有mute的动画曲线"
        self.description = u"动画曲线在pub时不可以被mute掉!"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        self.muted_data = {'facial': [], 'body': []}
        return

    def run_check(self):
        try:
            self.muted_data = {'facial': [], 'body': []}
            for i in cmds.ls('*:anim_controls_grp'):
                if cmds.objExists('{}.facial'.format(i)):
                    self.muted_data['facial'].append(i)
                if cmds.objExists('{}.body'.format(i)):
                    self.muted_data['body'].append(i)
            err_msg = ''
            if self.muted_data['facial']:
                err_msg += u'以下Chr的表情被mute了:\n{}'.format(', '.join(self.muted_data['facial']))
            if self.muted_data['body']:
                err_msg += u'以下Chr的身体被mute了:\n{}'.format(', '.join(self.muted_data['body']))
            if err_msg:
                return err_msg

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        if self.muted_data['facial']:
            cmds.select(self.muted_data['facial'])
            mute_f.main(facial=True, body=False, show_ui=False)
        if self.muted_data['body']:
            cmds.select(self.muted_data['body'])
            mute_f.main(facial=False, body=True, show_ui=False)
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
