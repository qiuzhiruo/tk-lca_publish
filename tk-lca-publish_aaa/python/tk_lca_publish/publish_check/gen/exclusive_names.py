# -*- coding:utf-8 -*-

import traceback
import pymel.core as pm
import maya.cmds as cmds


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查assets下重命名的物体"
        self.description = u"重命名的物体会造成xml文件无法输出"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def getTransforms(self, top=None, recursive=True, skipmaster=True):
        children = pm.listRelatives(top, c=True, type='transform')
        trans = []
        for c in children:
            if 'lay' in c.name():
                continue
            if skipmaster and ':master' in c.name():
                trans.append(c.name())
                continue
            trans.append(c.name())
            if recursive:
                trans.extend(self.getTransforms(top=c, recursive=recursive, skipmaster=skipmaster))
            else:
                trans.extend(self.getTransforms(top=c, recursive=recursive, skipmaster=skipmaster))
        return trans

    def getTransforms2(self, root):
        return cmds.ls(root, dag=True, type='transform')

    def select_obj(self, names):
        try:
            name = names[0].split('|')[-1]
            objs = pm.ls(name)
            if objs:
                pm.select(objs)
        except:
            pass

    def check_flg(self, node):
        ar_n = node.split('|')[-1].rsplit(':', 1)[0]+'_AR'
        if cmds.objExists(ar_n) and cmds.nodeType(ar_n) == 'assemblyReference':
            # ar_p = cmds.assembly(ar_n, q=True, al=True)
            ar_p = cmds.getAttr('%s.definition' % ar_n)
            if ar_p and ar_p.startswith('Z:') and '/flg/' in ar_p:
                return True
            elif  ar_n and ar_p.startswith('/mnt/') and '/flg/':
                return True
            else:
                return False
        else:
            return False


    def run_check(self):
        try:
            trans = self.getTransforms2('|assets')
            # trans.extend([i.name() for i in pm.ls('assets')])
            # illegal_name = []
            # for t in trans:
            #     if '|' in t:
            #         illegal_name.append( t )
            # if illegal_name:
            #     self.select_obj(illegal_name)
            #     return u"发现重命名的物体:\n" + '\n'.join( illegal_name )

            bad_nodes_ = [i for i in trans if '|' in i]
            bad_nodes_2 = [cmds.ls(i, long=1)[0] for i in bad_nodes_ if pm.nodeType(i) == 'transform']
            bad_nodes_3 = [node for node in bad_nodes_2 if '|lay|' not in node]
            bad_nodes_4 = [node for node in bad_nodes_3 if not self.check_flg(node)]

            # fix bug of prp include |hi|mesh_grp and |low|mesh_grp
            try:
                bad_nodes_not_reference = [node for node in bad_nodes_4 if
                                           not cmds.referenceQuery(node, isNodeReferenced=True)]
            except:
                bad_nodes_not_reference = bad_nodes_4

            # cmds.referenceQuery(ancg, isNodeReferenced=True)

            bad_nodes = list(set([obj.split('|')[-1] for obj in bad_nodes_not_reference]))
            if bad_nodes:
                self.select_obj(bad_nodes)
                notes = []
                for obj in bad_nodes:
                    one_string = str([i.fullPath() for i in pm.ls(obj)])
                    notes.append(one_string)

                str1 = u'以下物体重名，请修改：\n' + '\n'.join(notes)
                str2 = u'共有 {} 组物体重名'.format(len(bad_nodes))
                str2_2 = str(bad_nodes)
                str3 = u'已经自动选中了一组，请在大纲中按F查看'
                str4 = u'若资产为[scn]中的flg(植被)资产 且 无动画 请将[Active Representation]标签切换为 [abc] 或 [ma]'

                return u'\n'.join([str1, str2, str2_2, str3, str4])

            return ""

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
