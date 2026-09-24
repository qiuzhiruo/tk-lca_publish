# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Zhixiang
#
# Date:
#
# Description: As the description shows below
#
#
############################################

import os
import shutil
import glob
import traceback

from lxml import etree as ET

try:
    from pymel.core import *
    from pymel.mayautils import getMayaLocation

    xgenModelPath = getMayaLocation() + '/plug-ins/xgen/scripts'
    sys.path.append(xgenModelPath)
    import xgenm as xg
    import xgenm.xgGlobal as xgg
except:
    pass

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"对比上一版xgen的collection、desciption和之前版本有没有变化"
        self.description = u"对比上一版xgen的collection、desciption和之前版本有没有变化"
        return

    def read_xml_file(self, xml_file):
        result = {}
        tree = ET.parse(xml_file)
        root = tree.getroot()
        inst_nodes = root.xpath('//palette')
        if not inst_nodes:
            return
        for i in inst_nodes:
            collection_name = i.attrib['name']
            descrition_list = i.xpath('//description')
            if not descrition_list:
                continue
            temp_list = []
            for desc in descrition_list:
                temp_list.append(desc.attrib['name'])
            result[collection_name] = temp_list
        return result

    def compear_dic(self, dic_a, dic_b, order=True):
        result = ''
        if order:
            info = u'新增了'
        else:
            info = u'减少了'
        for new_coll in dic_a:
            if new_coll in dic_b:
                for new_dec in dic_a[new_coll]:
                    if new_dec not in dic_b[new_coll]:
                        result += (info + ' descirption  :%s --> %s\n' % (new_coll, new_dec))
            else:
                result += (info + ' collection   :%s\n' % new_coll)
        return result

    def proceed(self):
        try:
            # find all info xml files
            all_xml_file = sorted(glob.glob(os.path.dirname(self.dialog.version_dir) + '/*/hair_attr.xml'))
            if len(all_xml_file) > 1:
                current_xml, last_xml = all_xml_file[-1], all_xml_file[-2]
            else:
                return ""

            c = self.read_xml_file(current_xml)
            l = self.read_xml_file(last_xml)
            message = ''
            message += self.compear_dic(c, l, True)
            message += self.compear_dic(l, c, False)
            if not message:
                return ""
            else:
                message = u'对比版本' + '%s\n'%os.path.basename(os.path.dirname(last_xml)).rsplit('.',1)[-1] + message

            version_info = self.dialog.sg.find_one('Version', [['project', 'is', self.dialog.project],
                                                               ['code', 'is', self.dialog.version_name]],
                                                   ['id', 'description'])

            desc = version_info['description'].decode('utf-8') + '\n{' + message + '}'
            self.dialog.sg.update('Version', version_info['id'], {'description': desc})

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
