# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import traceback
import pymel.core as pm

class AssetLockOperator():
    '''
    This class create locking function for assets by adding asset_selector locator and setting of attributes
    Care must be taken that this class can only be used in mod, rig, asb and scn step
    '''
    def __init__(self):
        path = pm.sceneName().replace('\\', '/')
        # check the step
        self.step = ''
        if '/mod/' in path:
            self.step = 'mod'
        elif '/rig/' in path:
            self.step = 'rig'
        elif '/asb/' in path:
            self.step = 'asb'
        elif '/scn/' in path:
            self.step = 'scn'
        else:
            pm.warning('Adding locking for assets is only available in mod, rig, asb and scn step.')
        # check the type of asset
        self.type = ''
        if '/prp/' in path:
            self.type = 'prp'
        elif '/env/' in path:
            self.type = 'env'
        elif '/veh/' in path:
            self.type = 'veh'

    def overrideDisplay(self, node, override=True):
        if not isinstance(node, type([])):
            node = [node]
        for n in node:
            if not pm.objExists(n):
                continue
            n = pm.PyNode(n)
            try:
                try:
                    if n.attr('drawOverride').isConnected():
                        n.attr('drawOverride').disconnect()
                except:
                    pass
                if override:
                    if n.attr('overrideEnabled').get() != 1:
                        n.attr('overrideEnabled').set(1)
                    if n.attr('overrideDisplayType').get() != 2:
                        n.attr('overrideDisplayType').set(2)
                else:
                    if n.attr('overrideEnabled').get() != 0:
                        n.attr('overrideEnabled').set(0)
                    if n.attr('overrideDisplayType').get() != 0:
                        n.attr('overrideDisplayType').set(0)
            except:
                pass

    def add_locker(self):
        '''
        This is used in mod and rig step
        '''
        try:
            if self.step!='mod' and self.step!='rig':
                pm.warning('add_locker can only be used in mod and rig step!')
                return

            if self.type!='prp' and self.type!='env' and self.type!='veh':
                pm.warning('add_locker can only be used for prp, env, veh type of asset')
                return

            # delete before adding
            self.delete_locker()

            #get master, rig, global_ctrl and poly node
            try:
                master = pm.PyNode('|master')
                rig = pm.PyNode('|master|rig')
                global_ctrl = pm.PyNode('global_ctrl')
                poly = pm.PyNode('|master|poly')
            except:
                print traceback.format_exc()
                return

            # create asset_selector locator
            try:
                loc = pm.spaceLocator(name='asset_selector')
                pm.parent(loc, master)
                pm.parentConstraint(global_ctrl, loc, maintainOffset=False)
                pm.scaleConstraint(global_ctrl, loc, maintainOffset=False)
            except:
                print traceback.format_exc()
                return

            # scale locator to reasonable size
            try:
                s = max( poly.getBoundingBox(space='object').width(),  poly.getBoundingBox(space='object').depth())/2.0
            except:
                s = 1.0
            if s < 0.5:
                s = 0.5

            loc.attr('localScale').set([s,s,s])
            # override display type, so we can select it regardless the settings on parent
            loc.attr('overrideEnabled').set(1)
            loc.attr('overrideColor').set(17)
            # connect useless attribute to the poly group, so user could be hinted by the color of the polyshapes
            loc.caching >> poly.caching
            # lock locator
            loc.attr('translate').lock()
            loc.attr('rotate').lock()
            loc.attr('scale').lock()
            loc.attr('visibility').lock()
            try:
                loc.getShape().attr('visibility').lock()
            except:
                pass

            # overrideEnable stuff
            if self.step == 'mod':
                # disable override on all meshes if step is mod
                groups = pm.listRelatives('|master', type='transform')
                for g in groups:
                    if 'rig' in str(g) or 'asset_selector' in str(g):
                        continue
                    try:
                        if g.attr('drawOverride').isConnected():
                            g.attr('drawOverride').disconnect()
                        g.attr('overrideEnabled').set(0)
                    except:
                        pass
                    trans = pm.listRelatives(g, ad=True, type='transform')
                    for t in trans:
                        try:
                            if t.attr('drawOverride').isConnected():
                                t.attr('drawOverride').disconnect()
                            t.attr('overrideEnabled').set(0)
                            try:
                                if t.getShape().attr('drawOverride').isConnected():
                                    t.getShape().attr('drawOverride').disconnect()
                                t.getShape().attr('overrideEnabled').set(0)
                            except:
                                pass
                        except:
                            pass
            elif self.step == 'rig':
                # rig take over the control of overrideEnabled, we only need to switch to reference displayType
                if pm.objExists('Visibility'):
                    vis = pm.PyNode('Visibility')
                    if vis.hasAttr('meshDisplayType'):
                        vis.attr('meshDisplayType').set(2)

            # hide |master|rig
            rig.attr('lodVisibility').set(0)

            # override |master|poly and others if any
            try:
                self.overrideDisplay( ['|master|poly', '|master|shape', '|master|misc'], override=True )
            except:
                pass

        except:
            print traceback.format_exc()

    def delete_locker(self):
        try:
            if not pm.objExists('|master|asset_selector'):
                # this asset has no selector, could be chr or crd, ignored
                print 'Failed to find |master|asset_selector node'
                return

            if pm.referenceQuery('|master', inr=True):
                # if this is reference, we hide the locker(activate) instead of deleting
                loc = pm.PyNode('|master|asset_selector')
                if loc.attr('lodVisibility').get() != 0:
                    loc.attr('lodVisibility').set(0)
            else:
                pm.delete('|master|asset_selector')

            rig = pm.PyNode('|master|rig')
            if rig.hasAttr('lodVisibility') and rig.attr('lodVisibility').get()!=1:
                rig.attr('lodVisibility').set(1)

            self.overrideDisplay( ['|master|poly', '|master|shape', '|master|misc'], override=False )
        except:
            pass