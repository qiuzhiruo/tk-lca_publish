# -*- coding:utf-8 -*-

import os
import traceback
import shutil
import pymel.core as pm


import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )

import assembly_operator as asop
import sgXml_parser as sgxml
#import convertHi2Lo as hi2lo

# sys.path.append('U:/toolset/tools/gene/scene_operator')
# sys.path.append('/mnt/utility/toolset/tools/gene/scene_operator')
import gene.scene_operator.sceneOperator as scnOp
reload(scnOp)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将文件拷贝到服务器"
        self.description = u"将文件拷贝到服务器"
        return

    def proceed(self):
        try:
            self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
            l_attrs = pm.listAttr("|master")
            if not 'rraVersion' in l_attrs:
                pm.addAttr("|master", shortName='rrav', longName='rraVersion', dt="string")
            if not 'rraPath' in l_attrs:
                pm.addAttr("|master", shortName='rrap', longName='rraPath', dt="string")

            pm.setAttr( "|master.rraVersion", self.dialog.version_name[-3:], type="string" )
            pm.setAttr( "|master.rraPath", self.dialog.tank_file, type="string" )
            error_export = False
            try:
                # pm.select('|master|rra', replace=True)
                # pm.select('|master|rig', add=True)
                pm.select('|master')
                pm.exportSelected( self.dialog.tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)

                pm.select('|master')
                pm.exportSelected( self.dialog.tank_file, force=True, options="v=0;", type="mayaBinary", pr=True, es=True)

            except:
                error_export = True
            pm.select(cl=True)

            if error_export:
                return u"Failed to export .ma! Check the |master|rra name"
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


