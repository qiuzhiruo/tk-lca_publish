# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os, shutil
import traceback
import production.CacheUtils.CacheUtils as cu
import production.CacheUtils.XmlYeti as XY
from pymel.core import *
import xml.dom.minidom as dom
import h5py
import maya.cmds as mc
import pymel.core as pm
from production.AbcExportOption import abcExportOption


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出 Yeti 毛发 Fur 和 xml 文件"
        self.description = u"输出 Yeti 毛发 Fur Cache 供 srf 组使用。"
        return

    def Write_gen_fur_info(self):
        import sys
        # lctools_env=os.getenv('LCTOOLSET','/mnt/utility/toolset')
        #lctools_env="/mnt/work/home/wangbin/git_repo/lcatools"
        # sys.path.append(lctools_env+'/lib/production')
        import production.write_trash_cfx_rig as write_trash_cfx_rig
        reload(write_trash_cfx_rig)
        import production.write_trash_cfx_rig.writetrash as ww
        asset_name=self.dialog.entity['name']
        project=self.dialog.project['name']
        ww.write_asseet_for_gen_fur(project,asset_name)

    def proceed(self):
        try:
            # put listRelatives into try block to avoid no plugin satuation
            # TODO: use import to identify
            loadPlugin('mtoa', quiet=True)
            loadPlugin('AbcExport', quiet=True)
            if not ls(typ='pgYetiMaya'):
                return ''

            for shape in ls(typ='pgYetiMaya'):
                part = shape.getParent()
                cacheFileName=""
                currentTime( 1, edit=True )
                current_frame = currentTime(q=1)

                cacheFileName = cu.feedYetiCache(self.dialog.version_dir, part)
                print '  Yeti Fur:', cacheFileName
                shape.fileMode.set(0)

                select(part, r=1)
                sampleTimeResult = '0.000000'
                try:
                    f=h5py.File(cacheFileName,'r')
                    dset = f['/geo/yeti_variables_internal/F/sample_times']
                    sampleTime= dset[...]
                    sampleTimeResult=' '.join(map(lambda n: '%f'%n, sampleTime))
                    f.close()
                except:
                    pass
                doc = dom.Document()
                root_node = doc.createElement('data')
                root_node.setAttribute('frame', str(current_frame))
                root_node.setAttribute('mb_samples', '3')
                root_node.setAttribute('mb_len', '0.5')
                root_node.setAttribute('sample_times', sampleTimeResult)
                doc.appendChild(root_node)

                part.displayOutput.set(1)
                bbx=part.getBoundingBox()
                # boundingbox

                bbox_element = doc.createElement('boundingbox')
                bbox_value = doc.createTextNode('%f %f %f %f %f %f' % tuple(itertools.chain.from_iterable(bbx)))
                bbox_element.appendChild(bbox_value)
                root_node.appendChild(bbox_element)

                partname = part.nodeName()
                xmlPath=self.dialog.version_dir +'/hair/'+partname+'/'
                if os.path.isdir(xmlPath):
                    shutil.rmtree(xmlPath)
                os.makedirs(xmlPath)
                path = xmlPath+partname+'.xml'
                #metadata
                XY.exportMetaData(part, path)
                print '  Yeti Hair:', path

                # frame xml
                fur_xml_frame_path=XY.insertFrame(path,current_frame)
                f = open(fur_xml_frame_path, 'w')
                f.write(doc.toprettyxml(encoding='utf-8'))
                f.close()

            cv_list = []
            for yeti_nd_name in mc.ls(type='pgYetiMaya'):
                yeti_nd = pm.PyNode(yeti_nd_name)
                guides_sets = pm.getAttr(yeti_nd.guideSets)
                for guides_set in guides_sets:
                    cvs = mc.sets(str(guides_set), q=1)
                    for cv in cvs:
                        cv_shape = mc.listRelatives(cv, c=1, type='nurbsCurve', fullPath=1)[0]
                        cv_trans = mc.listRelatives(cv_shape, p=1, type='transform', fullPath=1)[0]
                        cv_grp = mc.listRelatives(cv_trans, p=1, type='transform', fullPath=1)[0]
                        if cv_grp not in cv_list: cv_list.append(cv_grp)
                        if not mc.objExists(cv_shape + '.yetiDescription'):
                            mc.addAttr(cv_shape, ln='yetiDescription', dataType='string')
                            atr_value = yeti_nd_name + '/' + guides_set
                            mc.setAttr(cv_shape + '.yetiDescription', atr_value, type='string')
            roots = ''
            for i in cv_list:
                roots += ' -root {}'.format(i)
            abc_path = os.path.join(self.dialog.version_dir, 'fur/', 'guides.abc')
            abc_cmds = '-stripNamespaces -worldSpace -dataFormat ogawa -attr yetiDescription -uvWrite  -frameRange 1 1 {} -file {}'.format(
                roots, abc_path)
            mc.AbcExport(j=abc_cmds)

            try:
                self.Write_gen_fur_info()
            except Exception, e:
                print e        

            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
