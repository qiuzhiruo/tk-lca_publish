# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil
import pymel.core as pm

import sys
toolset = os.getenv('LC_TOOLSET')
# sys.path.append('/mnt/utility/toolset/tools/gene/scene_operator')
# sys.path.append('U:/toolset/tools/gene/scene_operator')
sys.path.append('%s/tools/gene/scene_operator' % toolset)
import sceneOperator as scnOp
reload(scnOp)

# sys.path.append('/mnt/utility/toolset/lib/pipeline')
# sys.path.append('U:/toolset/tools/lib/pipeline')
import production.pipeline.mayaReferenceUtils as mru
reload(mru)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"解锁assets，后续的xml步骤需要给物体tag"
        self.description = u"解锁assets，后续的xml步骤需要给物体tag"
        return

    def proceed(self):
        try:
            topNode = None
            if '/asset/' in pm.sceneName().replace('\\', '/').lower():
                topNode = '|master'
            elif '/shot/' in pm.sceneName().replace('\\', '/').lower():
                topNode = '|assets'
            masters = mru.MayaReferenceUtils().listMasters(top=topNode)
            scnOp.AssetsActivator().activateAsset( masters )

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


