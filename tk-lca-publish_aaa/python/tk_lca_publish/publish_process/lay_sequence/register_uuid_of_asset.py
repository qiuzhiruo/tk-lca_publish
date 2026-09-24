# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description: Create version dir on the server
#
############################################

import os
import traceback
import ani.lca_pass_manager.pass_manager_model as pmm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"给所有角色注册UUID"
        self.description = u"给所有角色注册UUID, 为方便以后追踪pass信息"
        return

    def proceed(self):
        try:
            # add 添加角色 UUID信息
            pmm_cm = pmm.CharacterModel()
            pmm_cm.register_all_characters()

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
