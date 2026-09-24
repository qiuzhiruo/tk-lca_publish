# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os
import traceback
import shutil
import re

import sys
import production.pipeline.utils as pplu


def rsync_files(source,destination):
    if not source.endswith('/'):
        source+='/'

    os.system('rsync -az \"'+source+'\" \"'+destination+'\"')

def set_output_format():
    """
        setup the global output settings.
    """
    cmds = '''
        source setMayaSoftwareFrameExt.mel;
        setMayaSoftwareFrameExt(3,0);
        setAttr "defaultRenderGlobals.extensionPadding" 4;
    '''
    try:
        mm.eval(cmds)
    except:
        pass


def get_component_name(f):
    extension= f.split('.')[-1]
    
    comp_name=''

    if extension in ['abc','vdb','nk','exr','tif']:
        file_name=os.path.basename(f).split('-')[0]
        folder=os.path.dirname(f)
        file_name_sp=file_name.split('.')

        if len(file_name_sp)>3:
            comp_name=file_name_sp[1]
        else:
            comp_name=file_name_sp[0]
            if re.match('[a-z]\d{5}$',comp_name):
                comp_name=file_name_sp[1]

        name_sp=file_name.split('.')

        if 'efx' in name_sp:
            comp_name=name_sp[name_sp.index('efx')+1]

        if file_name.endswith('.exr') and not folder.endswith('/L') and not folder.endswith('/R'):
            return ('Error : Exr sequence need to be in /L or /R folder')

        if extension =='abc' and folder.endswith('/'+extension):
            comp_name = folder.split('/')[-2].split('.')[0]
        
        if extension =='exr' and (folder.endswith('/L') or folder.endswith('/R')):
            comp_name = folder.split('/')[-2].split('.')[0]

    if not comp_name:
        return ('Error Cannot find component name for file '+f)
    else:
        return comp_name
        
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"移动EFX资产文件"
        self.description = u"移动所选EFX资产到publish文件夹"

    def proceed(self):
        try:
            # self.dialog.tank_file = None
            old_publish_version_dir = self.dialog.version_dir
            publish_version_dir = old_publish_version_dir.replace('/mnt/proj/', '/efxcache/')

            # change publish mod to 777
            publish_dir = publish_version_dir.split('publish')[0]+'publish'
            if not os.path.isdir(publish_dir):
                try:
                    # There's no function named makedir in os.
                    # By this way we force EFX to use Vactory
                    os.makedir(publish_dir)

                    os.makedirs(publish_dir)
                    os.chmod(publish_dir, 0777)
                except:
                    return u"无法创建文件夹：%s" % publish_dir

            paths = []
            for i in range(self.dialog.w_publish_file.listWidget_cache.count()):
                dir_path = self.dialog.w_publish_file.listWidget_cache.item(i).text()
                paths.append(dir_path)

            for p in paths:

                if 'CompName:' in p:
                    continue

                comp_name = get_component_name(p)

                if 'Error' in comp_name:
                    return comp_name

                extension=p.split('.')[-1]

                if extension in ['abc','nk']:   # none sequence file
                    new_abc_folder = os.path.join(publish_version_dir,comp_name,extension)
                    try:
                        os.makedirs(new_abc_folder)
                    except:
                        pass
                        
                    # if the file is abc file and it's already in one publish version folder
                    # we will make symlink instead of copy
                    if extension == 'abc' and '/publish/' in p:
                        path = new_abc_folder+'/'+os.path.basename(p)
                        if os.path.isfile(path):
                            os.remove(path)
                        os.symlink(p, path)
                    else:
                        shutil.move(p, new_abc_folder)
                    
                elif extension in ['exr', 'vdb']:#sequence files
                    if extension == 'exr':
                        if p.split('/')[-2]=='L' or p.split('/')[-2]=='R':
                            new_comp_folder=os.path.join(publish_version_dir,comp_name,p.split('/')[-2])
                        else:
                            new_comp_folder=os.path.join(publish_version_dir,comp_name,extension)
                    else:
                        new_comp_folder=os.path.join(publish_version_dir,comp_name,extension)
                    


                    file_name=os.path.basename(p)

                    if '/publish/' not in p:
                        try:
                            os.makedirs(os.path.dirname(new_comp_folder))
                        except:
                            pass

                        if '-' in file_name:
                            shutil.move(os.path.dirname(p), os.path.dirname(new_comp_folder))
                        else:
                            shutil.move(p, new_comp_folder)
                    else:
                        try:
                            os.makedirs(new_comp_folder)
                        except:
                            pass

                        if '-' in file_name:
                            seq_f=pplu.findFiles(os.path.dirname(p),'.'+extension)

                            for f in seq_f:
                                os.symlink(f, new_comp_folder+'/'+os.path.basename(f))
                        else:
                            os.symlink(p, new_comp_folder+'/'+os.path.basename(p))

                elif extension in ['tif']:#misc files
                    misc_folder=os.path.join(publish_version_dir,comp_name,extension)
                    try:
                        os.makedirs(os.path.dirname(misc_folder))
                    except:
                        pass

                    shutil.move(p,misc_folder)

            try:
                f = open(old_publish_version_dir+'/_extra_link_', 'w')
                f.write(publish_version_dir)
                f.close()
            except:
                return traceback.format_exc()

            try:
                 # Send a singal to lock the version folder
                server = self.dialog.version_dir.split('projects')[0]
                v_file = server + 'trash/versions/' + self.dialog.version_name + '_efx.txt'
                f = open(v_file, 'w')
                f.write(publish_version_dir)
                f.close()
            except:
                return traceback.format_exc()

            return ''
        except:
            print 'publish错误，请检查路径是否符合标准.'
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
