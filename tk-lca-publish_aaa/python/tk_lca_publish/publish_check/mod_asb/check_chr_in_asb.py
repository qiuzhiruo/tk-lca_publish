# -*- coding:utf-8 -*-

import maya.cmds as cmds


class MG:
    error_type = ['chr']


# All system check classes will use StdCheck as the class name.
class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查asb资产中的人物"
        self.description = u"检查asb资产中是否包含人物资产。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        if not cmds.objExists('|master|asb'):
            return ''

        error_info = {}
        for ar_node in cmds.ls(typ='assemblyReference'):
            asset_type = cmds.getAttr('{}.definition'.format(ar_node)).split('/')[6]
            if asset_type in MG.error_type:
                if asset_type in error_info:
                    error_info[asset_type].append(ar_node)
                else:
                    error_info.update({asset_type: [ar_node]})

        if error_info:
            all_err_nodes = []
            for k, v in error_info.items():
                all_err_nodes.extend(list(v))
            cmds.select(all_err_nodes)

            err_msg = u'场景中包含{}类型的资产' \
                      u'节点分别是\n{}\n'.format(list(error_info.keys()), '\n'.join(all_err_nodes))
            return err_msg
        else:
            return ''

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


