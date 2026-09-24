#! -*- coding:utf-8 -*-

__author__ = 'yuke'

import os
import hashlib
import maya.cmds as cmds

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查layers显示层是否被隐藏"
        self.description = u"检查动画文件的layers的有物体的显示层是否被隐藏显示，如果被隐藏检查不通过，用fix修复全部显示之后，重新拍屏再提交"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        self.assets_group = "|assets"
        self.not_vis = []
        layers = cmds.ls(type='displayLayer') or []
        for layer in layers:
            members = cmds.editDisplayLayerMembers(layer, query=True) or []
            if members:
                is_visible = cmds.getAttr(layer + ".visibility")
                if not is_visible:
                    self.not_vis.append(layer)
        current_file = cmds.file(query=True, sceneName=True)
        dirpath = os.path.dirname(current_file)
        move_filename = os.path.basename(current_file).replace('.ma', '.mov')
        move_filepath = os.path.join(dirpath, 'data', move_filename)
        if os.path.isfile(move_filepath):
            hash_value = self.move_sha256(move_filepath)
        else:
            return u'当前路径没有mov视频, {0}'.format(move_filepath)
        if self.not_vis:
            locked = cmds.lockNode(self.assets_group, q=True, lock=True)
            if locked and locked[0]:
                cmds.lockNode(self.assets_group, lock=False)
            if not cmds.attributeQuery('move_hash', node=self.assets_group, exists=True):
                cmds.addAttr(self.assets_group, longName='move_hash', dataType='string')
            cmds.setAttr(self.assets_group + '.move_hash', hash_value, type='string')
            cmds.lockNode(self.assets_group, lock=True)
            return u'注意显示层被隐藏的显示层，{0}'.format(self.not_vis)

        else:
            if not cmds.attributeQuery('move_hash', node=self.assets_group, exists=True):
                return ''
            else:
                old_hash = cmds.getAttr(self.assets_group + '.move_hash')
                if hash_value == old_hash:
                    cmds.confirmDialog(
                        title='Tip',
                        message=u'请重新拍屏',
                        button=['OK'],
                        defaultButton='OK'
                    )
                    return u'请重新拍屏后再进行提交'
                else:
                    return ''


    def move_sha256(self, move_path):
        f = open(move_path, 'rb')
        sha256 = hashlib.sha256()

        while True:
            data = f.read(8192)
            if not data:
                break
            sha256.update(data)

        f.close()
        move_sha256_data = sha256.hexdigest()
        return move_sha256_data

    def run_fix(self):
        if self.not_vis:
            for layer in self.not_vis:
                if cmds.objExists(layer):
                    cmds.setAttr(layer + '.enabled', 1)
                    cmds.setAttr(layer + '.visibility', 1)
                    cmds.refresh(force=True)
                    print layer
                    print cmds.objExists(layer)
                    print cmds.nodeType(layer)
                    print cmds.getAttr(layer + '.enabled')
                    print cmds.getAttr(layer + '.visibility')
            cmds.confirmDialog(
                title='Tip',
                message=u'显示层已经打开,请重新拍屏',
                button=['OK'],
                defaultButton='OK'
            )
        else:
            cmds.confirmDialog(
                title='Tip',
                message=u'请重新拍屏',
                button=['OK'],
                defaultButton='OK'
            )
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty