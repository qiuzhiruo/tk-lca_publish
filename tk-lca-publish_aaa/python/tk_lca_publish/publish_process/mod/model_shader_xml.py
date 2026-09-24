# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: wangbin
#
# Date: 2015.12
#
# Description:
#
############################################

import os
import re
import traceback
import json
import maya.cmds as cmds
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import production.pipeline.lcProdProj as lcp
import logging
from proc.function_running_time import record_time


# All publish process will use StdProcess as the class name.

class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"模型材质信息导出"
        self.description = u"把模型的简单材质信息导出，存到srf的v00版中"
        return

    def WriteData(self, Path, Data):
        try:
            f = open(Path, "w")
            DataStr = json.dumps(Data)
            f.write(DataStr)
            f.close()
            try:
                os.chmod(Path, 0777)
            except:
                pass
            return True
        except Exception, e:
            logger = logging.getLogger(__name__)
            logger.debug("path %s , data %s  erroir %s" % (Path, str(Data), str(e)))
            print e
            return None

    # def ReadData(self, Path):
    #     f = open(Path, "r")
    #     DataStr = f.read()
    #     Data = json.loads(DataStr)
    #     f.close()
    #     return Data

    def Write_marker(self, xml_path, proj_name):
        data = {}

        evenFloder_linux = "/mnt/proj/trash/mod_writeshader_xml_event"
        evenFloder_win = "Z:/trash/mod_writeshader_xml_event"
        if os.path.exists(evenFloder_linux):
            evenFloder = evenFloder_linux
        else:
            evenFloder = evenFloder_win
        # xml_path="/mnt/work/home/wangbin/Wb2015/CodeWork/modxml/p/cintiq_b.srf.surfacing.v000/mod_mat_info/cintiq_b.xml"
        Asse_name = os.path.splitext(os.path.basename(xml_path))[0]
        xml_path = os.path.normpath(xml_path).replace("\\", "/")
        # ProR=r".*/projects/(\w{3})/asset/.*"
        # proj_name=re.findall(ProR,xml_path)[0]
        data["xml_path"] = xml_path
        even_path = os.path.join(evenFloder, proj_name + "." + Asse_name + ".info").replace("\\", "/")
        self.set_log(evenFloder)
        self.WriteData(even_path, data)
        logger = logging.getLogger(__name__)
        logger.debug("%s write ok to %s" % (proj_name + "." + Asse_name + ".info", even_path))

    def set_log(self, FILE):
        logger = logging.getLogger(__name__)
        hdlr = logging.FileHandler(os.path.join(FILE, 'log.log'))
        try:
            os.chmod(os.path.join(FILE, 'log.log'), 0777)
        except Exception, e:
            print e

        formatter = logging.Formatter('%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)

    @record_time(__file__)
    def proceed(self):
        try:
            asset = self.dialog.entity['name'].lower()
            proj = self.dialog.project['name'].lower()
            version_dir = self.dialog.d_assets_info[asset]['version_dir'].lower()
            allshader_InfoData = self.Get_all_shader_info()
            # assetName="bird"
            # modVersion="v001"
            # proj="tst"
            R = r".*/.*\.mod\.(model\.v\d*$)"
            p = re.compile(R)
            p_finder = p.findall(version_dir)
            if not p_finder: return ''

            modVersion = p_finder[0]
            self.localP = lcp.lcProdProj()
            self.localP.setProj(proj)
            # Klf_path=localP.getSrfAsset(asset)["klf"]
            # if not Klf_path or "srf.surfacing.v000" in Klf_path:
            if not self.dialog.has_srf:
                Xml_path = self.Get_xml_path(asset)
                self.WriteLibData(Xml_path, allshader_InfoData, asset, modVersion)
                self.dialog.print_log(u"模型材质xml 写出到 %s 完成" % (Xml_path))
                try:
                    self.Write_marker(Xml_path, proj)
                except Exception, e:
                    self.dialog.print_log(str(e))
                return ""
            else:
                self.dialog.print_log(u"不需要写出xml")
                return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

    def Get_all_shader_info(self):
        '''
        maya  得到材质信息 e.g  {u'lambert5': {'shapeList': [u'|master|poly|hi|cloth|clothShape'], 'material_value': (0.7647058963775635, 0.2099192589521408, 0.5467749238014221)}, u'lambert4': {'shapeList': [u'|master|poly|hi|hand|handShape'], 'material_value': (0.34134799242019653, 0.2029988318681717, 0.8627451062202454)}, u'lambert3': {'shapeList': [u'|master|poly|hi|cap|capShape'], 'material_value': (0.6028450131416321, 0.9607843160629272, 0.7509934306144714)}, u'lambert2': {'shapeList': [u'|master|poly|hi|head_grp|head_geo|head_geoShape'], 'material_value': (0.7254902124404907, 0.3271818459033966, 0.3271818459033966)}}
        '''
        all_shader_info = {}
        Allmaterials = cmds.ls(mat=True)
        All_as_shape = []
        for Allmaterial in Allmaterials:
            shaderLibInfo = {}
            if cmds.objExists(Allmaterial + ".color"):
                try:
                    AllmaterialValue = cmds.getAttr(Allmaterial + ".color")
                except:
                    # for ramp shader:
                    AllmaterialValue = cmds.getAttr(Allmaterial + ".color[0].color_Color")
                if not AllmaterialValue: AllmaterialValue = [()]
                ShapeList = []
                if not Allmaterial:
                    continue
                shadingEngine = cmds.listConnections(Allmaterial + ".outColor", s=False, d=True)
                if not shadingEngine:
                    continue
                for shadingEngineItem in shadingEngine:
                    ShapNameList = cmds.listConnections(shadingEngineItem, s=True, d=False, t="mesh")
                    if not ShapNameList:
                        continue
                    for ShapNameListItem in ShapNameList:
                        fullPathname = cmds.listRelatives(ShapNameListItem, f=True)
                        if fullPathname and re.findall("\|master\|poly\|(hi|md|lo)\|.*", fullPathname[0]) and fullPathname[
                            0] not in ShapeList and fullPathname[0] not in All_as_shape:
                            All_as_shape.append(fullPathname[0])
                            ShapeList.append(fullPathname[0])
                if ShapeList:
                    # shaderLibInfo["material_name"]=Allmaterial
                    shaderLibInfo["material_value"] = AllmaterialValue[0]
                    shaderLibInfo["shapeList"] = ShapeList
                if shaderLibInfo:
                    all_shader_info[Allmaterial] = shaderLibInfo
        return all_shader_info

    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        return

    def WriteLibData(self, path, allshader_InfoData, assetName, modVersion):
        root = Element('MaterialInfoXML0', {"assetName": assetName, "modVersion": modVersion})
        tree = ET.ElementTree(root)
        for key in allshader_InfoData.keys():
            shader_value = allshader_InfoData[key]["material_value"]
            Geo_path_list = allshader_InfoData[key]["shapeList"]
            shader = Element('shader', {"name": key})
            root.append(shader)
            if shader_value:
                rgb = ET.Element('rgb')
                difco = ET.Element('difCo', {"value": str(shader_value)[1:-1]})
                rgb.append(difco)
                shader.append(rgb)
            if Geo_path_list:
                geo = ET.Element('geoPath')
                for Geo_path_listitem in Geo_path_list:
                    celPathgeo = ET.Element('shape', {'path': Geo_path_listitem})
                    geo.append(celPathgeo)
                shader.append(geo)
        self.indent(root)
        tree.write(path, 'UTF-8')
        try:
            os.chmod(path, 0777)
        except Exception, e:
            print e
        return True

    def Get_xml_path(self, assetName):
        # path="/mnt/proj/projects/tpr/asset/chr/accounting/srf/publish/accounting.srf.surfacing.v012/mod_mat_info/accounting.xml"
        Xml_path = os.path.join(self.localP.getAssetFolder(assetName, 'srf'), '%s.srf.surfacing.v000' % assetName,
                                'mod_mat_info', '%s.xml' % assetName)
        # Xml_path="%s/%s.srf.surfacing.v000/mod_mat_info/%s.xml"%(self.localP.getAssetFolder(assetName,'srf'),assetName,assetName)
        try:
            os.makedirs(os.path.dirname(Xml_path))
            os.chmod(os.path.dirname(Xml_path), 0775)
        except Exception, e:
            pass
        return Xml_path
