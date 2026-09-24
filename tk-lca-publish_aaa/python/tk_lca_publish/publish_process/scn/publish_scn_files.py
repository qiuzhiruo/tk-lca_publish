# -*- coding:utf-8 -*-

import os
import traceback
import shutil
import pymel.core as pm


import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )

import scn_assemblyOperator as asop
import sgXml_parser as sgxml
#import convertHi2Lo as hi2lo

# sys.path.append('U:/toolset/tools/gene/scene_operator')
# sys.path.append('/mnt/utility/toolset/tools/gene/scene_operator')
toolset = os.getenv('LC_TOOLSET')
sys.path.append('%s/tools/gene/scene_operator' % toolset)

import sceneOperator as scnOp
reload(scnOp)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提取scn资产，将文件拷贝到服务器。"
        self.description = u"将scn套上global_control和intermediate_ctrl控制器，存出.ma文件"
        return

    def proceed(self):
        try:
            
            self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'

            # Add version mark
            l_attrs = pm.listAttr("|master")
            if not 'asbVersion' in l_attrs:
                pm.addAttr("|master", shortName='asbv', longName='asbVersion', dt="string")
            if not 'asbPath' in l_attrs:
                pm.addAttr("|master", shortName='asbp', longName='asbPath', dt="string")

            pm.setAttr( "|master.asbVersion", self.dialog.version_name[-3:], type="string" )
            pm.setAttr( "|master.asbPath", self.dialog.tank_file, type="string" )

            # Add rig
            ctrl = asop.ScnAssemblyOperator()
            if not ctrl.add_ctrl():
                return u"Errors when adding rig and control, check the console!"

            # get all of models' references for shotgun linking
            mod_list = ctrl.listModReferences()

            # lock assets
            assetLock = scnOp.AssetsActivator2()
            assetLock.deactivateAssets(mod_list)

            # catch errors by variables and deal with them after deleting rig, as we don't want to left scraps if any failure of publish
            error_export = False
            #error_sync = False
            try:
                # select and export
                pm.select('|master|asb', replace=True)
                pm.select('|master|rig', add=True)
                pm.exportSelected( self.dialog.tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
            except:
                error_export = True

            # delete rig
            ctrl.delete_ctrl()
            pm.select(cl=True)

            if error_export:
                return u"Failed to export .ma! Check the |master|asb name"
            #if error_sync:
            #    return u"Failed to sync latest version! Any network or permission issues? Try it again later."

            # shotgun linking stuff
            try:
                # filter out duplicated asset first
                mod_list = list(set(mod_list))
                #get the scene name
                asb_name = os.path.basename( pm.sceneName() ).split('.')[0]
                asbinfo = self.dialog.sg.find_one('Asset', [['code', 'is', asb_name]], [])
                assetinfo = []
                if asbinfo:
                    for tmp in mod_list:
                        asset_name = os.path.basename(pm.referenceQuery(tmp,  filename=True, wcn=True))[:-3]
                        assetid = self.dialog.sg.find_one('Asset', [['code', 'is', asset_name]], [])
                        if assetid:
                            assetinfo.append( assetid )
                        else:
                            print ('==> unable find asset on shotgun: '+tmp)
                    self.dialog.sg.update('Asset', asbinfo['id'], {'assets':assetinfo})
                else:
                    print ('==> unable find shot code on shotgun: '+asb_name)
            except:
                pass

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


