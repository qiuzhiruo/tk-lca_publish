# -*- coding:utf-8 -*-

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
import Nodes3DAPI
import sgtk
from sgtk.platform.qt import QtCore, QtGui
import NodegraphAPI as ngapi

from production.shotgun_connection import Connection
sg = Connection('get_project_info').get_sg()

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查LookFileBake 相关信息。"
        self.description = u"LookFileBake节点是否能够正确bake，通过此检查来提醒制作人员。"
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
            assetinfo = sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
            asset_type =assetinfo.get('sg_asset_type','')

            klf_bake_node = ngapi.GetAllNodesByType('LookFileBake')
            if not klf_bake_node:
                return u'没有找到 LookFileBake 节点.'

            ##check root location
            if asset_type != 'crd':
                if len(klf_bake_node)>1:
                    return u'找到'+str(len(klf_bake_node))+u'个LookFileBake节点'

                root_location_param = klf_bake_node[0].getParameter('rootLocations')

                if root_location_param.getNumChildren()==0:
                    return u'LookFileBake 节点的root location 没有数值.'
                else:
                    root_loc_value = root_location_param.getChildByIndex(0).getValue(0)
                    if self.dialog.entity['name'] not in root_loc_value:
                        return u'LookFileBake root location 参数不对.'+self.dialog.entity['name']+u'应该在参数路径中'

                    if not root_loc_value.endswith('/master') and not root_loc_value.endswith('/master/'):
                        return u'Root location 应该以/master结尾.'

            for n in klf_bake_node:
                allIps=n.getInputPorts()
                for ip in allIps:
                    ipName=ip.getName()
                    ipts=ip.getConnectedPorts()
                    if not ipts:
                        return u'LookFileBake节点 '+klf_bake_node[0].getName()+u' inport '+ipName+u' 没有链接，会导致lookfile 无法bake'


            #make sure we can bake lookfile
            if not os.path.isdir('/tmp/klf_tst'):
                os.mkdir('/tmp/klf_tst')

            for n in klf_bake_node:
                klf_path = os.path.join('/tmp/klf_tst', n.getName()+'.klf')
                try:
                    Nodes3DAPI.LookFileBake.LookFileBake.WriteToLookFile(n, 0, klf_path)
                except:
                    return u'无法对节点：'+n.getName()+u'Bake LookFile'

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


