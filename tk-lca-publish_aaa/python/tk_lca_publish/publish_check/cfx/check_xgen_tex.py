# -*-coding:utf-8-*-
"""
 @Time : 4/18/23 9:32 PM
 @Author : Taka(xutao)
"""

import traceback
import os
import re
import maya.cmds as cmds
import pymel.core as pm
try:
    import xgenm as xgm
    import xgenm.xgGlobal as xgg
except:
    pass


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查xgen使用的贴图是否都已经bake"
        self.description = u"检查xgen每个description的ptx,xpd,xuv是否已经bake在work目录下"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            if 'cloth' in self.dialog.task['name'] or pm.ls(type='pgYetiMaya'):
                return ''

            collections = xgm.palettes()
            if not collections:
                return u'这个文件没有collection!'

            bad_str = ''
            self.work_path = os.path.dirname(cmds.file(q=True, sn=True))

            for collection in collections:
                descriptions = xgm.descriptions(collection)
                for description in descriptions:

                    primitive = xgm.getActive(collection, description, 'Primitive')
                    generator = xgm.getActive(collection, description, 'Generator')
                    renderer = xgm.getActive(collection, description, 'Renderer')

                    for obj in [primitive, generator, renderer]:
                        bad_str += self.check_tex(collection, description, obj)

                    fx_modules = xgm.fxModules(collection, description)
                    for fx_module in fx_modules:
                        if xgm.getAttr('active', collection, description, fx_module) == 'true':
                            bad_str += self.check_tex(collection, description, fx_module)

            return bad_str

        except:
            return traceback.format_exc()

    def check_tex(self, collection, description, obj):

        error_str = ''

        attrs = xgm.allAttrs(collection, description, obj)

        patches = xgm.boundGeometry(collection, description)

        for attr in attrs:
            attr_value = xgm.getAttr(attr, collection, description, obj)

            if '/paintmaps/' in attr_value:
                textures = re.findall(r'[(](.*?)[)]', attr_value)
                for texture in textures:
                    if '${DESC}' in texture:
                        tex = texture.split('/')[-1].strip('\'')
                        for patch in patches:
                            tex_path = os.path.join(self.work_path,
                                                    'xgen/collections/{0}/{1}/paintmaps/{2}/{3}.ptx'.format(
                                                        collection, description, tex, patch))
                            error_str += self.add_error(error_str, tex_path, collection, description, obj, attr)

            if '/${FXMODULE}/' in attr_value:
                for patch in patches:
                    fx_module_type = xgm.fxModuleType(collection, description, obj)
                    if fx_module_type == 'ClumpingFXModule':
                        if '/Maps/' in attr_value:
                            sub = '/Maps'
                            ext = 'ptx'
                        if '/Points/' in attr_value:
                            sub = '/Points'
                            ext = 'xuv'
                    elif fx_module_type == 'NoiseFXModule':
                        sub = ''
                        ext = 'xpd'
                    else:
                        sub = ''
                        ext = 'ptx'

                    tex_path = os.path.join(self.work_path,
                                            'xgen/collections/{0}/{1}/{2}{3}/{4}.{5}'.format(
                                            collection, description, obj, sub, patch, ext))
                    error_str += self.add_error(error_str, tex_path, collection, description, obj, attr)

            if 'Region' in attr_value:
                if obj == 'SplinePrimitive':
                    if xgm.getAttr('regionMask', collection, description, obj).split('.')[0] == '0':
                        continue
                if xgm.fxModuleType(collection, description, obj) == 'ClumpingFXModule':
                    if xgm.getAttr('useControlMaps', collection, description, obj) == '0':
                        continue

                region_l = [i for i in attr_value.split('/') if 'Region' in i]
                region = region_l[0]
                for patch in patches:
                    tex_path = os.path.join(self.work_path,
                                            'xgen/collections/{0}/{1}/{2}/{3}.ptx'.format(
                                                collection, description, region, patch))
                    if not os.path.exists(tex_path):
                        error_str += self.add_error(error_str, tex_path, collection, description, obj, attr)

        return error_str

    def add_error(self, str, path, collection, description, obj, attr):

        if not os.path.exists(path):
            str += u'%s -> %s 这个description的 %s -> %s 缺少贴图: %s\n' % (
                collection, description, obj, attr, path)
        return str


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