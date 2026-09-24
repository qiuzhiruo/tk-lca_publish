# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.02
#
# Description: As the description shows below
#
############################################

import traceback
import datetime
import os, sys, shutil
import maya.cmds as cmds
try:
    import xgenm as xg
    import xgenm.xgGlobal as xgg
except:
    pass

    
# All system check classes will use StdCheck as the class name.
# ${PROJECT}xgen/beard_a_collection
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查xgen file path"
        self.description = u"检查xgen collection xgDataPath 是否在在标准路径/xgen/collections下, 如果不在, 可以自动修复把相应文件夹copy到标准路径下"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                return ''

            task = self.dialog.task['name'].lower()

            xgprojPath = cmds.workspace( q=True, rd=True ).rstrip('/')
            bad_str = ''
            for palette in cmds.ls(type='xgmPalette'):
                if '${PROJECT}xgen' not in xg.getAttr('xgDataPath', str(palette)):
                    bad_str += u'xgen的filepath不包含${PROJECT}字样或写成了${PROJECT}/xgen，请检查或使用自动修复.\n'
                currentxgDataPath = xg.getAttr( 'xgDataPath', str(palette) ).replace('${PROJECT}', xgprojPath+'/')
                if currentxgDataPath != '%s/xgen/collections/%s' % (xgprojPath, str(palette)) and \
                        currentxgDataPath != '%s/%s/xgen/collections/%s' % (xgprojPath, task, str(palette)):

                    bad_str += u'\n以下collection路径不在标准路径%s下，请自行修改或使用自动修复.\n' % xgprojPath
                    bad_str += palette+':'+currentxgDataPath+'\n'

            return bad_str

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for palette in cmds.ls(type='xgmPalette'):
                xg_dataPath = xg.getAttr('xgDataPath', str(palette))
                if '${PROJECT}' not in xg_dataPath and '/mnt/work/project' in xg_dataPath:
                    new_dataPath = xg_dataPath.replace(xg_dataPath.split('xgen/collections/')[0], '${PROJECT}')
                    xg.setAttr('xgDataPath', str(new_dataPath), str(palette))
                if '${PROJECT}/xgen' in xg_dataPath:
                    new_dataPath = xg_dataPath.replace('${PROJECT}/xgen', '${PROJECT}xgen')
                    xg.setAttr('xgDataPath', str(new_dataPath), str(palette))
                # currentxgDataPath = xg.getAttr( 'xgDataPath', str(palette) ).replace('${PROJECT}', xgprojPath+'/')
                # gen_xgDataPath = xgprojPath+'/xgen/collections/'+str(palette)
                #
                # if currentxgDataPath != gen_xgDataPath:
                #     if os.path.exists(gen_xgDataPath):
                #         submit_time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
                #         if not os.path.isdir(xgprojPath+'/xgen/collections/backup'):
                #             os.makedirs(xgprojPath+'/xgen/collections/backup')
                #         os.rename(gen_xgDataPath, gen_xgDataPath+'.'+submit_time_stamp)
                #         shutil.move(gen_xgDataPath+'.'+submit_time_stamp, xgprojPath+'/xgen/collections/backup')
                #     shutil.copytree(currentxgDataPath, gen_xgDataPath)
                #     new_xgDataPath = gen_xgDataPath.replace(xgprojPath+'/', '${PROJECT}')
                #     xg.setAttr('xgDataPath', str(new_xgDataPath), str(palette))
                    
            return ''
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



