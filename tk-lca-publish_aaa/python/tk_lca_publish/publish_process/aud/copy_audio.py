__author__ = 'yingjie'
import os
import shutil
import hashlib


class CopyAudio:
    def __init__(self, dialog):
        self.dialog = dialog
        self.publish_folder = ''
        self.all_aud_version=[]
        self.task_name=self.dialog.version_dir.split('.')[-2]
        print 'Current task is ',self.task_name
        

    def do_publish(self):
        #get publish folder info and save current katana scene into a temp file
        self.get_work_folder()

        self.get_publish_aud()

        self.check_copy()

        self.copy_old_wav()

    def check_copy(self):
        aud_publish_to = self.dialog.version_dir
        for ad in self.dialog.wav_files:
            tt_dir, tt_file = os.path.split(ad)
            if self.task_name != 'audio':       # e.g. self.task_name == 'xiaolai'
                tt_file = tt_file.replace('_' + self.task_name, '')  
            # destination file when executing os.symlink
            symb_tx = os.path.join(aud_publish_to, tt_file)     #e.g. ../aud/pulish/d20.aud.xiaolai.v003/d20355_xiaolai.wav
            self.check_aud(ad,symb_tx)

    def check_aud(self, tex_name, symbol_link_tx):
        if os.path.isfile(symbol_link_tx):
            return

        f = open(tex_name, 'rb')
        c = f.read()
        f.close()
        tex_hash = hashlib.md5(c).hexdigest()

        file_n = os.path.basename(tex_name)

        for t in self.all_aud_version:
            if (t['aud']+'.wav') == file_n:
                if tex_hash == t['md5']:
                    old_tex_file = t['path']+'/'+t['aud']+'.wav'
                    relative_tex = '../'+old_tex_file.split('/publish/')[1]
                    os.symlink(relative_tex, symbol_link_tx)
                else:
                    new_version_path = self.get_new_version(t['path'])
                    self.copy_aud(tex_name, new_version_path, symbol_link_tx, tex_hash)
                return

        #if the tex is a new file
        self.copy_aud(tex_name, None, symbol_link_tx, tex_hash)

    def copy_aud(self, tex_name, ver_path, symbol_link_tx, tex_hash):
        file = os.path.basename(tex_name)
        if self.task_name != 'audio':       # e.g. self.task_name == 'xiaolai'
            file = file.replace('_' + self.task_name, '')       #e.g. from 'd20355_xiaolai.wav' to 'd20355.wav'

        tex_path = os.path.join(self.publish_folder, self.task_name)
        if not ver_path:
            ver_path = os.path.join(tex_path, os.path.splitext(file)[0] + '.v001')

        if not os.path.isdir(ver_path):
            os.mkdir(ver_path)
            os.chmod(ver_path, 0777)
        new_tex_file = os.path.join(ver_path, file).replace('\\', '/')
        shutil.copy(tex_name, new_tex_file)
        relative_tex = '../'+new_tex_file.split('/publish/')[1]
        os.symlink(relative_tex, symbol_link_tx)

        f = open(os.path.join(ver_path, tex_hash), 'w')
        f.close()

    def get_work_folder(self):
        if self.dialog.wav_files:
            self.publish_folder = os.path.dirname(self.dialog.version_dir)
            aud_path = os.path.join(self.publish_folder, self.task_name)
            if not os.path.isdir(aud_path):
                os.mkdir(aud_path)
                os.chmod(aud_path,0777)

    def copy_old_wav(self):
        new_names=[]
        for ad in self.dialog.wav_files:
            newname = os.path.basename(ad)
            if self.task_name != 'audio':
                newname = newname.replace('_' + self.task_name, '')
            new_names.append(newname)

        #copy old wav files
        for t in self.all_aud_version:
            if (t['aud']+'.wav') not in new_names:
                symbol_link_tx = os.path.join(self.dialog.version_dir,t['aud']+'.wav')
                old_tex_file = t['path']+'/'+t['aud']+'.wav'
                relative_tex = '../'+ old_tex_file.split('/publish/')[1]
                os.symlink(relative_tex, symbol_link_tx)
    
    def get_publish_aud(self):
        publish_aud = os.path.join(self.publish_folder, self.task_name)

        self.all_aud_version=[]
        if os.path.isdir(publish_aud):
            tx_vers = os.listdir(publish_aud)
            tx_vers_sort = sorted(tx_vers)

            tx_len = len(tx_vers_sort)

            for i in range(tx_len):
                loc_path = publish_aud + '/' + tx_vers_sort[i]
                md5_code=''
                if os.path.isdir(loc_path):

                    files = os.listdir(loc_path)
                    for f in files:
                        if len(f.split('.'))==1:
                            md5_code=f
                            break
                    current_tx = tx_vers_sort[i][0:tx_vers_sort[i].rfind('.')]
                    if i == tx_len-1:
                        self.all_aud_version.append({'aud': current_tx, 'path': loc_path, 'md5': md5_code})
                    else:
                        next_tx = tx_vers_sort[i+1][0:tx_vers_sort[i+1].rfind('.')]
                        if current_tx != next_tx:
                            self.all_aud_version.append({'aud': current_tx, 'path': loc_path, 'md5': md5_code})
    
    def get_new_version(self, path):
        last_dot = path.rfind('.')
        path_version = path[last_dot+2:len(path)]
        new_version = int(path_version)+1
        return path[0:last_dot]+'.v'+str(new_version).zfill(3)
    