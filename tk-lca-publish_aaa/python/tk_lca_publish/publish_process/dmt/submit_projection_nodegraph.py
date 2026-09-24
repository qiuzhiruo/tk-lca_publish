# -*- coding:utf-8 -*-
__author__ = 'lvyuedong'

import os
import traceback
import shutil
import nuke


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出立体投射节点"
        self.description = u"将立体投射内的所有节点输出成.nk文件，并将连接的素材拷贝到 publish/img 和 geo 文件夹内。"
        return

    def deselectAll(self):
        try:
            for n in nuke.selectedNodes():
                n['selected'].setValue(False)
        except:
            pass

    def findInputNodes(self, group, out):
        # out should be a dict, in the format of:
        # { 'read':{node:['knob', 'value1', 'value2'], ...}, ... }
        children = group.nodes()
        for c in children:
            # skip disable node
            try:
                if c['disable'].getValue() == 1:
                    continue
            except:
                pass
            if c.Class() == 'Read':
                path = c['file'].getValue()
                out['img'].update({c: ['file', path, self.dialog.version_dir + '/img/' + os.path.basename(path)]})
                continue
            if c.Class() == 'ReadGeo2':
                path = c['file'].getValue()
                out['geo'].update({c: ['file', path, self.dialog.version_dir + '/geo/' + os.path.basename(path)]})
                continue
            if c.Class() == 'Group':
                self.findInputNodes(c, out)

    def listFiles(self, dir, pattern, pad=['%04d', '####', '%01d', '#', '%05d', '#####', '%03d', '###', '%02d', '##']):
        if not os.path.isdir(dir):
            return []
        buffer = []
        for p in pad:
            if p in pattern:
                buffer = pattern.split(p)
                break
        if len(buffer) != 2:
            print dir + '/' + pattern + ': unknown pattern'
            return []
        files = os.listdir(dir)
        f_filter = []
        for f in files:
            if f.startswith(buffer[0]) and f.endswith(buffer[1]):
                f_filter.append(f)
        return f_filter

    def proceed(self):
        try:
            try:
                if os.path.isdir(self.dialog.version_dir[:-5]):
                    shutil.rmtree(self.dialog.version_dir[:-5])
            except:
                return u"不能删除文件夹: " + self.dialog.version_dir + "， 请检查权限。"

            if os.path.isdir(self.dialog.version_dir + '/geo'):
                shutil.rmtree(self.dialog.version_dir + '/geo')
            os.makedirs(self.dialog.version_dir + '/geo')

            if os.path.isdir(self.dialog.version_dir + '/img'):
                shutil.rmtree(self.dialog.version_dir + '/img')
            os.makedirs(self.dialog.version_dir + '/img')

            # nk_file = nuke.root()['name'].getValue()
            nk_file = self.dialog.version_dir + '/' + self.dialog.version_name + '.nk'
            self.dialog.tank_file = nk_file

            backdrop = nuke.toNode('Stereo_Projection')
            if not backdrop:
                return 'Failed to find Stereo_Projection backdrop!'

            self.deselectAll()
            backdrop.selectNodes()
            sel = nuke.selectedNodes()

            # analysing read and read geo nodes
            grps = [s for s in sel if s.Class() == 'Group' and 'DMT_3D_Proj' in s.name()]
            read_nodes = {'img': {}, 'geo': {}}
            for g in grps:
                self.findInputNodes(g, read_nodes)

            # copy inputs of path to publish
            for k, v in read_nodes.iteritems():
                for n, f in v.iteritems():
                    if os.path.isfile(f[1]):
                        if not os.path.isfile(f[2]):
                            shutil.copyfile(f[1], f[2])
                    else:
                        # filename may contains %04d
                        src_dir = os.path.dirname(f[1])
                        dst_dir = os.path.dirname(f[2])
                        tmp = self.listFiles(src_dir, os.path.basename(f[1]))
                        for t in tmp:
                            if not os.path.isfile(dst_dir + '/' + t):
                                shutil.copyfile(src_dir + '/' + t, dst_dir + '/' + t)

            # copy .nk file (save as)
            try:
                self.deselectAll()
                backdrop.selectNodes()
                backdrop.setSelected(True)
                nuke.nodeCopy(nk_file)
            except:
                print 'something wrong happend when exporting nodes to nuke file.'

            # open .nk file and replace the path to publish
            sucess = False
            try:
                file = open(nk_file, 'r')
                content = file.read()
                file.close()
                sucess = True
            except:
                print 'Failed to open and write file: ' + nk_file

            if sucess:
                new_content = []
                for line in content.split('\n'):
                    replaced = False
                    if line.strip().startswith('file'):
                        for k, v in read_nodes.iteritems():
                            for n, f in v.iteritems():
                                if f[1] in line:
                                    line = line.replace(f[1], f[2])
                                    replaced = True
                                    continue
                            if replaced:
                                continue
                    new_content.append(line)
                file = open(nk_file, 'w')
                file.write('\n'.join(new_content))
                file.close()

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
