import os
import sys
import traceback
import shutil
import time
import subprocess


def isAsbUpdated(ma, proj):
    print '###################'
    # find the asb version in the scn file
    print ma
    fileid = open(ma, 'r')
    contents = fileid.read()
    fileid.close()

    scn_name = os.path.basename(ma)[:-3] # strip .ma

    if not contents:
        return -1

    version_scn = ''
    asb_name = ''
    lines = contents.split('\n')
    for l in lines:
        if l.startswith('file ') and '/asset/asb/' in l.replace('\\', '/'):
            version_scn = l.replace('\\', '/').split('/')[-2][-3:]
            asb_name = l.replace('\\', '/').split('/')[-1].split('.')[0]
            break
    if not asb_name:
        print 'Failed to find asb reference, ' + ma
        return -1
    
    print scn_name, ' status:'
    print asb_name, '\nscn version is ', version_scn
    if not version_scn.isdigit():
        return -1

    # find the latest version of asb
    asb_path = '/mnt/proj/projects/' + proj + '/asset/asb/' + asb_name + '/mod/publish/'
    if not os.path.isdir(asb_path):
        print 'Failed to find asb path: ' + asb_path
        return -1

    dirs = sorted( [d for d in os.listdir(asb_path) if d.startswith(asb_name) and d[-3:].isdigit()] )
    version_asb = dirs[-1][-3:]
    if not version_asb.isdigit():
        return -1
    print 'asb version is ', version_asb + '\n'

    if int(version_asb) > int(version_scn):
        return 1
    elif int(version_asb) < int(version_scn):
        return 2

    return 0

def list_scn( proj ):
    '''
    the returned list will be the work files
    '''
    scn_root = '/mnt/proj/projects/' + proj + '/asset/scn/'
    scn = sorted( os.listdir(scn_root) )

    scn_update_list = []
    scn_sync_list = []  # those scn already updated or synced
    scn_strange = []
    for s in scn:
        scn_dir = scn_root+s+'/mod/publish/'
        if not os.path.isdir(scn_dir):
            print 'XXXX ERROR ', s, ', this is an illegal scn asset, ignored' + '\n'
            continue

        folders = sorted( [d for d in os.listdir(scn_dir) if d.startswith(s) and d[-3:].isdigit()] )
        if not folders:
            print 'XXXX ERROR ', s, ', There is no version folder, ignored.' + '\n'
            continue

        publish_ma = '/mnt/proj/projects/' + proj + '/asset/scn/' + s + '/mod/publish/' + folders[-1] + '/' + s + '.ma'
        if not os.path.isfile( publish_ma ):
            print 'XXXX ERROR ', s, ', failed to find the publish file: ' + publish_ma + '\n'
            continue

        #mod_path = scn_root + s + '/mod/publish/' + folders[-1] + '/'
        task_ma = '/mnt/work/projects/' + proj + '/asset/scn/' + s + '/mod/task/maya/' + folders[-1] + '.ma'

        if not os.path.isfile(task_ma):
            print 'XXXX ERROR ', 'failed to find ' + task_ma + '\n'
            continue

        exit_code = isAsbUpdated( task_ma, proj )
        if exit_code == 1:
            scn_update_list.append(task_ma)
        elif exit_code == 0:
            scn_sync_list.append(task_ma)
        elif exit_code == 2:
            scn_strange.append(task_ma)

    return {'update':scn_update_list, 'synced':scn_sync_list, 'ill':scn_strange}

def update( proj ):
    scn_dict = list_scn(proj)
    scn_list = scn_dict['update']
    scn_sync = scn_dict['synced']
    scn_ill = scn_dict['ill']

    log_root = '/mnt/proj/projects/'+proj+'/asset/scn/scn_auto_update_log/'

    old_failed = []
    old_log_path = ''
    try:
        old_log_path = log_root + sorted(os.listdir(log_root))[-1] + '/'
        old_log_path = old_log_path + sorted(os.listdir(old_log_path))[-1] + '/'
    except:
        pass

    old_failed = []
    if scn_list and old_log_path:
        try:
            if os.path.isfile( old_log_path + 'log.failed.txt' ):
                old_log_id = open(old_log_path+'log.failed.txt', 'r')
                contents =  old_log_id.read()
                old_log_id.close()
                if contents:
                    old_failed = [f.strip() for f in contents.split('\n') if f != '' and f != '\n']
                    # filter out the failed scn if it exists in the current list_sync
                    old_failed = list( set(old_failed).difference(scn_sync) )
                    # then filter out the failed scn in the current scn_list
                    scn_list = list( set(scn_list).difference(old_failed) )
        except:
            print traceback.format_exc()

    '''
    if not scn_list:
        print 'There is no scn should be updated.\n'
        if old_failed:
            print 'But the following scn were failed to be updated in the previous running:\n' + '\n'.join(old_failed) + '\n'
        if scn_ill:
            print 'And the following scn is very strange because the version in scn is greater than the version in asb:\n' + '\n'.join(scn_ill)
        return
    '''

    script_path = os.path.dirname(__file__).replace('\\','/')
    mayapy = ''
    TOOL_ROOT = os.getenv('LC_UTILITY')
    if proj=='god':
        try:
            os.system('unset MAYA_LOCATION')
            os.system('source {}/lca_launchers/maya/maya2013config'.format(TOOL_ROOT))
        except:
            print traceback.format_exc()
        mayapy = '/mnt/usr/autodesk/maya2013-x64/bin/mayapy'
    elif proj=='tpr':
        try:
            os.system('unset MAYA_LOCATION')
            os.system('source {}/lca_launchers/maya/maya2015config'.format(TOOL_ROOT))
        except:
            print traceback.format_exc()
        mayapy = '/mnt/usr/autodesk/maya2015-x64-sp5/bin/mayapy'

    log_path = log_root + time.strftime('%y%m%d', time.localtime()) + '/' + time.strftime('%H%M%S', time.localtime()) + '/'

    if not os.path.isdir(log_path):
        os.makedirs( log_path )

    try:
        logid_brief = open(log_path+'log.brief.txt', 'w')
        logid_detail = open(log_path+'log.detail.txt', 'w')
    except:
        print traceback.format_exc()
        return

    failed = old_failed[:]
    success = []

    if scn_list:
        print 'The following scn will be updated: \n' + '\n'.join(scn_list)
    else:
        print 'There is no scn should be updated.\n'

    i = 1
    j = len(scn_list)
    for s in scn_list:
        #scn_task_name = os.path.basename(s)[:-3]
        #scn_task_path = os.path.dirname(s)
        #scn_name = scn_task_name.split('.')[0]
        #if not scn_task_path.endswith('/'):
        #    scn_task_path = scn_task_path + '/'

        # update scn
        print '('+str(i)+'/'+str(j)+') Start to update scn: ' + s
        i = i + 1

        cmd = mayapy + ' ' + script_path + '/update_scn_cmd.py ' + s
        err, out = subprocess.Popen( cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE ).communicate()

        try:
            logid_brief.write( '\n############################\n' + err + '\n' )
            logid_detail.write( '\n############################\n' + out + '\n' )
        except:
            print traceback.format_exc()
            return

        print err

        if 'Failed to update scn:' in err:
            failed.append(s)
            print 'Failed to update.\n' + s
        elif 'Updated successfully!' in err:
            success.append(s)
            print 'Update successfully!\n' + s
        else:
            failed.append(s)

    # close log
    try:
        logid_brief.close()
        logid_detail.close()
    except:
        print traceback.format_exc()
        return

    if failed:
        try:
            logid_failed = open(log_path+'log.failed.txt', 'w')
            logid_failed.write( '\n'.join(failed) )
            logid_failed.close()
        except:
            print traceback.format_exc()
            return

    if success:
        try:
            logid_success = open(log_path+'log.success.txt', 'w')
            logid_success.write( '\n'.join(success) )
            logid_success.close()
        except:
            print traceback.format_exc()
            return

    if scn_ill:
        try:
            logid_ill = open(log_path+'log.ill.txt', 'w')
            logid_ill.write( '\n'.join(scn_ill) )
            logid_ill.close()
        except:
            print traceback.format_exc()
            return

    # send message to tianyi at 10:00 am everyday if any failed
    if (failed or scn_ill) and time.strftime('%H', time.localtime()).startswith('18'):
        try:
            # sys.path.append('U:/toolset/lib/production')
            # sys.path.append('/mnt/utility/toolset/lib/production')
            import production.lca_xmpp as lca_xmpp
            pidgin = lca_xmpp.Sender()
            message = ''
            if failed:
                message = message + 'The following scn were failed to update:\n'+'\n'.join(failed)
            if scn_ill:
                message = message + '\nThe following scn have greater version number compared to the latest asb, that makes no sense at all:\n' + '\n'.join(scn_ill)
            pidgin.send('tianyi', message)
        except:
            print traceback.format_exc()


update('god')