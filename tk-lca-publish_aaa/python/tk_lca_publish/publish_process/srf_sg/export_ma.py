import maya.cmds as mc
import sys
import traceback
import os
import maya.standalone as std

def export(in_file,out_file):
    if not os.path.isfile(in_file) or not in_file.endswith('.ma'):
        print 'Srf export Error: ',in_file ,'is not a maya ma file'

    try:
        mc.file(in_file,f=True,options="v=0;",ignoreVersion=True, typ= "mayaAscii", o= True)
    except:
        print 'Srf export Error: ',traceback.format_exc()

    master_root=mc.ls('master')
    if not master_root:
        print 'Srf export Error: Cannot find master root location.'
        return
    
    mc.select(master_root[0],r=True)
    mc.file(out_file,force=True,options='v=0',typ='mayaAscii',es=True)
    return True
    
std.initialize('python')
export(sys.argv[-2],sys.argv[-1])
os._exit(0)
