import os
import sys

import maya.standalone as std
try:
    std.initialize(name='python')
except:
    pass
import maya.mel as mel
import pymel.core as pm

filename = sys.argv[1]
output_ma = sys.argv[2]
res = sys.argv[3]

mel.eval('file -f -options "v=0;"  -typ "mayaAscii" -o "'+filename+'";')

# Import references
d_ref = pm.getReferences()
for name, ref in d_ref.iteritems():
    try:
        ref.importContents()
    except:
        print 'Failed to import', name

if res == 'lo':
    if pm.objExists('|master|poly|hi'):
        try:
            pm.delete('|master|poly|hi')
        except:
            print 'Error: Can\'t delete |master|poly|hi'
            sys.exit(-2)

    show_lo = True

elif res == 'hi':
    show_lo = False

else:
    print res, 'is not a valid resolution. Skip.'
    sys.exit(-2)


try:
    n = pm.ls('Visibility')[0]
    n.setAttr('hiLoVis', show_lo)
except:
    print 'Warning: Failed to show the low res model.'

pm.select('|master')
pm.exportSelected(output_ma, preserveReferences=True, force=True)

os._exit(0)

