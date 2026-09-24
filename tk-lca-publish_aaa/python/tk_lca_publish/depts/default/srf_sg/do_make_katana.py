__author__ = 'yingjie'

import sys
import glob
import os
from Katana import KatanaFile
from Katana import NodegraphAPI

def make_katana():
    if len(sys.argv)>=3:
        xml_folder=sys.argv[-2]
        xml_file=glob.glob(xml_folder+'/*.xml')

        if xml_file:
            KatanaFile.Load(sys.argv[-1])

            asset_name=os.path.basename(xml_file[0]).split('.')[0]
            katana_file=os.path.dirname(xml_folder)+'/'+asset_name+'.srf.v000.katana'
            NodegraphAPI.GetNode('asset_in').getParameter('asset').setValue(xml_file[0],0)
            NodegraphAPI.GetNode('asset_in').getParameter('name').setValue('/root/world/assets/'+asset_name,0)
            root_location_param = NodegraphAPI.GetNode('LookFileBake').getParameter('rootLocations')
            root_location_param.getChildByIndex(0).setValue('/root/world/assets/'+asset_name+'/master',0)

            KatanaFile.Save(katana_file)
            try:
                os.chmod(katana_file,0775)
            except:
                pass

make_katana()