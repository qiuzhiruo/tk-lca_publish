import traceback
import os
import subprocess
import sys
# sys.path.append('/mnt/utility/toolset/lib')
import production.pipeline.lcProdProj as clpp
import shutil

tool_srf_path='{}/python/tk_lca_publish/publish_process/srf_sg'.format(os.getenv('LCA_PUBLISH_APP'))
out = open("/tmp/srf_batch_publish_log.txt",'w')
err = open('/tmp/srf_batch_publish_error.txt','w')


cp=clpp.lcProdProj()
cp.setProj('god')

def has_klf(folder):
    found_klf=False
    if folder:
        pub_files=os.listdir(folder)
        for pf in pub_files:
            if pf.endswith('.klf'):
                found_klf=True
    return found_klf

def batch_check(list_file,mark='batch'):
    file_content=[]
    with open(list_file) as f:
        file_content = f.readlines()


    error_list=[]
    index=1
    for fff in file_content:
        ff=None
        if fff.endswith('\n'):
            ff=fff[:-1]
        else:
            ff=fff

        print float(index)/float(len(file_content))*100,'%'
        index+=1

        asset_name = os.path.basename(ff).split('.')[0]
        version_dict=cp.get_asset_version_folder(asset_name,'srf')
        
        latest_ver=None
        if not version_dict:
            error_list.append(ff)
            continue

        if version_dict.has_key('surfacing'):
            latest_ver = version_dict.get('surfacing')[-1]
        elif version_dict.has_key('srf'):
            latest_ver = version_dict.get('srf')[-1]

        if not has_klf(latest_ver):
            error_list.append(ff)
            if os.path.isfile(latest_ver+'/'+mark):
                shutil.rmtree(latest_ver)

    return error_list    

def batch_publish(list_file,mark='batch'):
    file_content=[]
    with open(list_file) as f:
        file_content = f.readlines()

    error_list=[]
    index=1
    for fff in file_content:
        ff=None
        if fff.endswith('\n'):
            ff=fff[:-1]
        else:
            ff=fff

        print float(index)/float(len(file_content))*100,'%'
        index+=1
        if not ff or not os.path.isfile(ff):
            error_list.append(ff)
            continue

        cmd = 'katana '+ '--script='+tool_srf_path+'/do_publish_srf_katana.py'

        asset_name = os.path.basename(ff).split('.')[0]
        version_dict=cp.get_asset_version_folder(asset_name,'srf')
        if not asset_name:
            error_list.append(ff)
            continue

        latest_ver=None
        if not version_dict:
            error_list.append(ff)
            continue

        if version_dict.has_key('surfacing'):
            latest_ver = version_dict.get('surfacing')[-1]
        elif version_dict.has_key('srf'):
            latest_ver = version_dict.get('srf')[-1]

        if not latest_ver:
            latest_ver=cp.getAssetFolder(asset_name,'srf')+\
                        '/'+asset_name+'.srf.surfacing.v001'

        if os.path.isfile(latest_ver+'/'+mark) and has_klf(latest_ver):
            error_list.append(ff)
            continue

        if not os.path.isdir(latest_ver) or not has_klf(latest_ver):
            current_ver=latest_ver
        else:
            current_ver=latest_ver[:-3] + str(int(latest_ver[-3:])+1).zfill(3)

        print '======Asset Name : %s =====New Version : %s' % (asset_name,current_ver)

        cmd += ' '+current_ver
        cmd += ' '+ff
        
        try:        
            pp = subprocess.Popen(cmd, shell=True, stdout=out,stderr=err)
            pp.wait()

            if not has_klf(current_ver):
                error_list.append(ff)
                shutil.rmtree(current_ver)
            else:
                os.system('touch '+current_ver+'/'+mark)

        except:
            print traceback.format_exc()
            try:
                os.remove(current_ver)
            except:
                print traceback.format_exc()

            error_list.append(ff)

    if error_list:
        list_folder=os.path.dirname(list_file)
        with open(list_file+'.error','w') as f:
            f.writelines(error_list)

        print 'Failed katana file','\n'.join(error_list)
    
    return error_list
"""
python /home/yingjie/git_repo/tk-lca-publish/python/tk_lca_publish/publish_process/srf_sg/batch_publish_srf.py "/mnt/public/Share/jerry/srf_publish_list/publish_prp.list" "publish"
""" 
if __name__ == "__main__":

    try:
        list_file=sys.argv[-2]
        if not os.path.isfile(list_file):
            print 'Error : wrong file',list_file

        if sys.argv[-1]=='publish':

            print batch_publish(list_file)

        elif sys.argv[-1]=='check':

            print batch_check(list_file)
    except:
        print traceback.format_exc()

