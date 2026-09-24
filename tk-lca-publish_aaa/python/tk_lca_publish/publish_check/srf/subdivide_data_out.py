# -*- coding:utf-8 -*-
__author__ = 'yingjie'


############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shtogun data
#
############################################

import traceback

import os
import re
from Katana import FarmAPI
import sgtk
from sgtk.platform.qt import QtCore, QtGui
import NodegraphAPI as ngapi
import traceback
import shutil
from xml.etree import ElementTree as ET

def write_attrs_to_publish_xml(old_xml):
        if not os.path.exists(old_xml):
            if  'efx' in old_xml:
                return ''
            else:
                return u'未找到xml文件' + old_xml
        
        xml_file='/tmp/subdivide.xml'
        if os.path.isfile(xml_file):
            os.remove(xml_file)
        shutil.copy(old_xml,'/tmp/subdivide.xml')

        subdiv_objects=[]
        #Get the object subdivide attributes
        ard_obj_set = ngapi.GetAllNodesByType('ArnoldObjectSettings')
        for ard in ard_obj_set:
            objects_value = ard.getParameter('CEL').getValue(0)
            if not objects_value or objects_value=='()':
                continue

            obj_value_str=objects_value[1:-2].split()
            iter_value = ard.getParameter('args.arnoldStatements.iterations.value').getValue(0)
            if ard.getParameter('args.arnoldStatements.smoothing.value').getValue(0):
                for o in obj_value_str:
                    master_pt = o.find('/master/')
                    subdiv_objects.append({'name':o[master_pt+1:],'iter':str(iter_value)})
        print 'Get subdivide data, num is',len(subdiv_objects)

        try:
            tree = ET.parse(xml_file)
        except Exception, e:
            return u'无法解析xml文件'+xml_file

        print 'Subdivide Data : Open scenegraph xml',xml_file

        root = tree.getroot()
        inst_list=root.getiterator('instance')
        for inst in inst_list:
            if inst.attrib.get('name','') == 'master':
                inst_attr = inst.getiterator('objAttributeList')
                if inst_attr:
                    for i in inst_attr:
                        i.clear()
                    inst_attr_temp=inst_attr[0]
                else:
                    inst_attr_temp = ET.SubElement(inst, 'objAttributeList')

                inst_attr_temp.set('version','0.0')
                for obj_attr in subdiv_objects:
                    attr_elem=ET.SubElement(inst_attr_temp, 'attribute')
                    attr_elem.set('name',obj_attr.get('name',''))
                    attr_elem.set('attr','subdivide')
                    attr_elem.set('value',obj_attr.get('iter',''))
        if tree:
            try:
                tree.write(xml_file)
            except:
                return u'写入subdivide data失败'

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Katana文件中物体的subdivide data。"
        self.description = u"Subdivide data要写进xml，方便efx读取使用。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def check_path(self, path, key):
        p = re.compile("[\w\.]*$")
        tokens = path.replace(":", "\\").replace("/", "\\").split("\\")
        for token in tokens:
            if not p.match(token):
                return key + u" 各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + path

        return ''


    def run_check(self):

        try:
            if int(self.dialog.w_publish_file.checkBox.isChecked()):
                return ''
            result= write_attrs_to_publish_xml(self.dialog.xml_file)
            if result:
                return result
            return''
        except:
            return traceback.format_exc()


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


