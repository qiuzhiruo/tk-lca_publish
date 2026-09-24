import hou
import os
import sys

# if sys.platform == 'win32':
#     TEMPLATE_HIP = 'U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/aud/template_hip/voice.hip'
# elif sys.platform == 'linux2':
#     TEMPLATE_HIP = '/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/aud/template_hip/voice.hip'
tk_lca_publish_path = os.getenv('LCA_PUBLISH_APP')
TEMPLATE_HIP = '{}/python/tk_lca_publish/publish_process/aud/template_hip/voice.hip'.format(tk_lca_publish_path)

def reset_wav_file(wav_dir, shot):
    #wf = os.path.join(wav_dir, shot + '_xiaolai.wav')
    wf = os.path.join(wav_dir, shot + '.wav')
    wave_file_node = hou.node('/obj/chopnet_voice/wavefile')
    wave_file_node.parm('file').set(wf)

def exportWav(abc_dir, duration, shot):
    filename = os.path.join(abc_dir, shot + '.abc')
    f1 = 1
    f2 = duration
    abcExport = hou.node('/out/alembicExport')
    abcExport.parm('f1').set(f1)
    abcExport.parm('f2').set(f2)
    abcExport.parm('filename').set(filename)
    abcExport.render(frame_range = (f1, f2, 1), output_file = filename)

def loadTemplateHip(hip):
    try:
        hou.hipFile.load(hip)
    except hou.LoadWarning, e:
        print e
    except hou.OperationFailed, e:
        print e

def saveTemplateHip():
    try:
        hou.hipFile.save()
    except hou.OperationFailed, e:
        print e

def getShotDurations(shots, proj = 'TPR'):
    # if sys.platform == 'win32':
    #     thd_parites = u'U:/toolset/lib/3rd_party'
    # else:
    #     thd_parites = u'/mnt/utility/toolset/lib/3rd_party'
    # if thd_parites not in sys.path:
    #     sys.path.append(thd_parites)
    # from shotgun_api3 import shotgun
    #
    # SG_URL = u'http://shotgun.zhuiguang.com/'
    # SG_SCRIPT_NAME = u'Tank'
    # SG_SCRIPT_KEY = u'5d368446b5b0edb4366a9a57c4fd22e3e3cd79b0'
    shot_dur_dict = {}
    from production.shotgun_connection import Connection
    for shot_name in shots:
        try: 
            sg = Connection('get_shot_info').get_sg()
            #shot = sg.find('Shot', [['project',  'name_is',  proj], ['code',  'is', 'd20355' ]], ['sg_cut_duration', 'sg_cut_in', 'sg_cut_out'])
            shot = sg.find('Shot', [['project',  'name_is',  proj], ['code',  'is', shot_name]], ['sg_cut_duration'])
            duration = shot[0]['sg_cut_duration']
        except Exception, e:
            print 'Cannot get shot duration from shotgun'
            print e
            duration = None
        shot_dur_dict[shot_name] = int(duration)
    return shot_dur_dict

def shot_export(shot, duration, wav_dir, abc_dir):
    if duration:
        reset_wav_file(wav_dir, shot)
        exportWav(abc_dir, duration, shot)
        saveTemplateHip()
        print shot, 'conversion succeeded.'
    else:
        print 'Failed to export wav abc from ', shot, 'please contact TD for solution.'
        
def main(shots, wav_dir, abc_dir):
    shot_dur_dict = getShotDurations(shots)
    loadTemplateHip(TEMPLATE_HIP)
    for shot in shots:
        shot_export(shot, shot_dur_dict[shot], wav_dir, abc_dir)
        
    print 'Done!'


