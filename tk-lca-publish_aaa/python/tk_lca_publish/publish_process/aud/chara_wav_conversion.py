# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import traceback
import subprocess
import os
import sys

#import get_wav_abc as gwa

# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将角色wav转换为abc"
        self.description = u"将角色wav文件转换为abc文件，供动画组使用;如果publish是从audio任务启动的，则跳过该步骤"
        return
    
    def proceed(self):
        task_name = self.dialog.version_dir.split('.')[-2]
        #if just normal audio task, do not need to convert anything
        if task_name == 'audio':
            return ''
        try:
            abc_dir = os.path.join(self.dialog.version_dir, 'abc').replace('\\', '/')    # ../tst/preproduction/[seq]/story/aud/publish/[seq].aud.xiaolai.v001/abc 
            if not os.path.exists(abc_dir):
                os.mkdir(abc_dir)
            
            seq_name = self.dialog.entity['name']       # d20
            shots = [os.path.splitext(wav_file)[0] for wav_file in os.listdir(self.dialog.version_dir) if wav_file.endswith('.wav')]
            LCA_PUBLISH_APP = os.getenv('LCA_PUBLISH_APP')
            if sys.platform == 'win32':
                hython_path = '\"C:/Program Files/Side Effects Software/Houdini 14.0.361/bin/hython\"'
                # code_path = 'U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/aud'
            elif sys.platform == 'linux2':
                hython_path = '/mnt/usr/hfs14.0.291/bin/hython'
                # code_path = '/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/aud'
            code_path = '%s/python/tk_lca_publish/publish_process/aud' % LCA_PUBLISH_APP
            args = hython_path + ' -c ' + \
                    '\"import sys;sys.path.append(\'%s\');import get_wav_abc as gwa;gwa.main(%s, \'%s\', \'%s\')\"' % \
                    (code_path, str(shots), self.dialog.version_dir, abc_dir)       # self.dialog.version_dir: wav_dir
            print args
            output = self.run_cmd(args)
            print 'output: ', output
            return output
        except:
            return traceback.format_exc()
        
    def run_cmd(self, args):
        '''
        args: list
        '''
        try:
            #args_str = ' '.join(args)
            args_str = args
            print args_str
            if sys.platform == 'linux2':
                pipe = subprocess.Popen(args_str, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, close_fds = True, shell = True)
            elif sys.platform == 'win32':
                pipe = subprocess.Popen(args_str, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
            import time
            time.sleep(0.5)
            output = pipe.stdout.readlines()
            #if pipe.poll() !=  0:
                #return None
            #else:
                #return output
            print output
            return ''
        except  OSError, e:
            print 'run_cmd: ', ' '.join(args)
            print e
            return str(e)
        
        except ValueError, e:
            print 'run_cmd:', ' '.join(args)
            print e
            return str(e)
    
    def get_process_name(self):
        return self.process_name
    
    def get_description(self):
        return self.description

class Fake_Dialog(object):
    def __init__(self):
        self.entity = {'name':'p20'}
        self.version_dir = '/mnt/proj/projects/tpr/preproduction/%s/story/aud/publish/%s.aud.xiaolai.v002' % (self.entity['name'], self.entity['name'])
        
        

if __name__ == '__main__':
    dialog = Fake_Dialog()
    stdProcess = StdProcess(dialog)
    stdProcess.proceed()
    print 'Done'
    
    
