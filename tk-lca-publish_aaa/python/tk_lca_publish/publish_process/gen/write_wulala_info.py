# -*- coding:utf-8 -*-
import subprocess
import traceback
import sys
import os
import shutil
import ConfigParser
import random
import glob
import getpass
import datetime

def write_wulala_config(path,args):
    cf=ConfigParser.ConfigParser()
    cf.add_section('wulala')

    for k,v in args.items():
        cf.set('wulala',k,v)
    
    cf.write(open(path,'w'))
    os.chmod(path, 0777)

def write_info(proj,asset,step='mod'):
    result={'user':getpass.getuser(),
            'proj':proj,
            'asset':asset,
            'step':step,
            'date':datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")}
    if sys.platform=='linux2':    
        write_wulala_config('/mnt/proj/trash/asset_match/publish_info/'+proj+'.'+asset+'.config', result)
    elif sys.platform=='win32':
        write_wulala_config('Z:/trash/asset_match/publish_info/'+proj+'.'+asset+'.config', result)

# write_info('god','xiaoying')

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = "Render Asset"
        self.description = "Wulala farm render asset"
        return

    def proceed(self):
        try:
            ast_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
            if ast_info['sg_asset_type'] in ['efx','scn','asb']:
                return ''

            asset = self.dialog.entity['name']
            proj = self.dialog.project['name']
            step = self.dialog.step['name']
            
            # if step=='srf':
            #     step='mod'

            write_info(proj.lower(), asset,step=step)
        except:
            self.dialog.print_error(traceback.format_exc())

        return ''

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description