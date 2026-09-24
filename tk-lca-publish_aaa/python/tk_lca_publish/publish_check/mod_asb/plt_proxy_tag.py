# -*- coding:utf-8 -*-
__author__ = 'yingjie'

import traceback
import os
import re
import maya.cmds as cmds

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"是否将flg类型的资产标记示意"
        self.description = u"为了避免 mod 植被和 plt 的植被冲突，mod可以将flg类的资产放在改组下|master|asb|plt_proxy_grp。skip tag: skip_plt_proxy"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    def run_check(self):
        try:
            scn_name = cmds.file(q=1,sn=1, shn=1).split('.')[0]
            sg_info = self.get_asset_shotgun_info(asset_name=scn_name)
            if sg_info:
                if 'skip_plt_proxy' in sg_info['tag_list']:
                    print 'skip plt_proxy_tag check'
                    return ''


            tl=cmds.ls(type='assemblyReference',l=True)
            error_list=[]
            for n in tl:
                if '/asset/flg/' in cmds.getAttr(n+'.definition'):
                    if not n.startswith('|master|asb|plt_proxy_grp|'):
                        error_list.append(n)

            if len(error_list)>10:

                return (u"发现场景中有超过10个flg类型的资产不在|master|asb|plt_proxy_grp 这个层级下面:\n" +u" ".join(error_list))

            else:
                return ""
        except:
            return traceback.format_exc()

        return ""

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
