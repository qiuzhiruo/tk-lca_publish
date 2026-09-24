# -*- coding:utf-8 -*-

import pymel.core as pm

import lay.lca_camera_lock.functions as functions_cl
reload(functions_cl)


def get_constrained_nodes():
    constrained_nodes = []
    cameras_grp = functions_cl.get_cameras_group()
    camera_nodes = cameras_grp.getChildren(allDescendents=True, type='transform')
    camera_nodes.append(cameras_grp)
    constraint_nodes = []
    for node in camera_nodes:
        for attr in ('t', 'r', 's'):
            constraints = node.attr(attr).outputs(type='constraint')
            # print 'node / constraints: (' + str(node) + ' / ' + str(constraints) + ')'
            if constraints:
                constraint_nodes.extend(constraints)

    constraint_nodes = list(set(constraint_nodes))
    for const in constraint_nodes:
        outputs = list(set(const.outputs(type=['transform','pairBlend'])))
        for output in outputs:
            if output in camera_nodes:
                continue

            if pm.objectType(output, isAType='constraint'):
                continue

            if output in constrained_nodes:
                continue
                
            if pm.objectType(output, isAType='pairBlend'):
                output = list(set(output.outputs(type='transform')))
                if len(output) != 0:
                    constrained_nodes.extend(output)
                continue

            constrained_nodes.append(output)

    return list(set(constrained_nodes))
