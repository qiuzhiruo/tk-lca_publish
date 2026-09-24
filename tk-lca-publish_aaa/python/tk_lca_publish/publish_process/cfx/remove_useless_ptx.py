# -*-coding:utf-8-*-
"""
 @Time : 3/18/23 3:20 PM
 @Author : Taka(xutao)
"""

import os, sys, shutil, traceback

import pymel.core as pm
import maya.mel as mel

try:
    import xgenm as xgm
except:
    pass


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"删除未使用到的 Xgen UV Ptex贴图"
        self.description = u"删除未使用到的 Xgen UV Ptex贴图"
        return

    def proceed(self):
        try:
            if 'cloth' in self.dialog.task['name'] or pm.ls(type='pgYetiMaya'):
                return ''

            collections = xgm.palettes()
            if not collections:
                return u'这个文件没有collection!'

            work_path = pm.workspace(q=True, rd=True)
            for collection in collections:
                descriptions = xgm.descriptions(collection)
                for description in descriptions:
                    u_ptex_path = os.path.join(work_path, 'xgen/collections/{0}/{1}/paintmaps/UV_uparamcoord'.format(collection, description))
                    v_ptex_path = os.path.join(work_path, 'xgen/collections/{0}/{1}/paintmaps/UV_vparamcoord'.format(collection, description))

                    patches = xgm.boundGeometry(collection, description)

                    patches_ptex = ['%s.ptx' % patch for patch in patches]

                    for uv_path in [u_ptex_path, v_ptex_path]:
                        for ptx in os.listdir(uv_path):
                            if ptx not in patches_ptex:
                                path = os.path.join(uv_path, ptx)
                                if os.path.isdir(path):
                                    shutil.rmtree(path)
                                if os.path.isfile(path):
                                    os.remove(path)

            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description