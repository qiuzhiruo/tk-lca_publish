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
        self.process_name = u"提取组装资产，将文件拷贝到服务器。"
        self.description = u"将组装套上global_control和intermediate_ctrl控制器，冻结资产，存出.ma文件"
        return

    def proceed(self):
        try:
            #we didn't touch file without version any more
            #try:
            #    if os.path.isdir(self.dialog.version_dir[:-5]):
            #        shutil.rmtree(self.dialog.version_dir[:-5])
            #except:
            #    return 'Failed to delete folder '+self.dialog.version_dir[:-5]+'!'
            
            self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
            self.dialog.proxy_file = ''
            # Add version mark
            l_attrs = pm.listAttr("|master")
            if not 'asbVersion' in l_attrs:
                pm.addAttr("|master", shortName='asbv', longName='asbVersion', dt="string")
            if not 'asbPath' in l_attrs:
                pm.addAttr("|master", shortName='asbp', longName='asbPath', dt="string")

            pm.setAttr( "|master.asbVersion", self.dialog.version_name[-3:], type="string" )
            pm.setAttr( "|master.asbPath", self.dialog.tank_file, type="string" )

            # Add rig
            #ctrl = asop.AssemblyOperator()
            #if not ctrl.add_ctrl():
            #    return u"Errors when adding rig and control, check the console!"

            # get all of models' references for shotgun linking
            #mod_list = ctrl.listModReferences()

            # lock assets
            #assetLock = scnOp.AssetsActivator2()
            #assetLock.deactivateAssets(mod_list)

            # catch errors by variables and deal with them after deleting rig, as we don't want to left scraps if any failure of publish
            error_export = False
            #error_sync = False
            try:
                # select and export
                pm.select('|master|asb', replace=True)
                #pm.select('|master|rig', add=True)
                pm.exportSelected( self.dialog.tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)

                if pm.objExists('|master|proxy'):
                    print "have proxy ......."
                    # set v 1
                    shapes = pm.ls('|master|proxy', dag=True)
                    for shape in shapes:
                        shape.v.setLocked(False)
                        shape.v.set(1)
                    self.dialog.proxy_file = self.dialog.version_dir + '/' + '{}_proxy.ma'.format(self.dialog.entity['name'])
                    pm.select('|master|proxy', replace=True)
                    pm.exportSelected(self.dialog.proxy_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
            except:
                error_export = True

            #try:
            #    # Sync the latest version
            #    #shutil.copytree(self.dialog.version_dir, self.dialog.version_dir[:-5])
            #    os.makedirs(self.dialog.version_dir[:-5], mode=0777)
            #    l_files = os.listdir(self.dialog.version_dir)
            #    for file in l_files:
            #        if os.path.isfile(self.dialog.version_dir + '/' + file):
            #            shutil.copyfile(self.dialog.version_dir + '/' + file, self.dialog.version_dir[:-5] + '/' + file)
            #        else:
            #            shutil.copytree(self.dialog.version_dir + '/' + file, self.dialog.version_dir[:-5] + '/' + file)
            #except:
            #    error_sync = True

            # delete rig
            #ctrl.delete_ctrl()
            pm.select(cl=True)

            if error_export:
                return u"Failed to export .ma! Check the |master|asb name"
            #if error_sync:
            #    return u"Failed to sync latest version! Any network or permission issues? Try it again later."

            # build low resolution file
            '''
            # we don't need low resolution asb any more, asb publish file should be pointed to low resolution elements.
            try:
                if not os.access(self.dialog.version_dir[:-5], os.W_OK):
                    return u"Writing permission denied by system when built low resolution asb file!"
                hi2lo.ConvertHi2Lo(self.dialog.version_dir+'/'+self.dialog.entity['name'] + '.ma', self.dialog.version_dir+'/res_lo/'+self.dialog.entity['name'] + '.ma').convert()
                os.makedirs(self.dialog.version_dir[:-5]+'/res_lo', mode=0777)
                shutil.copyfile(self.dialog.version_dir+'/res_lo/'+self.dialog.entity['name'] + '.ma', self.dialog.version_dir[:-5]+'/res_lo/'+self.dialog.entity['name'] + '.ma')
            except:
                return u"Failed to build low resolution asb file!"
            '''

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


