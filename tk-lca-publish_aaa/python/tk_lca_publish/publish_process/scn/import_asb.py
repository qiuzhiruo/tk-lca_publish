# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import sys

import pymel.core as pm

# sys.path.append('U:/toolset/lib/production/pipeline')
# sys.path.append('/mnt/utility/toolset/lib/production/pipeline')

import production.pipeline.mayaReferenceUtils as mru
reload(mru)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"import asb"
        self.description = u"import asb: 将非reference组摘出， 然后import asb，再放回去"
        return


    def proceed(self):
        try:
            if not pm.objExists('|master'):
                return u"找不到|master组，无法import asb资产"

            # record reference path and version, used by relink step later
            try:
                version_path = pm.PyNode('|master').attr('asbPath').get()
                path = os.path.dirname( pm.sceneName() ).replace('\\', '/')
                f = open( os.path.join(path, os.path.basename(pm.sceneName())[:-3]+'.asb_version.txt'), 'w' )
                f.write( version_path )
                f.close()
            except:
                pass

            mref = mru.MayaReferenceUtils()
            groups = mref.getNonReferenceNode('master', recursive=False)
            groups_parents = {}
            for g in groups:
                try:
                    groups_parents[g] = g.getParent().name()
                except:
                    pass

            # unparent non reference group
            for g in groups_parents.iterkeys():
                try:
                    pm.parent(g, world=True)
                except:
                    pass

            # import asb
            ref_file = pm.FileReference('|master')
            ref_file.importContents()

            # parent non reference back to group
            for g in groups_parents.iterkeys():
                try:
                    pm.parent(g, groups_parents[g])
                except:
                    pass

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


