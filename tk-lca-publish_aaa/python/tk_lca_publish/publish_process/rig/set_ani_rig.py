# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2016 Light Chaser Animation
#
# Author: Guo JianWei
#
# Date: 2016.10.19
#
# Description: Export rigging info
#
############################################
import traceback
import pymel.all as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog=None):
        self.dialog = dialog
        self.process_name = u"设置ani rig。"
        self.description = u"ani rig rename grps"
        return

    def proceed(self):
        try:
            if pm.objExists("poly"):
                for a in pm.listRelatives("poly",pa=1, ad=1):
                    isType = pm.ls(a,type= 'transform')
                    if isType:
                        a.rename("ani_"+a)
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

if __name__ == '__main__':
    main = StdProcess()
    main.write_asset_data()
