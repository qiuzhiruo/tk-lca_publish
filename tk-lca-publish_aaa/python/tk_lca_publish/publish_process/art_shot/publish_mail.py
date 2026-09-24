# -*- coding:utf-8 -*-
import sys
import os
import xml.dom.minidom as minidom
import create_sg_version
import traceback

if sys.platform.startswith('win'):
    # WORK_ROOT = 'W:'
    OUTPUT_ROOT = 'O:'
    PUBLISH_ROOT = 'Z:'
    # TOOL_ROOT = 'U:'
elif sys.platform.startswith('linux'):
    # WORK_ROOT = '/mnt/work'
    OUTPUT_ROOT = '/output'
    PUBLISH_ROOT = '/mnt/proj'
    # TOOL_ROOT = '/mnt/utility'

WORK_ROOT = os.getenv('LC_WORK')
TOOL_ROOT = os.getenv('LC_UTILITY')


class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"color_key的version preview路径同步到1984"
        self.description = u"color_key的version preview路径同步到1984"
        return

    def write_cache(self, server):
        if self.dialog.entity['type'] == 'Shot':
            proj_name = self.dialog.project['name'].lower()
            step_name = self.dialog.step['name']

            l_preview = create_sg_version.get_version_folder(self.dialog.l_preview_files, proj_name, step_name)
            v_file = server + '/trash/log/1984/Version_Caches/' + proj_name + '.txt'
            for file_path in l_preview:
                shot_name = os.path.basename(file_path).split('.')[0]
                version_name = file_path.split('/')[-1]
                with open(v_file, 'a') as f:
                    mov1 = server + 'projects/' + proj_name + '/shot/' + shot_name[:3] + '/' + shot_name + '/' + \
                           self.dialog.step['name'] + '/publish/' + version_name + '/preview/' + version_name + '.mov'
                    f.write(mov1.replace(server, '/mnt/proj/') + '\n')

    def proceed(self):
        try:
            proj_name = self.dialog.project['name'].lower()
            step_name = self.dialog.step['name']

            # Query skipped checks
            server = PUBLISH_ROOT
            self.write_cache(server)

            l_preview = create_sg_version.get_version_folder(self.dialog.l_preview_files, proj_name, step_name)

            try:
                for file_path in l_preview:
                    version_name = file_path.split('/')[-1]
                    v_file = server + '/trash/versions/' + version_name + '.txt'
                    with open(v_file, 'wb') as f:
                        f.write(file_path.replace(server, '/mnt/proj/'))
            except:
                print 'Failed to Send a singal to lock the version folder.'

            # Version log
            try:
                for file_path in l_preview:
                    shot_name = os.path.basename(file_path).split('.')[0]
                    version_name = file_path.split('/')[-1]
                    publish_dir = PUBLISH_ROOT + '/projects/' + proj_name.lower() + '/shot/' + shot_name[
                                                                                               :3] + '/' + shot_name + '/' + step_name + '/publish/' + version_name
                    version_tag = self.dialog.w_sys.comboBox_tag.currentText()
                    self.dialog.print_log('pub image path :' + str(version_tag))

                    doc = minidom.Document()
                    root = doc.createElement('Version')
                    doc.appendChild(root)
                    tag = doc.createElement('Tag')
                    root.appendChild(tag)
                    tag.setAttribute('value', u'精确色稿')
                    tag = doc.createElement('Name')
                    root.appendChild(tag)
                    tag.setAttribute('value', version_name)

                    f = open(publish_dir + '/version_log.xml', 'w')
                    f.write(doc.toprettyxml(indent='\t', encoding="utf-8"))
                    f.close()
            except:
                print 'Failed to write the version log.'

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
