# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import sys
import traceback

filename = sys.argv[1]

import maya.standalone
maya.standalone.initialize( name='python' )

# utils_path = ''
# if os.name == 'nt':
#     utils_path = 'U:/'
# else:
#     utils_path = '/mnt/utility/'
lca_app_path = os.getenv('LC_APP_PATH')
sys.path.append('%s/maya/scripts' % lca_app_path)
import userSetup

import update_scn_maya
reload(update_scn_maya)

try:
    print 'Updating scn: ' + filename + '\n'

    try:
        err = update_scn_maya.main( filename )
    except:
        print traceback.format_exc()

    if err:
        print err, '\nXXXX Error:\nFailed to update scn: ' + '\n'
    else:
        print 'Updated successfully!\n'
except:
    print traceback.format_exc()

os._exit(0)

'''
windows:
"C:\Program Files\Autodesk\Maya2013\bin\mayapy" update_scn_cmd.py filename >> D:\dailyToDownstreamLog.txt
pause
'''
