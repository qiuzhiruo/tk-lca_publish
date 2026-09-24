# -*- coding:utf-8 -*-
import traceback
import maya.cmds as cmds
from collections import OrderedDict
import lay.utilities.maya_common_ops as mco


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查TO_EFX下重命名的物体"
        self.description = u"|assets|lay|TO_EFX下重命名的物体会造成TO_EFX组下的特效示意导出报错"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def check_repeat_name(self):
        to_efx_grp = '|assets|lay|TO_EFX'

        if not cmds.objExists(to_efx_grp):
            return None

        cmds.select(to_efx_grp, r=True)
        mco.set_nodes_lock_status(lock_it=False)

        lay_all_obj = cmds.ls(to_efx_grp, dag=True, long=True, type="transform")
        lay_all_obj.remove(to_efx_grp)
        # 倒序排列, 保证先修改最里面层级obj
        lay_all_obj.reverse()

        # print lay_all_obj

        repeat_obj = OrderedDict()
        repeat_grp = OrderedDict()

        for i in lay_all_obj:
            if cmds.listRelatives(i,s=1):
                repeat_obj.setdefault(i.split('|')[-1].split(':')[-1], [])
                repeat_obj[i.split('|')[-1].split(':')[-1]].append(i)
            else:
                repeat_grp.setdefault(i.split('|')[-1].split(':')[-1], [])
                repeat_grp[i.split('|')[-1].split(':')[-1]].append(i)

        print "repeat_obj: ", repeat_obj
        print "repeat_grp: ", repeat_grp

        illegal_name = []
        illegal_name_grp = []

        for key, value in repeat_obj.items():
            if not len(value) > 1:
                continue
            print "key: ", key
            print "value: ", value

            illegal_name.append(value)
        
        for key, value in repeat_grp.items():
            if not len(value) > 1:
                continue
            print "key: ", key
            print "value: ", value

            illegal_name_grp.append(value)

        return illegal_name,illegal_name_grp

    def run_check(self):

        try:

            illegal_name,illegal_name_grp = self.check_repeat_name()

            illegal_names = illegal_name+illegal_name_grp
            if illegal_names:
                # print "illegal_name: \n"
                msg = ''
                for i in illegal_names:
                    msg += (str(i) + '\n')

                return u'illegal_names: {0}\n'.format(str(msg))

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:

            illegal_name,illegal_name_grp = self.check_repeat_name()
            print "illegal_name: ", illegal_name
            print "illegal_name_grp: ", illegal_name_grp

            for value in illegal_name:
                for num in range(len(value)):
                    # print num
                    value_new_name = "{0}_{1}_{2}".format(value[num].split('|')[-1], illegal_name.index(value),num)
                    cmds.rename(value[num], value_new_name)

            for value in illegal_name_grp:
                for num in range(len(value)):
                    # print num
                    value_new_name = "{0}_{1}_{2}".format(value[num].split('|')[-1], illegal_name_grp.index(value),num)
                    cmds.rename(value[num], value_new_name)

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
