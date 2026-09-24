# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.10
#
# Description: export action nodes for use in Miarmy
#
############################################
import traceback
import sys
import os

import pymel.core as pm

import production.mayautils.decorators as md
reload(md)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"分段输出模型缓存。"
        self.description = u"分段输出模型缓存，适用于Houdini Instance流程。"
        return

    @md.d_disableViews
    def proceed(self):
        try:
            # create cache folder
            output_dir = os.path.join(self.dialog.version_dir, 'cache')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, 0777)

            # get asset namespace
            asset_namespace = self.dialog.skeletons_group.namespace().strip(':')

            # load Alembic Export plugin
            pm.loadPlugin('AbcExport', quiet=True)

            # setup and export geo cache
            import production.CacheUtils.CacheXml as cx
            import production.CacheUtils.Common as cc

            motion_param = cc.getMotionblurParameter(self.dialog.project['name'],
                                                     self.dialog.entity['name'],
                                                     True)
            # before publish
            import ani.lca_before_publish
            ani.lca_before_publish.run()
            
            for data in self.dialog.actions_data:
                path = os.path.join(output_dir, data['name'])
                path = os.path.normpath(path)
                if not os.path.exists(path):
                    os.makedirs(path, 0777)
                cx.do_cache(path,
                            asset_namespace,
                            data['start'],
                            data['end'],
                            motion_param,
                            cache_shape=True)
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
