# -*- coding:utf-8 -*-

import os
import sys
import traceback
import shutil
import subprocess
import time
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"如果场景有变动，那么需要flo针对改动的资产重出cache"
        self.description = u"如果场景有变动，那么需要flo针对改动的资产重出cache"
        return

    def filterObjects(self, obj):
        # convert obj to master
        masters = []
        for o in obj:
            if pm.referenceQuery(o, inr=True):
                ns = pm.referenceQuery(o, ns=True)
                if pm.objExists(ns+':master') and pm.objExists(ns+':poly'):
                    masters.append( pm.PyNode(ns+':master') )
        return filter(None, set(masters))

    def filterOutChrCrd(self, master):
        filtered = []
        for m in master:
            filename = pm.referenceQuery(m, f=True).replace('\\', '/')
            if '/chr/' in filename or '/crd/' in filename:
                continue
            filtered.append(m)
        return filtered

    def findAllAssets(self, top='|assets', ns_level='*:master'):
        masters = []
        masters_raw = [m for m in pm.ls(ns_level, rn=True) if m.isReferenced() and m.isChildOf(top)]
        if not masters_raw:
            return masters_raw
        masters = [m for m in masters_raw if pm.objExists(m.name().replace(':master',':poly'))]
        masters.extend( self.findAllAssets(top, '*:'+ns_level) )
        return masters

    def build_ani_assets_xml(self, xml_path):
        # this function was copied from ani/list_ani_assets.py, and should be updated at every modification of the host
        from xml.dom.minidom import Document

        sys.path.append( self.dialog.tool_root + 'toolset/tools/cfx/lcaCfxCache')
        sys.path.append( self.dialog.tool_root + 'toolset/lib/production/CacheUtils')
        import FilterCacheObjects as cf
        import assetdata as ad

        if not xml_path.endswith('/'):
            xml_path = xml_path + '/'
        xml_path = xml_path.replace('\\', '/')

        l_assets = []
        asset_trans = pm.ls('master', recursive=True, referencedNodes=True)
        for trans in asset_trans:
            # if not trans.name().endswith(':master'):
                # continue

            l_sons = pm.listRelatives(trans, c=True, pa=True)
            for son in l_sons:
                if not son.name().endswith(':poly'):
                    continue

                #asset_name = trans.name().split(":")[-2]
                asset_name = '.'.join( trans.name().split(":")[:-1] )
                #print asset_name
                if pm.referenceQuery(trans, isNodeReferenced=True):
                    ref_path = pm.referenceQuery(trans, filename=True)
                    tokens = ref_path.split('/')
                    if 'asset' in tokens:
                        i = tokens.index('asset')
                        asset_type = tokens[i+1]
                        ref_asset_name = tokens[i+2]
                        asset_src = tokens[i+3]
                    else:
                        asset_type = '-'
                        ref_asset_name = '-'
                        asset_src = '-'
                        #self.d_asset[asset_name] = {'type':tokens[i+1], 'src':tokens[i+3]}
                else:
                    asset_type = '-'
                    ref_asset_name = '-'
                    asset_src = '-'

                l_assets.append(ad.AssetData(asset_name, asset_type, ref_asset_name, asset_src, trans))

        cf.filterCacheObjects(l_assets, fastmode=True)

        cut_in = pm.animation.playbackOptions(q=True, minTime=True)
        cut_out = pm.animation.playbackOptions(q=True, maxTime=True)

        doc = Document()
        master = doc.createElement('anim')
        master.setAttribute('start', str(int(cut_in)) )
        master.setAttribute('end', str(int(cut_out)) )
        doc.appendChild(master)

        for asset in l_assets:
            if asset.flag:
                a = doc.createElement('asset')
                a.setAttribute('type', asset.type)
                a.setAttribute('name', asset.name)
                a.setAttribute('namespace', asset.namespace)
                a.setAttribute('transform', asset.transform.name())
                a.setAttribute('constrained', str(asset.constrained))
                master.appendChild(a)

        f = open( xml_path + 'ani_assets.xml', 'w')
        f.write(doc.toprettyxml(indent = '    '))
        f.close()

    def proceed(self):
        try:
            # find the objects which should be cached
            masters_all = self.findAllAssets()
            masters = self.filterOutChrCrd( self.filterObjects(masters_all) )

            masters = list(set(masters))

            tagged = []
            for m in masters:
                if m.hasAttr('lca_cacheInStereo'):
                    tagged.append(m)

            if not tagged:
                return ""

            # convert master name to cache name
            caches = []
            for t in tagged:
                caches.append( str(t).replace(':master', '').replace(':', '.') )

            # prepare cache path
            cache_path = pm.sceneName().replace('\\', '/').replace('/work/', '/proj/').replace('W:', 'Z:').split('/flo/')[0] + '/flo/publish/'
            if not cache_path.endswith('/'):
                cache_path = cache_path + '/'
            if not os.path.isdir(cache_path):
                print 'Failed to locate cache dir: ' + cache_path
                return ""
            flo_versions = sorted( [d for d in os.listdir(cache_path) if '.flo.final_layout' in d] )
            if not flo_versions:
                return ""
            cache_path = cache_path + flo_versions[-1] + '/'
            flo_file = flo_versions[-1] + '.ma'

            if not os.path.isfile( cache_path+flo_file ):
                print 'Failed to locate flo file: ' + cache_path + flo_file
                return ""

            # copy stereo task to flo publish and overwrite, just before the launch of cache
            time_folder = 'backup/' + time.strftime('%y%m%d%H%M%S', time.localtime())
            if not os.path.isdir( cache_path + time_folder + '/' ):
                os.makedirs( cache_path + time_folder + '/' )
            # backup
            shutil.copyfile( cache_path+flo_file, cache_path+time_folder+'/'+flo_file )
            if os.path.isfile( cache_path+'ani_assets.xml' ):
                shutil.copyfile( cache_path+'ani_assets.xml', cache_path+time_folder+'/ani_assets.xml' )
            # overwrite
            shutil.copyfile( pm.sceneName(), cache_path+flo_file )
            # generate ani_assets.xml
            self.build_ani_assets_xml( cache_path )

            # if os.name == 'posix':
            #     script = '/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/stereo/submitCacheJob.py'
            # else:
            #     script = 'U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/stereo/submitCacheJob.py'
            script = '%s/python/tk_lca_publish/publish_process/stereo/submitCacheJob.py' % os.getenv('LCA_PUBLISH_APP')
                
            cmd_message = ''
            for c in caches:
                cmd = ( 'ulimit -t 120;python %s %s %s %s %s;'%(script, self.dialog.project['name'], flo_file[:-3], c, cache_path) )
                cmd_message = cmd_message + '\n' + cmd
                print cmd
                subprocess.Popen(cmd, shell=True)

            if caches:
                try:
                    # sys.path.append('U:/toolset/lib/production')
                    # sys.path.append('/mnt/utility/toolset/lib/production')
                    import production.lca_xmpp as lca_xmpp
                    reload(lca_xmpp)
                    pidgin = lca_xmpp.Sender()
                    message = flo_file[:-3]+': the following assets were modified by stereo task:\n'+'\n'.join(caches)
                    pidgin.send('zhulin', message)
                    pidgin.send('chengshun', message)
                    pidgin.send('lvyuedong', message + '\nThe render command is:' + cmd_message)
                except:
                    print traceback.format_exc()
                
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


