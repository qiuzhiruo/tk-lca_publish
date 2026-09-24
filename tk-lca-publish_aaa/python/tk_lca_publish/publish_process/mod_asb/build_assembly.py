# -*- coding:utf-8 -*-

import os
import shutil
import sys
import traceback
import re

import pymel.core as pm
import maya.OpenMaya as OpenMaya
import maya.app.general.editUtils as editUtils

lctools_env = os.environ.get('LCTOOLSET')
sys.path.append(lctools_env+'/tools')


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"构建 Assembly Reference 文件。"
        self.description = u"输出资产信息；根据信息文件构建 Assembly Reference文件；最后建立 Assembly Definition 文件。"
        return


    def create_asset_list(self):
        self.d_assets = {}
        self.d_sub_assets = {}
        l_nodes = pm.listRelatives('|master', ad=True, type='transform')
        for node in l_nodes:

            if sys.platform.startswith('win'):
                node_type=node.type()
            else:
                node_type=pm.mel.eval('nodeType "%s"'%node.name())
                if node_type=='AssemblyReference':
                    node_type='assemblyReference'

            if node.name().endswith(':master') and '_AR' not in node.fullPath():
                if not pm.objExists(node.name().replace(":master", ":global_ctrl")):
                    continue

                ctrl = pm.PyNode(node.name().replace(":master", ":global_ctrl"))
                self.d_assets[node.fullPath()] = {}
                self.d_assets[node.fullPath()]['path'] = pm.referenceQuery(node, filename=True)
                self.d_assets[node.fullPath()]['xform'] = pm.xform(ctrl, ws=True, q=True, m=True)

            elif node_type == 'assemblyReference':
                if not os.path.isfile(node.getAttr('definition')):
                    continue
                if ':' in node.name():
                    self.d_sub_assets[node.fullPath()] = pm.xform(node, ws=True, q=True, m=True)
                    continue
                fullPath = node.fullPath().replace('_AR', '')
                self.d_assets[fullPath] = {}
                self.d_assets[fullPath]['path'] = node.getAttr('definition')
                self.d_assets[fullPath]['xform'] = pm.xform(node, ws=True, q=True, m=True)
        return


    def get_ar_constraint(self,constraint_name):
        l_nodes = pm.listRelatives('|master', ad=True, type='assemblyReference')
        MAYA_VERSION = pm.about(version=True)[:4]

        if MAYA_VERSION == '2017':
            from maya.maya_to_py_itr import PyEditItr

            for ar_node in l_nodes:
                selectedAssembly = editUtils.makeDependNode(ar_node)
                edits = PyEditItr(OpenMaya.MItEdits(selectedAssembly , selectedAssembly, 1 , 1) )

                Constraint_StrC = re.compile(r'connectAttr "(.+).scale.+'+constraint_name)

                for e in edits:
                    e_str=e.getString()
                    match = Constraint_StrC.findall(e_str)
                    if match:
                        p_node_full_path=ar_node.fullPath()+'|'+match[0]
                        return p_node_full_path
        return
    def create_constraint_list(self):
        self.d_constraint = {}

        l_nodes = pm.listRelatives('|master', ad=True, type='parentConstraint',f=1)

        for c in l_nodes:
            if ':' not in c.name():
                print c.fullPath()
                c_node=c.getParent()
                if c.getTargetList():
                    p_node=c.getTargetList()[0]
                    self.d_constraint[c.name()]=[p_node.fullPath(),c_node.fullPath()]
                else:
                    p_node_fullPath=self.get_ar_constraint(c.name())
                    if p_node_fullPath:
                        self.d_constraint[c.name()]=[p_node_fullPath,c_node.fullPath()]

    def build_asb_ref(self):
        pm.newFile(force=True)
        for dg in sorted(self.d_assets.keys()):
            path = self.d_assets[dg]['path']
            tokens = dg.split('|')

            for i in range(1,len(tokens)-1):
                if not pm.objExists('|'.join(tokens[:i+1])):
                    n = pm.createNode('transform', name=tokens[i])
                    if pm.objExists('|'.join(tokens[:i])):
                        pm.parent(n, '|'.join(tokens[:i]))

                    if n.name() != tokens[i]:
                        n.rename(tokens[i])

            ar_parent = pm.PyNode('|'.join(tokens[:-1]))
            asset_ns = tokens[-1].split(':')[0]

            tokens = path.split('/')
            j = tokens.index('asset')
            asset_name = tokens[j+2]
            j = tokens.index('publish')

            #ad_ma = '/'.join(tokens[:j+2]) + '/assembly_definition/' + asset_name + '.ma'

            ar = pm.createNode("assemblyReference")
            hl = pm.createNode("hyperLayout", n= "hyperLayout_" + asset_ns)
            pm.connectAttr(hl.name()+".msg", ar.name()+".hl")
            ar.setAttr("definition", path)
            pm.mel.eval('AEassemblyChangeAttrNamespace "'+ar.name()+'.repNamespace" "'+asset_ns+'";')

            ar.rename(asset_ns + '_AR')
            pm.xform(ar, m=self.d_assets[dg]['xform'])
            pm.parent(ar, ar_parent)

        for dg in sorted(self.d_sub_assets.keys()):
            if pm.objExists(dg):
                pm.xform(dg, m=self.d_sub_assets[dg], ws=True)

        # Lock master and asb group
        for n_name in ['|master', '|master|asb']:
            if pm.objExists(n_name):
                n = pm.PyNode(n_name)
                for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                    n.setAttr(attr, l=True)


        for c_name,v in self.d_constraint.items():
            p_ar=pm.PyNode(v[0].split('AR')[0]+'AR')
            node_name = p_ar.name()
            base_name = re.sub(r'(_\d+)?_AR$', '', node_name).rstrip('0123456789') + '.ma'
            p_ar.setActive(base_name)
            c=pm.parentConstraint(v[0],v[1])
            c.rename(c_name)

        pm.saveAs(self.dialog.version_dir + '/assembly_reference/' + self.dialog.entity['name'] + '.ma' )
        pm.newFile(force=True)
        return

    def build_asb_proxy(self):
        print "self.dialog.version_dir:" + self.dialog.version_dir
        if os.path.isfile(self.dialog.proxy_file):
            pm.openFile(self.dialog.proxy_file , f=True)
            print "have proxy ......."
            # export cache
            pm.gpuCache('|master|proxy', startTime=1, endTime=1, optimize=True, optimizationThreshold=40000,
                        writeMaterials=True, saveMultipleFiles=False, dataFormat='ogawa', directory=self.dialog.version_dir + '/gpu',
                        fileName='proxy')
        else:
            print "no have proxy ......"
            pm.openFile(self.dialog.version_dir + '/assembly_reference/' + self.dialog.entity['name'] + '.ma', f=True)
            pm.gpuCache(pm.ls(type='gpuCache'), q=1, waitForBackgroundReading=1)
            proxy_path = self.dialog.version_dir + '/gpu/proxy'
            from proc import asb_cache_filter
            reload(asb_cache_filter)
            asb_cache_filter.fil(proxy_path)

        pm.newFile(force=True)

    def build_asb_def(self):
        maya_file = self.dialog.version_dir + '/assembly_reference/' + self.dialog.entity['name'] + '.ma'
        assembly_file = self.dialog.version_dir + '/assembly_definition/' + self.dialog.entity['name'] + '.ma'
        gpu_cache_file = self.dialog.version_dir + '/gpu/proxy.abc'
        proj_tags = self.dialog.sg.find_one('Project', [['name', 'is', self.dialog.project['name'].upper()]], ['tag_list'])['tag_list']
        if not 'No USD' in proj_tags:
            shutil.copyfile(os.path.dirname(__file__)+'/assembly_definition_usd.ma', assembly_file)
        else:
            shutil.copyfile(os.path.dirname(__file__)+'/assembly_definition.ma', assembly_file)
        f = open(assembly_file, 'r')
        l_lines = f.readlines()
        f.close()
        f = open(assembly_file, 'w')
        for line in l_lines:
            new_line = line.replace('{ASSET}', self.dialog.entity['name'])
            new_line = new_line.replace('{MAYA_FILE}', maya_file)
            new_line = new_line.replace('{GPU_CACHE_PROXY}', gpu_cache_file)

            f.write(new_line)
        f.close()

        self.dialog.assembly_definition = assembly_file
        return


    def proceed(self):
        try:
            try:
                pm.loadPlugin('sceneAssembly', quiet=True)
            except:
                print 'Failed to load sceneAssembly plugins. Skip'
                return ""

            # Create Folders
            if not os.path.isdir(self.dialog.version_dir + '/assembly_reference/'):
                os.makedirs(self.dialog.version_dir + '/assembly_reference/')
                os.makedirs(self.dialog.version_dir + '/gpu/')
            if not os.path.isdir(self.dialog.version_dir + '/assembly_definition/'):
                os.makedirs(self.dialog.version_dir + '/assembly_definition/')


            self.create_asset_list()
            self.create_constraint_list()

            self.build_asb_ref()
            self.build_asb_proxy()
            self.build_asb_def()
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


