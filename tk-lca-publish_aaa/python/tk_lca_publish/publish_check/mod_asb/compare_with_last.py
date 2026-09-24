# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.01
#
# Description:
#
############################################
import traceback
import os
import sys
from xml.etree import ElementTree
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'和上一版本的 Assembly Reference 命名进行比对'
        self.description = u'如果上一版本资产 abc 调用进来，命名空间是abc；这个版本相同的资产的命名空间还得是abc，不能使abc1。'
        self.auto_fix = True
        self.duty = u'艺术家本人。'
        return

    def get_ar_dict(self, l_ar_path):
        d_ar = {}
        for path in l_ar_path:
            if path.endswith('_AR') and not ('_AR|' in path):
                ar_name = path.split('|')[-1]
                asset = ar_name[:-3].rstrip('0123456789')
                if not d_ar.has_key(asset):
                    d_ar[asset] = []
                d_ar[asset].append(ar_name)

        for asset, l_assets in d_ar.iteritems():
            l_assets.sort()
        return d_ar


    def get_ar_list(self, l_ar_path):
        d_ar = {}
        for path in l_ar_path:
            if path.endswith('_AR') and not ('_AR|' in path):
                ar_name = path.split('|')[-1]
                d_ar[ar_name] = path
        return d_ar


    def run_check(self):
        try:
            self.dialog.ar_msg=u""
            self.dialog.ar_info = {'add_ar': [],
                                   'remove_ar':[],
                                   'hierarchy_change': [],
                                   'xform_change': []}
            last_xml = self.dialog.publish_root + '/' + self.dialog.version_key + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            l_old_assets = []
            l_errs = []
            desp = u"和上一版模型相比:\n"

            if os.path.isfile(last_xml):
                f = open(last_xml, 'r')
                xml_text = f.read()
                f.close()

                root = ElementTree.fromstring(xml_text)
                l_attrs = root.getiterator('attribute')
                l_old_AR = [attr.attrib['value'] for attr in l_attrs if attr.attrib['name'] == 'fullPath']
                l_ar = pm.listRelatives('|master', ad=True, type='assemblyReference')
                l_new_AR = [ar.fullPath() for ar in l_ar]

                d_old_AR = self.get_ar_dict(l_old_AR)
                d_new_AR = self.get_ar_dict(l_new_AR)

                for asset, l_old_assets in d_old_AR.iteritems():
                    if not d_new_AR.has_key(asset):
                        continue

                    l_new_assets = d_new_AR[asset]
                    l_unmatched = []
                    for AR in l_old_assets:
                        if not AR in l_new_assets:
                            l_unmatched.append(AR)

                    for AR in l_new_assets:
                        if not AR in l_old_assets and len(l_unmatched) > 0:
                            l_errs.append(u"当前文件中的 " +AR+u" 在上一版本里叫 " + l_unmatched[0])
                            l_unmatched.pop(0)

                # Fill publish description
                d_old_AR = self.get_ar_list(l_old_AR)
                d_new_AR = self.get_ar_list(l_new_AR)
                l_ar_added = []
                l_ar_moved = []
                l_ar_removed = []
                msg_added = msg_moved = msg_removed = u""
                self.dialog.ar_msg = msg_added
                for ar_name in d_old_AR.keys():
                    if not d_new_AR.has_key(ar_name):
                        l_ar_removed.append(ar_name)
                    elif d_new_AR[ar_name] != d_old_AR[ar_name]:
                        l_ar_moved.append(ar_name)
                for ar_name in d_new_AR.keys():
                    if not d_old_AR.has_key(ar_name):
                        l_ar_added.append(ar_name)

                if len(l_ar_added) > 0:
                    self.dialog.ar_info['add_ar'] = l_ar_added
                    msg_added += u"新增了" + str(len(l_ar_added)) + u"个资产: \n"
                    self.dialog.ar_msg +=msg_added

                    if len(l_ar_added) > 5:
                        msg_added += u" ".join(l_ar_added[:5]) + u" ...\n"
                    else:
                        msg_added += u" ".join(l_ar_added) + u"\n"

                    self.dialog.ar_msg += u" \n".join(l_ar_added) + u"\n"

                if len(l_ar_removed) > 0:
                    self.dialog.ar_info['remove_ar'] = l_ar_removed
                    msg_removed += u"减少了" + str(len(l_ar_removed)) + u"个资产: \n"
                    self.dialog.ar_msg+=msg_removed
                    if len(l_ar_removed) > 5:
                        msg_removed += u" ".join(l_ar_removed[:5]) + u" ...\n"
                    else:
                        msg_removed += u" ".join(l_ar_removed) + u"\n"

                    self.dialog.ar_msg+= u" \n".join(l_ar_removed) + u"\n"
                if len(l_ar_moved) > 0:
                    msg_moved += u"有" + str(len(l_ar_moved)) + u"个资产改变了层级: \n"
                    self.dialog.ar_info['hierarchy_change'] = l_ar_moved
                    self.dialog.ar_msg+=msg_moved
                    if len(l_ar_moved) > 5:
                        msg_moved += u" ".join(l_ar_moved[:5]) + u" ...\n"
                    else:
                        msg_moved += u" ".join(l_ar_moved) + u"\n"
                    self.dialog.ar_msg += u" \n".join(l_ar_moved) + u"\n"
                    
                if msg_added == u"" and msg_moved == u"" and msg_removed == u"":
                    self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(desp + u" 本版本资产无变化。")
                else:
                    self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(desp + msg_added + msg_removed + msg_moved)

            return "\n".join(l_errs)
        except:
            return traceback.format_exc()


    def run_fix(self):
        try:
            last_xml = self.dialog.publish_root + '/' + self.dialog.version_key + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            l_old_assets = []
            l_errs = []
            if os.path.isfile(last_xml):
                f = open(last_xml, 'r')
                xml_text = f.read()
                f.close()

                root = ElementTree.fromstring(xml_text)
                l_attrs = root.getiterator('attribute')
                l_old_AR = [attr.attrib['value'] for attr in l_attrs if attr.attrib['name'] == 'fullPath']
                l_ar = pm.listRelatives('|master', ad=True, type='assemblyReference')
                l_new_AR = [ar.fullPath() for ar in l_ar]

                d_old_AR = self.get_ar_dict(l_old_AR)
                d_new_AR = self.get_ar_dict(l_new_AR)

                for asset, l_old_assets in d_old_AR.iteritems():
                    if not d_new_AR.has_key(asset):
                        continue

                    l_new_assets = d_new_AR[asset]
                    l_unmatched = []
                    for AR in l_old_assets:
                        if not AR in l_new_assets:
                            l_unmatched.append(AR)

                    for AR in l_new_assets:
                        if not AR in l_old_assets and len(l_unmatched) > 0:
                            ar = pm.PyNode(AR)
                            new_name = l_unmatched[0]
                            new_ns = new_name[:-3]
                            pm.lockNode(ar,lock=0)
                            ar.setAttr('repNamespace',l=False)
                            ar.setAttr('repNamespace', new_ns)
                            ar.rename(new_name)
                            l_unmatched.pop(0)

            return ''
        except:
            return traceback.format_exc()

        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

