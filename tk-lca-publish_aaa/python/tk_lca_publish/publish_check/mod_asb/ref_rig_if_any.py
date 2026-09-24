# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback

import os
import re
import pymel.core as pm

import sys
# sys.path.append('U:/toolset/lib/production')
# sys.path.append('/mnt/utility/toolset/lib/production')
# sys.path.append('/Volumes/utility/toolset/lib/production')

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"优先使用rigging，不能使用rigging_layout。"
        self.description = u"如果资产有对应的rig版本，则不能再reference模型版本。不能使用rigging_layout 或者其他特殊 rigging版本。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        self.auto_fix_list = []
        return

    def run_check(self):

        try:
            ref_master = pm.ls(type='assemblyReference')
            
            rig_ref = []
            rig_special = []
            #from production.shotgun_connection import Connection
            #sg = Connection('get_project_info').get_sg()
            for r in ref_master:
                try:
                    try:
                        ref_mod_file = str( r.getAttr('definition')).replace('\\', '/')
                        if '/mod/' in ref_mod_file and r.hasAttr('rigPath'):
                            # this is a reference of rig asset that reference to model asset
                            ref_mod_file = str( pm.referenceQuery(r, f=True, wcn=True, p=True) ).replace('\\', '/')
                        elif '/rig/publish/' in ref_mod_file:
                            tokens = ref_mod_file.split('/')
                            i = tokens.index('publish')
                            v_name = tokens[i+1]
                            if not v_name.endswith('.rig.rigging'):
                                rig_special.append(ref_mod_file)
                                self.auto_fix_list.append(r)
                    except:
                        print 'Failed to get filename for reference: '+r.name()
                        continue
                    asset_name = os.path.basename( ref_mod_file )[:-3]
                    gpu_catch = ref_mod_file.split(asset_name)[0] + asset_name + '/rig/publish/' + asset_name + '.rig.rigging/gpu_ma/' + asset_name + '.abc'
                    if not os.path.exists(gpu_catch):
                        continue
                    if '/mod/' in ref_mod_file:
                        ref_rig_file = ref_mod_file.split(asset_name)[0] + asset_name + '/rig/publish/' + asset_name + '.rig.rigging/' + asset_name + '.ma'
                        if os.path.isfile(ref_rig_file):
                            # check mission status
                            try:
                                asset_info = self.dialog.sg.find_one('Task', [['entity.Asset.code', 'is', asset_name], ['content', 'is', 'rigging'], ['project.Project.name','is',self.dialog.project['name']]], ['id', 'sg_status_list'])
                            except:
                                print 'Failed to get task info from shotgun for asset: '+asset_name
                                continue
                            if asset_info and asset_info['sg_status_list'] in ['ip', 'fin', 'aa', 'sc', 'da']:
                                rig_ref.append( r.name() )
                                self.auto_fix_list.append(r)
                except:
                    pass
            if len(rig_ref)>0:
                pm.select(rig_ref)
                return u"下列资产应该reference对应的rig版本: " + '\n'.join(rig_ref)

            if len(rig_special)>0:
                pm.select(rig_special)
                return u"下列资产应该reference标准绑定 .rig.rigging 版本: " + '\n'.join(rig_special)

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        
        for r in self.auto_fix_list:
            ref_mod_file = str(r.getAttr('definition')).replace('\\', '/')
            asset_name = os.path.basename(ref_mod_file)[:-3]
            ref_rig_file = ref_mod_file.split(asset_name)[0] + asset_name + '/rig/publish/' + asset_name + '.rig.rigging/assembly_definition/' + asset_name + '.ma'
            if os.path.isfile(ref_rig_file):
                r.setAttr('definition',ref_rig_file)

        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


