# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Huang Xin
#
# Date: 2018.06.13
#
# 
#
########################################################################################

import os,sys,re,traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查生长面个数"
        self.description = u"每个description只能有1个生长面"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @staticmethod
    def check_patch_xml(xml_list):
        from lxml import etree as ET
        err_dict = {}
        for xml in xml_list:
            tree = ET.parse(xml)
            root = tree.getroot()
            patch_item=root.xpath('//patches')
            des_item = root.xpath('//description')[0]
            if len(patch_item) > 1:
                des_name = xml.split('/')[-1].split('.')[0]
                patches = [p.attrib['patchesName'] for p in patch_item]
                err_dict.setdefault(des_name, patches)

        return err_dict

    def run_check(self):
        try:
            proj = self.dialog.project['name']
            entity = self.dialog.entity['name']
            if not re.match('[a-z]\d{5}', entity):
                return ''
            output_cache=str(self.dialog.w_publish_file.lineEdit_cache.text())
            if output_cache:
                xml_list = []
                for root, dirs, files in os.walk(output_cache+'/cache'):
                    for f in files:
                        if f.endswith('.xml'):
                            xml_list.append(os.path.join(root, f))

                err_dict = StdCheck.check_patch_xml(xml_list)
                if err_dict:
                    info = u'Cache中包含多生长面，请检查!!!'
                    for des, patch in err_dict.items():
                        info += '\n'+des+u'有%d个生长面:\n'%len(patch)+', '.join(patch)
                    return info
            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            return ''

        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty
