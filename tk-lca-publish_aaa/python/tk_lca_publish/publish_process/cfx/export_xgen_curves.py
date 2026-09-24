# -*-coding:utf-8-*-

import traceback
import maya.mel as mel
import xgenm as xg
from xgenm.ui.xgDescriptionEditor import refreshDescriptionEditor


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出xgen曲线"
        self.description = u"将全部xgen曲线导出成mel文本"
        return

    def proceed(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                return 'task not hair'

            collections = xg.palettes()
            if not collections:
                return 'No Collections'
            else:
                '''
                遍历所有Description，记录原始的preview percent，然后将preview percent和render percent全部改为100，导出Mel文本，再将preview percent改回去
                '''
                for collection in collections:
                    descriptions = xg.descriptions(collection)
                    if not descriptions:
                        return 'No Descriptions'
                    else:
                        for description in descriptions:
                            print 'Export Xgen Curve: ', collection + ' ' + description
                            percent = xg.getAttr('percent', collection, description, 'GLRenderer')
                            xg.setAttr('percent', '100', collection, description, 'GLRenderer')
                            output_path = self.dialog.version_dir + '/xgen/mel/{collection}/{description}'.format(collection=collection, description=description)
                            mel_cmd = 'xgmMelRender -pb {"%s"};' % description
                            xg.setActive(collection, description, 'MelRenderer')
                            xg.setAttr('percent', '100', collection, description, 'MelRenderer')
                            xg.setAttr('outputDir', output_path, collection, description, 'MelRenderer')
                            refreshDescriptionEditor()
                            mel.eval(mel_cmd)
                            # xg.igExportMaps( [description] )
                            xg.setAttr('percent', percent, collection, description, 'GLRenderer')
                            xg.setActive(collection, description, 'RendermanRenderer')
                            refreshDescriptionEditor()
                return ''

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description