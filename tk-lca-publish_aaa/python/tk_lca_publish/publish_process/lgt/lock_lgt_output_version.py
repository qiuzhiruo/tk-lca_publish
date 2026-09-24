import os

root_dir='/mnt/proj/trash/lgt_publish_info'
pub_list=os.listdir(root_dir)
try:
    os.makedirs(root_dir+'/old')
except:
    pass
for p in pub_list:
    if p.endswith('.pub'):
        with open(root_dir+'/'+p) as f:
            pub_dir=f.readline().strip()
            print 'Lock file',pub_dir
            
            exr_dir=os.path.join(pub_dir,'exr')
            if os.path.isdir(exr_dir+'/L') and os.path.islink(exr_dir+'/L'):
                link_dir=os.path.realpath(exr_dir+'/L')
                os.system('chown -R root '+link_dir)
                os.system('chmod -R 755 '+link_dir)
            if os.path.isdir(exr_dir+'/R') and os.path.islink(exr_dir+'/R'):
                link_dir=os.path.realpath(exr_dir+'/R')
                os.system('chown -R root '+link_dir)
                os.system('chmod -R 755 '+link_dir)
        os.system('mv '+root_dir+'/'+p+' '+root_dir+'/old')
