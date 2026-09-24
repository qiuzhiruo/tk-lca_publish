# -*- coding:utf-8 -*-

import os
import traceback
import shutil
import json
import pymel.core as pm
import pymel.core.nodetypes as nt

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录scn中所有AR资产的状态"
        self.description = u"将scn中AR资产写入json文件中"
        return
    
    def get_transform(self,ar):
        TR_ATTRS=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY','scaleZ']
        transform=[ar.getAttr(attr) for attr in TR_ATTRS]

        return transform
    
    
    def get_all_ar_status(self):
        """
        result: a dict, e.g.  {1: {u'polygon_AR': u'polygons.ma'},
                                          2: {u'polygon:pipe_AR': u'',
                                                u'polygon:sphere1_AR': u'Locator',
                                                u'polygon:sphere_AR': u'sphere.abc'}
                                         }
        """
        ar_levels = {}
        ars = pm.ls(type = 'assemblyReference')
        for ar in ars:
            ar_name = ar.name()
            level = ar_name.split(':')
            print ar_name, ar.getActiveLabel(), len(level)
            if len(level) not in ar_levels.keys():
                ar_levels[len(level)] = {}
            ar_levels[len(level)][ar_name] = [ar.getActiveLabel(),self.get_transform(ar)]
        
        return ar_levels

    def proceed(self):
        try:
            self.dialog.json_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.json'
            ar_levels = self.get_all_ar_status()
            f = open(self.dialog.json_file,'w')
            data_dict = json.dumps(ar_levels, sort_keys = True, indent = 4, separators = (',', ': '))
            f.write(data_dict)
            f.close()
            
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


