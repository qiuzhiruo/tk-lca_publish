import os
import re
import production.pipeline.utils as pplu

def rsync_files(source,destination):
    if not source.endswith('/'):
        source+='/'

    os.system('rsync -az '+source+' '+destination)


def findAllFiles(path):
    """
    find file under path recursively
    """
    result=[]
    for root, dirs, files in os.walk(path):
        for f in files:
            result.append( os.path.join(root, f) )
    return result

def get_efx_data_from_folder(folder):
    files = findAllFiles(folder)
    result_files = []
    folders = []
    for f in files:
        current_f = os.path.dirname(f)
        extension = f.split('.')[-1]
        if extension in ['vdb', 'exr'] and current_f not in folders:
            vdb_f = pplu.findFiles(current_f, '.'+extension,onlyFileName=True)
            result_files.append(current_f+'/'+vdb_f[0]+'-'+vdb_f[-1])
            folders.append(current_f)

        if extension in ['abc', 'nk', 'tif', 'klf']:
            result_files.append(f)

    return result_files

def get_component_name(f):
    extension = f.split('.')[-1]
    comp_name = ''

    if extension in ['abc', 'vdb', 'nk', 'exr', 'tif', 'klf']:
        file_name = os.path.basename(f).split('-')[0]
        folder = os.path.dirname(f)
        file_name_sp = file_name.split('.')

        if len(file_name_sp)>3:
            comp_name = file_name_sp[1]
        else:
            comp_name = file_name_sp[0]
            if re.match('[a-z]\d{5}$',comp_name):
                comp_name = file_name_sp[1]

        name_sp = file_name.split('.')

        if 'efx' in name_sp:
            comp_name = name_sp[name_sp.index('efx')+1]

        if file_name.endswith('.exr') and not folder.endswith('/L') and not folder.endswith('/R'):
            return ('Exr sequence need to be in /L or /R folder')

        if folder.endswith('/'+extension):
            comp_name = folder.split('/')[-2].split('.')[0]
        
        if extension =='exr' and (folder.endswith('/L') or folder.endswith('/R')):
            comp_name = folder.split('/')[-2].split('.')[0]

    if not comp_name:
        return ('Error Cannot find component name for file '+f)
    else:
        return comp_name

# print get_efx_data_from_folder('/mnt/public/home/yingjie/Work/stuff/lala')
# print get_component_name('/mnt/public/home/yingjie/Work/stuff/lala/L/aaa.1001.exr')