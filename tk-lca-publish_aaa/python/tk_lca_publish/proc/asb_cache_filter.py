# -*- coding:utf-8 -*-

# Author: Chen Ming

import sys
import os
import maya.cmds as cmds
import pymel.core as pm
ATTRS_TO_HIDE = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v')


class fil():
    def __init__(self, filepath, threshold=0.005):
        print('init')
        self.filepath = filepath
        print('filepath:' + filepath)
        if not self.correct_path():
            return

        self.root = '|master|asb'
        if not pm.objExists(self.root):
            print 'not find master|asb node .'
            return
        self.root_node=pm.PyNode(self.root)
        self.threshold = threshold #objects smaller than this ratio will be hidden
        self.max_m = self.generate_max()

        cmds.select(cl = True)
        print('max_m: '+ str(self.max_m))
        print('root: '+ self.root)

        self.ignore_list = []
        self.ignore_tiny(self.root)
        
        print 'ignore asserts :',len(self.ignore_list)
        
        if len(self.ignore_list) != len(pm.ls(type='gpuCache')):
            for ass in self.ignore_list:
                self.clean_up(ass)

        print 'start write cache...'
        self.write_cache()

        return


    #check if the filepath if correct
    def correct_path(self):
        index = self.filepath.rfind('/')
        self.directory = self.filepath[:index]
        self.filename = self.filepath[index+1:]
        if os.path.isdir(self.directory):
            return True
        print('please provide a valid file path')
        return False
    #generate the max bounding box
    def generate_max(self):
        max_box = cmds.exactWorldBoundingBox(self.root)
        max_m = self.calc_m(max_box)
        return max_m

    #select the object if too small
    def ignore_tiny(self, node):

        #print('node name: '+ node)
        if cmds.nodeType(node) == 'gpuCache':
            return
        box = cmds.exactWorldBoundingBox(node)
        #print(box)
        sum = self.calc_m(box)
        #print(sum)
        if sum < self.max_m * self.threshold:
            if cmds.nodeType(node) == 'assemblyReference':
                self.ignore_list.append(node)
            else:
                self.ignore_list.extend(pm.listRelatives(node,type='assemblyReference',ad=True))

        else:
            if cmds.nodeType(node) == 'assemblyReference':
                #if 'env' not in cmds.getAttr(node+'.definition'):
                self.toProxy(node)


            children = cmds.listRelatives(node, children=True)
            if len(cmds.ls(node, dagObjects=True)) > 2:
                for child in children:
                    self.ignore_tiny(child)


        return 

        #helper function that helps calculate box measurement.
    def calc_m(self, box):
        sum = box[3]+box[4]+box[5]-box[0]-box[1]-box[2]
        return sum

    def toProxy(self, node):
        ref = pm.PyNode(node)
        reps = ref.getListRepresentations()
        # special form of proxy
        activeLabel=ref.getActiveLabel()

        if 'proxy.abc' in reps and 'proxy.abc' not in activeLabel:
            if 'Low' not in ref.getActiveLabel():
                try:
                    ref.setActiveLabel('Low')
                except:
                    pass
        elif not ref.getActiveLabel().endswith('.proxy.abc'):
            self.toCacheProxy(node)

        return
    #use proxy for objects that are too small
    def clean_up(self, node):
        ref=pm.PyNode(node)
        if pm.mel.eval('nodeType "%s"'%ref)=='assemblyReference':
            try:
                #print('cleaning',node)
                ref.setActive('')
                return
            except:
                print('cleaning error ',ref)
                pass

    def write_cache(self):
        pm.loadPlugin('gpuCache.so', quiet = True)
        gpu_list = pm.ls( type= 'gpuCache')
        if gpu_list:
            pm.gpuCache(gpu_list,q=1 ,waitForBackgroundReading=1)
            pm.gpuCache(self.root_node,  startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=True,dir=self.directory, dataFormat='ogawa', fileName=self.filename)
            
        return

    def toCacheProxy(self, node):
        ref = pm.PyNode(node)
        self.switchRep(ref, '.proxy.abc')
        self.setChannelBoxVisibility(node, ATTRS_TO_HIDE, True)
        return

    def switchRep(self, assembly, suffix):
        if not pm.objExists(assembly):
            print ('Node ' + assembly +' no longer exists, skipping...' )
            return False

        reps = assembly.getListRepresentations() or []
        for rep in reps:
            if rep.endswith(suffix):
                try:
                    assembly.setActiveLabel(rep)
                except:
                    pass
                return True

    def setChannelBoxVisibility(self, nodes, attrs, value):
        for node in nodes:
            if not pm.objExists(node):
                continue
            node = pm.nt.DependNode(node)
            for attr in attrs:
                path = node.longName()+'.'+attr
                if pm.listConnections(path, source=True, destination=False):
                    continue

                # for "The channelBox flag is ignored on keyable attributes."
                node.setAttr(attr, keyable=value)
                node.setAttr(attr, channelBox=value)
                node.setAttr(attr, keyable=value)
        return




# if __name__ == "__main__":
#     import maya.standalone
#     maya.standalone.initialize()
#
#     pm.loadPlugin('gpuCache.so', quiet = True)
#     pm.openFile('/mnt/work/shome/yuhuazhuo/to/chenming/north_area_a.mod.model.v047.ma')
#
#     fil('/mnt/work/shome/yuhuazhuo/to/chenming/test.assembly.v007')
#
#     print 'Done'
    # sys.exit(-1)
    # os._exit(0)