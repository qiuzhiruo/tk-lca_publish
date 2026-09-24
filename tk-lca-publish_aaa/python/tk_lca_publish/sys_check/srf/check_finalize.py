# -*- coding:utf-8 -*-
__author__='yingjie'

import traceback
from Katana import NodegraphAPI


# All system check classes will use StdCheck as the class name.
class StdCheck():


    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否已经通过Srf Finalize的检查"
        self.description = u"材质必须通过Srf Finalize的检查，最少要通过'check'和'publish check'"
        self.auto_fix = False
        self.duty = u"Srf"
        return


    def run_check(self):
        try:
            checkbox_labels = ['check', 'publish_check']
            xml_node = NodegraphAPI.GetNode('AssetXmlIn_Lc')
            if not xml_node:
                for group_node in NodegraphAPI.GetAllNodesByType('Group'):
                    if 'AssetXmlIn_Lc' in group_node:
                        xml_node = group_node
                        break
            if not xml_node:
                return u"哥们没找到AssetXmlIn_Lc节点！"
            xml_user = xml_node.getParameter('user')
            finalize_check = None
            for child in xml_user.getChildren():
                if child.getName() == 'finalize_check':
                    finalize_check = child
                    break
            if finalize_check:
                check_parameter = finalize_check.getChildren()
                check_list = []
                srf_finalize = {}
                if check_parameter:
                    for i in check_parameter:
                        if i.getName() in checkbox_labels:
                            check_list.append(i.getName())
                            srf_finalize[i.getName()] = i.getValue(0)
                    result = [item for item in checkbox_labels if item not in check_list]
                    if result:
                        return u"请正确打开文件！"
                else:
                    return u"请正确打开文件！"
                if srf_finalize['check'] == 'Yes' and srf_finalize['publish_check']=='Yes':
                    return u''
                elif srf_finalize['check'] == 'True' and srf_finalize['publish_check']=='True':
                    return u''
                else:
                    return u'请先用srfFinalize做文件预检查！'

            else:
                return u"请正确打开文件！"

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

