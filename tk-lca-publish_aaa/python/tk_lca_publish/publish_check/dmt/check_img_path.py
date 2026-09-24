# -*- coding:utf-8 -*-

import traceback

import os
import shutil
import nuke

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查素材路径"
        self.description = u"图片,.abc等素材必须放在task/nuke文件夹下（可以放在子文件夹下）"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def deselectAll(self):
        try:
            for n in nuke.selectedNodes():
                n['selected'].setValue(False)
        except:
            pass

    def findInputNodes(self, group, out):
        # out should be a dict, in the format of:
        # { 'read':{node:['knob', 'value1'], ...}, ... }
        children = group.nodes()
        for c in children:
            if c.Class() == 'Read':
                path = c['file'].getValue()
                out['img'].update( {c:['file', path]} )
                continue
            if c.Class() == 'ReadGeo2':
                path = c['file'].getValue()
                out['geo'].update( {c:['file', path]} )
                continue
            if c.Class() == 'Group':
                self.findInputNodes(c, out)

    def listFiles(self, dir, pattern, pad = ['%04d','####','%01d','#','%05d','#####','%03d','###','%02d','##']):
        if not os.path.isdir(dir):
            return []
        buffer = []
        for p in pad:
            if p in pattern:
                buffer = pattern.split(p)
                break
        if len(buffer)!=2:
            print dir+'/'+pattern+': unknown pattern'
            return []
        files = os.listdir(dir)
        f_filter = []
        for f in files:
            if f.startswith(buffer[0]) and f.endswith(buffer[1]):
                f_filter.append(f)
        return f_filter

    def run_check(self):
        try:
            backdrop = nuke.toNode('Stereo_Projection')
            if not backdrop:
                return u"找不到 Stereo_Projection backdrop!"

            self.deselectAll()
            backdrop.selectNodes()
            sel = nuke.selectedNodes()

            # analysing read and read geo nodes
            grps = [ s for s in sel if s.Class() == 'Group' and 'DMT_3D_Proj' in s.name() ]
            read_nodes = { 'img':{}, 'geo':{} }
            for g in grps:
                self.findInputNodes(g, read_nodes)

            illegal_files = []
            for k,v in read_nodes.iteritems():
                for n,f in v.iteritems():
                    # if '/task/nuke/' not in f[1].replace('\\', '/') and not f[1].startswith('/mnt/proj/'):
                    if not f[1].startswith('/mnt'):

                        illegal_files.append(n.name()+': '+f[1])

            if len(illegal_files)>0:
                return u"以下节点的素材文件不在/mnt/proj/文件夹下:\n"+'\n'.join(illegal_files)

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


