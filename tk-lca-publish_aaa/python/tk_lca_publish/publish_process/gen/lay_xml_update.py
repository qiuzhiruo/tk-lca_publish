# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import math
import shutil
import sys
import xml.etree.ElementTree as ET

class LayXmlUpdate():
    '''
    This class should be used to update layout scene graph xml
    If find any assembly in layout, this class will find and compare the assembly with same name under mod directories,
    if any discrepancy exists, an error will be raised to inform set dressing artist, implying the layout artist should publish
    the latest version.

    > LayXmlUpdate(path_to_layout_xml): initiate with path to layout xml file
    > update(): will return the updated tree, that can be put into write() to write the tree out as xml
    > write(path_to_xml): write the updated tree to path_to_xml file
    > updateProjectCode('god'): specify the project code by string, should be used before update(), after initialization, the default project is god

    example:
    > lay_xml = LayXmlUpdate(input_xml)     -> initialize
    > tree = lay_xml.update()               -> get updated tree
    > lay_xml.write( output_xml )           -> write updated tree
    or you can use builtin write method as:
    > tree.write( output_xml )              -> write updated tree by builtin method of ElementTree
    you can combine update() and write() as:
    > lay_xml.updateAndWrite( output_xml )  -> update and write at once
    '''

    def __init__(self, xml):
        self.xml_file = self.osPathConvert(xml)
        self.tree = None
        self.root = None
        self.getXMLTree()
        self.version = self.getPythonVersion()
        self.project_code = 'god'
        self.asset_path = self.osPathConvert('/mnt/proj/projects/'+self.project_code+'/asset/')
        self.verbose = 0

    def osPathConvert(self, path):
        if os.name == 'nt':
            if path.startswith('/mnt/proj/'):
                return path.replace('/mnt/proj/', 'Z:/')
            elif path.startswith('/mnt/work/'):
                return path.replace('/mnt/work/', 'W:/')
            else:
                return path
        else:
            if path.startswith('Z:/'):
                return path.replace('Z:/', '/mnt/proj/')
            elif path.startswith('W:/'):
                return path.replace('W:/', '/mnt/work/')
            else:
                return path
        return path

    def updateProjectCode(self, proj):
        self.project_code = str(proj)
        self.asset_path = self.osPathConvert('/mnt/proj/projects/'+self.project_code+'/asset/')

    def getXMLTree(self, xml=None):
        if not xml:
            if not os.path.isfile(self.xml_file):
                raise Exception(self.xml_file+' is not a valid xml file!')
                return
            self.tree = ET.parse(self.xml_file)
            self.root = self.tree.getroot()
        else:
            if not os.path.isfile(xml):
                raise Exception(xml+' is not a valid xml file!')
                return
            tree = ET.parse(xml)
            root = tree.getroot()
            return [tree, root]

    def getPythonVersion(self):
        return '.'.join( [str(i) for i in sys.version_info] )

    def getIter(self, root, name):
        if self.version.startswith('2.7'):
            return root.iter(name)
        else:
            return root.getiterator(name)

    def getAssemblyRealName(self, name):
        '''
        cut the version or duplicated number tail if any, return the assembly's real name if exists
        '''
        try:
            last_token = name.split('.')[-1]
            if not last_token:
                return None
            if os.path.isdir(self.asset_path+'asb/'+last_token):
                return last_token
            elif last_token[-1].isdigit():
                return self.getAssemblyRealName( last_token[:-1] )
            else:
                return None
        except:
            return None

    def getLatestAssemblyXML(self, name):
        '''
        grab the latest assembly xml of asset if exists
        '''
        asset = self.getAssemblyRealName(name)
        if not asset:
            return None
        publish = self.asset_path+'asb/'+asset+'/mod/publish'

        if os.path.isdir(publish):
            latest = sorted( [d for d in os.listdir(publish) if asset in d] )
            if latest:
                xml = publish+'/'+latest[-1]+'/scene_graph_xml/'+asset+'.xml'
                if os.path.isfile(xml):
                    return xml
        return None

    def compareInstances(self, inst1, inst2):
        '''
        This method return true if the trees in inst1 are included in inst2,
        return false if any instance in inst1 is not presented in inst2
        compareInstances(inst1, inst2)
        the inputs must be a list of instances, not instanceList
        '''
        # inst1 comes from layout, inst2 comes from assembly mod
        grp1 = [ i for i in inst1 if i.tag=='instance' and i.attrib.has_key('type') and i.attrib['type']=='group' ]
        ref1 = [ i for i in inst1 if i.tag=='instance' and i.attrib.has_key('type') and i.attrib['type']=='reference' ]
        grp2 = [ i for i in inst2 if i.tag=='instance' and i.attrib.has_key('type') and i.attrib['type']=='group' ]
        ref2 = [ i for i in inst2 if i.tag=='instance' and i.attrib.has_key('type') and i.attrib['type']=='reference' ]

        # it is possible that some child models of assembly have been unload by layout artist
        if len(grp1) > len(grp2) or len(ref1) > len(ref2):
            return False

        # compare reference one by one
        ref1_name_list = [i.attrib['name'].split('.')[-1] for i in ref1 if i.attrib.has_key('name')]
        ref2_name_list = [i.attrib['name'].split('.')[-1] for i in ref2 if i.attrib.has_key('name')]
        for r in ref1_name_list:
            if r in ref2_name_list:
                continue
            else:
                return False

        # compare group recursively
        grp1_dict = {}
        grp2_dict = {}
        # grab short name and compare
        for g in grp1:
            if g.attrib.has_key('name'):
                grp1_dict[ g.attrib['name'].split('.')[-1] ] = g
        for g in grp2:
            if g.attrib.has_key('name'):
                grp2_dict[ g.attrib['name'].split('.')[-1] ] = g
        for g in grp1_dict.keys():
            if g in grp2_dict.keys():
                continue
            else:
                return False
        # then throw children of group into next recursion
        for g in grp1_dict.keys():
            try:
                # suppose every group only had one child of instanceList
                children1 = grp1_dict[g].find('instanceList').findall('instance')
                children2 = grp2_dict[g].find('instanceList').findall('instance')
            except:
                print 'Something wrong happened when getting child instances of '+str(g)
                return False
            if not self.compareInstances( children1, children2 ):
                return False

        return True

    def removeIsReferenceEditedAttr(self, inst):
        if inst.attrib.has_key('isReferenceEdited'):
            del inst.attrib['isReferenceEdited']
            return True
        return False

    def update(self):
        '''
        iterate over instances and update the transformations of assembly assets, while keep edited content intact
        '''
        for inst in self.getIter(self.root, 'instance'):
            if inst.attrib.has_key('groupType') and inst.attrib['groupType'] == 'assembly':
                # get assembly tree from asb assets to compare
                asb_inst = []
                # get asb group instance under assembly
                asb_inst.append( inst.find('instanceList').findall('instance') )
                asb_xml = self.getLatestAssemblyXML( inst.attrib['name'] )
                if self.verbose == 1:
                    print 'asb mod path: '+asb_xml
                if asb_xml:
                    try:
                        root = self.getXMLTree( asb_xml )
                    except:
                        print 'failed to read asb xml'
                        continue
                    # we start compare from asb group
                    asb_mod_root = root[1].find('instanceList').find('instance')
                    asb_inst.append( root[1].find('instanceList').find('instance').find('instanceList').findall('instance') )
                    if self.verbose == 1:
                        print 'Compare level at:'
                        print '>layout xml:  '+' '.join( [p.attrib['name'] for p in asb_inst[0]] )
                        print '>asb mod xml:  '+' '.join( [p.attrib['name'] for p in asb_inst[1]] )
                    if self.compareInstances( asb_inst[0], asb_inst[1] ):
                        # start to update xform
                        # any xform of instance without isReferenceEdited attribute in layout xml will be replaced by the one with same name in assembly xml
                        # collect all info before update
                        asb_lay_collect = {}
                        asb_mod_collect = {}
                        # map name to instance and xform
                        for i in self.getIter(asb_inst[0][0], 'instance'):
                            if i.attrib.has_key('type') and i.attrib['type']=='reference':
                                name = i.attrib['name'].split('.')[-1]
                                xform = i.find('xform')
                                asb_lay_collect[ name ] = [i, xform, xform.attrib['value']]
                        for i in self.getIter(asb_inst[1][0], 'instance'):
                            if i.attrib.has_key('type') and i.attrib['type']=='reference':
                                name = i.attrib['name'].split('.')[-1]
                                xform = i.find('xform')
                                asb_mod_collect[ name ] = [i, xform, xform.attrib['value']]
                        if self.verbose == 1:
                            print asb_lay_collect, asb_mod_collect
                        # update
                        for i in asb_lay_collect.keys():
                            if not self.removeIsReferenceEditedAttr( asb_lay_collect[i][0] ):
                                if i in asb_mod_collect.keys():
                                    asb_lay_collect[i][1].attrib['value'] = asb_mod_collect[i][2]
                        # update assembly root at last
                        if self.verbose == 1:
                            print 'Compare assembly root: '+inst.attrib['name']+' '+asb_mod_root.attrib['name']
                        if not self.removeIsReferenceEditedAttr( inst ):
                            inst.find('xform').attrib['value'] = asb_mod_root.find('xform').attrib['value']
                    else:
                        print inst.attrib['name']+' has different version with assembly model, ignored.'
                else:
                    print 'Unable to find asb mod at',self.getAssemblyRealName(inst.attrib['name']),',ignored'

                self.addIsAsbAttr(inst)
            # get rid of isReferenceEdited attribute
            self.removeIsReferenceEditedAttr(inst)
        print 'layout xml tree has been updated'
        return self.tree

    def addIsAsbAttr(self, asb_inst):
        try:
            for i in self.getIter(asb_inst, 'instance'):
                if i.attrib.has_key('type') and i.attrib['type'] == 'reference':
                    i.set('isAsb', 'yes')
        except:
            pass

    def write(self, xml):
        xml_file = self.osPathConvert(xml)
        self.tree.write( xml_file )
        print 'layout xml tree has been written out at '+xml_file

    def updateAndWrite(self, xml):
        self.update()
        self.write(xml)

    def doNothing(self):
        '''
        import xml.etree.ElementTree as ET
        tree1 = ET.parse('/media/KINGSTON/lc/scenes_layout2.xml')
        tree2 = ET.parse('/media/KINGSTON/lc/wonton_shop_inside.xml')
        root1 = tree1.getroot()
        root2 = tree2.getroot()
        for inst in root1.getiterator('instance'):
            if inst.attrib.has_key('groupType') and inst.attrib['groupType'] == 'assembly':
                asb_lay = inst
                break
        for inst in root2.getiterator('instance'):
            if inst.attrib.has_key('groupType') and inst.attrib['groupType'] == 'assembly':
                asb_mod = inst
                break

        compareInstances(asb_lay.findall('instanceList')[0].findall('instance'), asb_mod.findall('instanceList')[0].findall('instance'))
        '''
        pass