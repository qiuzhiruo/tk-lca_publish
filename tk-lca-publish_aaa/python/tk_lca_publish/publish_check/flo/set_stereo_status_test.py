# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import lay.lca_camera_lock.functions as functions_cl
reload(functions_cl)

import production.lca_xmpp as lca_xmpp
reload(lca_xmpp)

import stereo.findStereoCamera as fsc
reload(fsc)

# All publish process will use StdProcess as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"set stereo status test"
        self.description = u"set stereo status test"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def osPathConvert(self, path):
        path = path.replace('\\', '/')
        if os.name == 'nt':
            if path.startswith('/mnt/proj/'):
                return path.replace('/mnt/proj/', 'Z:/')
            elif path.startswith('/mnt/work/'):
                return path.replace('/mnt/work/', 'W:/')
            elif path.startswith('/output/'):
                return path.replace('/output/', 'O:/')
            elif path.startswith('/mnt/utility/'):
                return path.replace('/mnt/utility/', 'U:/')
            elif path.startswith('/mnt/public/'):
                return path.replace('/mnt/public/', 'P:/')
            elif path.startswith('/mnt/usr/'):
                return path.replace('/mnt/usr/', 'C:/Program Files/')
            else:
                return path
        else:
            if path.startswith('Z:/'):
                return path.replace('Z:/', '/mnt/proj/')
            elif path.startswith('W:/'):
                return path.replace('W:/', '/mnt/work/')
            elif path.startswith('O:/'):
                return path.replace('O:/', '/output/')
            elif path.startswith('U:/'):
                return path.replace('U:/', '/mnt/utility/')
            elif path.startswith('P:/'):
                return path.replace('P:/', '/mnt/public/')
            elif path.startswith('C:/Program Files/'):
                return path.replace('C:/Program Files/', '/mnt/usr/')
            else:
                return path
        return path

    def run_check(self):
        try:
            stereo_cam_path = self.osPathConvert( str(fsc.findStereoCamera(self.dialog.entity['name'], self.dialog.project['name'].lower())) )
            print 'stereo camera path: '+stereo_cam_path

            status = False
            if self.dialog.step['name']=='flo' and os.path.isfile(stereo_cam_path):
                status = True
            elif self.dialog.step['name']=='ani' and not functions_cl.is_camera_locked() and os.path.isfile(stereo_cam_path):
                status = True

            print 'step: '+self.dialog.step['name']
            print 'project: '+self.dialog.project['name']
            print 'entity: '+self.dialog.entity['name']

            print 'is_camera_locked: '+str(functions_cl.is_camera_locked())
            print 'status: '+str(status)

            if status:
                info = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name'].lower()],['entity', 'name_is', self.dialog.entity['name']], ['step', 'name_is', self.dialog.step['name']], ['content', 'is', 'stereo']], ['sg_status_list'])
                if info:
                    print 'changing stereo status...'

                    task_id = info['id']
                    task_status = info['sg_status_list']
                    #if task_status=='aa' or task_status=='aaa' or task_status=='da' or task_status=='fin' or task_status=='rtk':

                    # change status
                    self.dialog.sg.update('Task', task_id, {'sg_status_list':'ip'})

                    # send message
                    try:
                        pidgin = lca_xmpp.Sender()
                        message = self.dialog.entity['name']+': stereo status was changed to ip, due to publish of final_layout.'
                        pidgin.send('lvyuedong', message)
                    except:
                        print traceback.format_exc()

                if self.dialog.step['name']=='ani':
                    # we also change flo status
                    info = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name'].lower()],['entity', 'name_is', self.dialog.entity['name']], ['step', 'name_is', self.dialog.step['name']], ['content', 'is', 'final_layout']], ['sg_status_list'])
                    if info:
                        print 'changing flo status...'

                        task_id = info['id']
                        task_status = info['sg_status_list']
                        #if task_status=='aa' or task_status=='aaa' or task_status=='da' or task_status=='fin' or task_status=='rtk':

                        # change status
                        self.dialog.sg.update('Task', task_id, {'sg_status_list':'ip'})

                        # send message
                        try:
                            pidgin = lca_xmpp.Sender()
                            message = self.dialog.entity['name']+': final_layout status was changed to ip, due to changes of camera from animation.'
                            for usr in ['tianyi', 'ericshen', 'xusanshan', 'zhaoqi', 'zouyu']:
                                pidgin.send(usr, message)
                        except:
                            print traceback.format_exc()

            return ""
            
        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        return

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


