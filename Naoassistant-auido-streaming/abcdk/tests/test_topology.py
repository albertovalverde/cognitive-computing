# -*- coding: utf-8 -*-
""" Pytest for topology.py """
import topology
from topology import TopologicalMap, VectorSpace
import numeric
import numpy as np
import math
import time

def test_VectorSpace_addPoint6D():
    """
    Test add Point 6D and correct computation of score
    """
    vs = VectorSpace() # create empty VS
    aA1 = np.array([10, 10, 10, 0, 0, math.pi/2.0])
    aA1bis = np.array([10, 10, 10, 0, 0, math.pi/2.2])  # decalage de math.pi/2.0 = 90deg == beaucoup trop
    aA2 = np.array([10, 10, 10, 0, 0, math.pi/4.0])
    aA3 = np.array([10, 10, 10, 0, 0, math.pi/3.0])  # decalage de math.pi/2.0 = 90deg == beaucoup trop


    vs.addPoint6D('nearWorst', aA1, 10, 10) # diag=10meters, pixels = 10 diag
    vs.addPoint6D('worst', aA1, 1, 1) # diag=10meters, pixels = 10 diag

    for i in range(10):
        vs.addPoint6D('perfect', aA1, 10, 10)
        if (i%2) == 0:
            vs.addPoint6D('medium', aA1bis, 10, 10)
            vs.addPoint6D('bad', aA1, 10, 10)
        else:
            if i%3 == 0 :
                vs.addPoint6D('bad', aA2, 10, 10)
            else:
                vs.addPoint6D('bad', aA3, 10, 10)

            vs.addPoint6D('medium', aA1, 10, 10)

    assert(vs.aAmersScores['perfect'] < vs.aAmersScores['worst'])  # score is lower for perfect
    assert(vs.aAmersScores['perfect'] < vs.aAmersScores['medium'] < vs.aAmersScores['nearWorst'])  # score is lower for perfect
    assert(vs.aAmersScores['perfect'] < vs.aAmersScores['medium'] < vs.aAmersScores['bad'] < vs.aAmersScores['nearWorst'])  # score is lower for perfect
    assert(vs.aAmersScores['perfect'] < vs.aAmersScores['medium'] < vs.aAmersScores['bad'] < vs.aAmersScores['nearWorst'] <= vs.aAmersScores['worst'])  # score is lower for perfect

    #vs.addPoint6D('b', aA1, 10)
    #for i in range(10):
    #    vs.addPoint6D('b', aA1, 10)
    #    vs.addPoint6D('b', aA2, 10)
    #assert(np.all(vs.aAmersPose6D['b'] == aA1))
    #assert(vs.aAmersScores['b'] == vs.rMaxScore) # NDEV ce test ne pass pas attention

    # NDEV rajouter des tests

def test_RectangularObstacle():
    a = topology.RectangularObstacle(1,2,3)

def test_CostMap():
    # Map creation:

    # Map serializitation using pickle
    import serialization_tools
    import os
    costMap = topology.CostMap(100 , 100)
    strPath = '/tmp/test.pickle'


    serialization_tools.saveObjectToFile(costMap, strPath )
    rSize = os.path.getsize(strPath)
    assert(rSize < 40000) ## 40Koctets is a maximum for an empty costmap

    obstacle = topology.RectangularObstacle(5, 5, 0.5)
    costMap.addObstacle([50, 10], obstacle, ttl=1)
    #costMap.addObstacle([5, 10], obstacle, ttl=5)
    costMap.addStaticObstacle([5, 10], obstacle)

    serialization_tools.saveObjectToFile(costMap, strPath )
    rSize = os.path.getsize(strPath)
    assert(rSize < 2000000) ## 1Mo for a map with some obstacles..

    #print rSize
    import pylab
    costMapBis = serialization_tools.loadObjectFromFile(strPath)
    costMapBis.draw()
    #pylab.show()


#def test_evaluateLabel():
#    labelPose6D = np.array([ 7.97337806,  0.98869209, -0.23098429,  0.1323602 , -0.21758283, numeric.MinAngle(-3.43999223)])
#    robotPose6D = np.array([ 9.67764975,  1.62962973, -1.31181061,  0.12348359, -0.16337271, numeric.MinAngle(-6.16900518)])
#
#    print topology.evaluateLabel(robotPose6D, labelPose6D)
#    print topology.evaluateLabel(np.array([0,0,0,0,0,0]), np.array([1,1,1,0,0,0]))

def test_computePoseAfterMove():
    np.testing.assert_almost_equal(topology.computePoseAfterMove(np.zeros(6), dxTorso=1, dyTorso=0, dtheta=0), np.array([1., 0., 0., 0., 0., 0.]))
    np.testing.assert_almost_equal(topology.computePoseAfterMove(np.zeros(6), dxTorso=0, dyTorso=1, dtheta=0), np.array([0., 1., 0., 0., 0., 0.]))
    np.testing.assert_almost_equal(topology.computePoseAfterMove(np.zeros(6), dxTorso=0, dyTorso=0, dtheta=1.0), np.array([0., 0., 0., 0., 0., 1.]))
    np.testing.assert_almost_equal(topology.computePoseAfterMove(np.zeros(6), dxTorso=1, dyTorso=0, dtheta=1.0), np.array([1., 0., 0., 0., 0., 1.]))
    np.testing.assert_almost_equal(topology.computePoseAfterMove(np.zeros(6), dxTorso=1, dyTorso=1, dtheta=1.0), np.array([1., 1., 0., 0., 0., 1.]))
    np.testing.assert_almost_equal(topology.computePoseAfterMove(np.zeros(6), dxTorso=1, dyTorso=1, dtheta=48.0), np.array([1., 1., 0., 0., 0., 3.1415]))
    np.testing.assert_almost_equal(topology.computePoseAfterMove(np.zeros(6), dxTorso=1, dyTorso=1, dtheta=-42.0), np.array([1., 1., 0., 0., 0., -3.1415]))

def test_getHeadMove():
#labelPose6D = np.array([ 7.97337806,  0.98869209, -0.23098429,  0.1323602 , -0.21758283, numeric.MinAngle(-3.43999223)])
#aRobotPose6D = np.array([ 9.67764975,  1.62962973, -1.31181061,  0.12348359, -0.16337271, numeric.MinAngle(-6.16900518)])
#print "test"
#    print getHeadMove(np.array([ 8.91617352,  1.54716198, 0 , 0. ,         0. ,        -1.9582767 ]), np.array([ 8.18197895  ,1.65898511 , 0.0,  0.08809285, -0.17426208, numeric.MinAngle(-3.39906762)]))
    #print "finTest"
    #headMove = getHeadMove(aRobotPose6D, labelPose6D)# np.array([1,1,1,0,0,0]))
    #print headMove
    headMove = topology.getHeadMove(np.array([0,0,0,0,0,0]), np.array([1,1,1,0,0,0]))
    np.testing.assert_allclose(headMove.yaw , 0.78, atol=0.1)
    np.testing.assert_allclose(headMove.pitch, -0.52, atol=0.1)
    headMove = topology.getHeadMove(np.array([0,0,1,0,0,0]), np.array([1,0,1,0,0,0]), np.array([0,0,1,0,0,0]))
    np.testing.assert_allclose(headMove.yaw , 0, atol=0.1)
    np.testing.assert_allclose(headMove.pitch, 0.0, atol=0.1)
    headMove = topology.getHeadMove(np.array([0,0,1,0,0,0]), np.array([1,0,0,0,0,0]), np.array([0,0,1,0,0,0]))
    np.testing.assert_allclose(headMove.yaw , 0, atol=0.1)
    np.testing.assert_allclose(headMove.pitch, 0.61, atol=0.1)
    #print("Test succes %s" % str(res))
    #return res


def test_addPoint6DToLocal():
    tMap = TopologicalMap()
    tMap.addPoint6DToLocal(strLabel='test', aPose=np.array([1,1,0,0,0,0]))
    res = tMap.aVss[tMap.nCurLocalVs].aAmersPose6D['test']
    assert( np.all(res == np.array([1,1,0,0,0,0])))

def test_deleteVectorSpacesContainingMark():
    tMap = TopologicalMap()
    #tMap.bDebug = True
    tMap.addPoint6DToLocal(strLabel='test', aPose=[1,1,0,0,0,0])
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.deleteVectorSpacesContainingMark('testB')
    return not(tMap.aVss.has_key(0))

def test_deleteMarkVss():
    tMap = TopologicalMap()
    #tMap.bDebug = True
    tMap.addPoint6DToLocal(strLabel='test', aPose=[1,1,0,0,0,0])
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[1,0,0,0,0,-math.pi/6.0])
    labelToDelete = 'testB'
    tMap.deleteMarkVss(labelToDelete)
#    tMap.aVss[0].draw()
    vs = tMap.aVss[0]
    return not(vs.aAmersPose6D.has_key(labelToDelete) or vs.aAmersAveragePose6D.has_key(labelToDelete) or vs._aAmersSubDictPose6D.has_key(labelToDelete))


def test_forgetViewerPos():
    tMap = TopologicalMap()
    #tMap.bDebug = True
    tMap.forgetViewerPos()
    # TODO : ameliorer ce test
    return (tMap.nCurLocalVs == 1)

def test_setVsLabel():
    tMap = TopologicalMap()
    #tMap.bDebug = True
    tMap.forgetViewerPos()
    tMap.setVsLabel('label0', vsId=0)
    tMap.setVsLabel('current')
    return (tMap.aVss[tMap.nCurLocalVs].strLabel == 'current' and tMap.aVss[0].strLabel == 'label0')

def test_computeRobotPos():
    tMap = TopologicalMap()
    #tMap.bDebug=True
    tMap.addPoint6DToLocal(strLabel='A', aPose=[2,2,0,0,0,0])
    #tMap.addPoint6D(0, 'B', [2,0,0,0,0,0])
    #tMap.addPoint6D(0, 'C', [0,0,0,0,0,-math.pi/3.0], 1.0)
    #tMap.addPoint6D(0, 'O', [5,0,0,0,0,0], 1.0)
    #tMap.forgetViewerPos()
    tMap._updateGlobalVectorSpaceUsingAmer(0, 'A')
    #tMap.updateGlobalMap()  ## not working yet
    #import pylab
    #pylab.figure()
    #tMap.draw()
    #pylab.figure('after update')
    #tMap.updateRobotPos('A', np.array([0, 0, 0, 0, 0, 0]))
    aPos = tMap.computeRobotPos('A', np.array([1, 0, 0, 0, 0, math.pi/2]))
    np.testing.assert_almost_equal(aPos, np.array([2, 3, 0, 0, 0, -math.pi/2.0]))
    return True
    #posToTest = tMap.updateRobotPos('A', np.array([1, 0, 0, 0, 0, math.pi/2]), False) # devrait etre plus rapide.. mais wrong result
    #return (np.all(posok == posToTest))  # test que les deux versions du code renvoie la meme chose

    ## TODO : raffiner le test ici

def test_UpdateGlobalVectorSpace():
    tMap = TopologicalMap()
    tMap.addPoint6DToLocal(strLabel= 'A', aPose= [1,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel= 'B', aPose= [2,0,0,0,0,0])
    tMap.addPoint6DToLocal(strLabel='C', aPose=[8,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    #tMap.addPoint6D(1, 'B', [8,2,0,0,0,math.pi/2])
    tMap.addPoint6DToLocal(strLabel='C', aPose=[6,2,0,0,0,math.pi/2])
    tMap.addPoint6DToLocal(strLabel='D', aPose=[1,0,0,0,0,0])

    #A_0 = tMap.aVss[0].aAmersPose6D['A']
    #B_0 = tMap.aVss[0].aAmersPose6D['B']
    #C_0 = tMap.aVss[0].aAmersPose6D['C']

    #B_1 = tMap.aVss[1].aAmersPose6D['B']
    #C_1 = tMap.aVss[1].aAmersPose6D['C']
    #D_1 = tMap.aVss[1].aAmersPose6D['D']
    #tMap.updateGlobalMapUsingLocalVectorSpace(0)
    #tMap.updateGlobalMapUsingLocalVectorSpace(1)
    tMap.updateGlobalMap()

    tMap.draw()
    import pylab
   # #pylab.show()

def test_UpdateGlobalVectorSpaceUsingAmer():
    ## TODO : n'y a t'il pas un probleme si la pos du robot dans le local est different de 0 ? (pour l'instant c'est tout le temps le cas .. mais a regarder)
    tMap = TopologicalMap()
    tMap.addPoint6DToLocal(strLabel='A', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='B', aPose=[2,0,0,0,0,0])
    tMap.addPoint6DToLocal(strLabel='C', aPose=[8,0,0,0,0,-math.pi/6.0], nViewedSize=1.0)
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='B', aPose=[8,2,0,0,0,math.pi/2])
    tMap.addPoint6DToLocal(strLabel='C', aPose=[6,2,0,0,0,math.pi/2], nViewedSize=0.5)
    tMap.addPoint6DToLocal(strLabel='D', aPose=[1,0,0,0,0,0])

    A_0 = tMap.aVss[0].aAmersPose6D['A']
    B_0 = tMap.aVss[0].aAmersPose6D['B']
    #C_0 = tMap.aVss[0].aAmersPose6D['C']

    #B_1 = tMap.aVss[1].aAmersPose6D['B']
    C_1 = tMap.aVss[1].aAmersPose6D['C']
    #D_1 = tMap.aVss[1].aAmersPose6D['D']

    tMap._updateGlobalVectorSpaceUsingAmer(0, 'C')
    tMap._updateGlobalVectorSpaceUsingAmer(1, 'B')
    A_Global = tMap.aGlobalVs['A']
    B_Global = tMap.aGlobalVs['B']
    C_Global = tMap.aGlobalVs['C']
    #D_Global = tMap.aGlobalVs['D']

    #bdistanceOk =  np.allclose(numeric.dist3D(A_0[:3], B_0[:3]) ,  numeric.dist3D(A_Global[:3], B_Global[:3])  , atol=3)
    #bdistanceOk &= np.allclose(numeric.dist3D(C_1[:3], B_0[:3]) ,  numeric.dist3D(C_Global[:3], B_Global[:3])  , atol=3)

    #bisOk = bdistanceOk

    import pylab
    tMap.bDebug=True
    pylab.figure()
    tMap.aVss[0].draw()
    pylab.figure()
    tMap.aVss[1].draw()
    pylab.figure()
    tMap.draw()
    pylab.show()
    # TODO : rajouter d'autre tests..
    np.testing.assert_allclose(numeric.dist3D(A_0[:3], B_0[:3]) ,  numeric.dist3D(A_Global[:3], B_Global[:3])  , atol=3)
    np.testing.assert_allclose(numeric.dist3D(C_1[:3], B_0[:3]) ,  numeric.dist3D(C_Global[:3], B_Global[:3])  , atol=3)
    #assert(bisOk)

def test_getVs():
    tMap = TopologicalMap()
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='testD', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='testD', aPose=[1,0,0,0,0,-math.pi/6.0])

    return (tMap.getVs('testD') == [0, 1] and tMap.getVs('testB') == [0])

def test_getVsWithName():
    tMap = TopologicalMap()
    tMap.aVss[0].strLabel = 'plop'
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='testD', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='testD', aPose=[1,0,0,0,0,-math.pi/6.0])

    #print (tMap.getVsWithName('plop'))
    return (tMap.getVsWithName('plop') == [0])

def test_updateTopology():
    tMap = TopologicalMap()
    tMap.addPoint6DToLocal(strLabel='A', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='B', aPose=[2,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='B', aPose=[8,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='C', aPose=[9,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='E', aPose=[-5,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='C', aPose=[-5,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='D', aPose=[10,0,0,0,0,-math.pi/6.0])

    tMap._updateGlobalVectorSpaceUsingAmer(0, 'B')
    tMap._updateGlobalVectorSpaceUsingAmer(1, 'B')
    tMap._updateGlobalVectorSpaceUsingAmer(2, 'C')

    tMap.updateTopology()
    return tMap.aNeighbors == {0: {1: 1}, 1: {0: 1, 2: 1}, 2: {1: 1}}

def test_getClosestPtPassage():
    tMap = TopologicalMap()
    tMap.addPoint6DToLocal(strLabel='AA', aPose=[0,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[8,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='BB', aPose=[0,0,0,0,0,-math.pi/6.0])
    tMap._updateGlobalVectorSpaceUsingAmer(0, 'testB')
    tMap._updateGlobalVectorSpaceUsingAmer(1, 'testB')

    tMap.lastMarkUsed = 'testB'
    bPos1isOk = (tMap.getClosestWayPoint() == 1)
    tMap.curPosGlobal = np.array([0,0,0,0,0,0])
    bPos2isOk = (tMap.getClosestWayPoint() == 0)
    tMap.bDebug = True
    tMap.draw()
    import pylab
    #pylab.show()
    return (bPos1isOk and bPos2isOk)

def test_getPathToVs():
    tMap = TopologicalMap()
    tMap.addPoint6DToLocal(strLabel='AA', aPose=[0,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[8,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='BB', aPose=[0,0,0,0,0,-math.pi/6.0])

    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='BB', aPose=[40,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='UU', aPose=[0,0,0,0,0,-math.pi/6.0])

    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='AA', aPose=[5,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='VV', aPose=[0,0,0,0,0,-math.pi/6.0])


    tMap._updateGlobalVectorSpaceUsingAmer(0, 'testB')
    tMap._updateGlobalVectorSpaceUsingAmer(1, 'testB')
    tMap._updateGlobalVectorSpaceUsingAmer(2, 'BB')
    pos = tMap.aRobotCurPos6d
    tMap._updateGlobalVectorSpaceUsingAmer(3, 'AA')
    tMap.updateTopology()

    tMap.lastMarkUsed = 'BB'
    tMap.aRobotCurPos6d = pos
    path = tMap.getPathToVs(0)
    assert ( path == [2,1,0])
    #tMap.bDebug = True
    #tMap.draw()
    #import pylab
    ##pylab.show()


def test_getNextPtPassages():
    tMap = TopologicalMap()

    tMap.addPoint6DToLocal(strLabel='AA', aPose=[0,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[8,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='BB', aPose=[0,0,0,0,0,-math.pi/6.0])

    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='BB', aPose=[40,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='UU', aPose=[0,0,0,0,0,-math.pi/6.0])

    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='AA', aPose=[5,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='VV', aPose=[0,0,0,0,0,-math.pi/6.0])

    tMap._updateGlobalVectorSpaceUsingAmer(0, 'testB')
    tMap._updateGlobalVectorSpaceUsingAmer(1, 'testB')
    tMap._updateGlobalVectorSpaceUsingAmer(2, 'BB')
    pos = tMap.aRobotCurPos6d
    tMap.lastMarkUsed = 'BB'
    tMap._updateGlobalVectorSpaceUsingAmer(3, 'AA')
    tMap.aRobotCurPos6d = pos

    tMap.aVss[0].strLabel = 'I1'
    tMap.aVss[1].strLabel = 'I2'
    tMap.aVss[1].strLabel = 'I3'

    #tMap.bDebug = True
    tMap.updateTopology()
    return ([2, 1, 0] == tMap.getNextWayPoints('I1'))

#def test_getBestLabel():
#    import pylab
#    import serialization_tools
#    np.set_printoptions(precision=3, suppress=True)
#    tMap = serialization_tools.loadObjectFromFile("abcdk/mapCouloirTest.pickle")
#    tMap.curPosGlobal = np.array([0 , 0, 0, 0, 0, math.pi/2])
#
#    tMap.bDebug = True
#    tMap.lastMarkUsed = '231'
#    targetPoint = np.array([1,0.5,0.18,0,0,math.pi/2])
#    print(tMap.getBestLabel(targetPoint, maxDistance=8))
#    tMap.draw()
#    vectDir = numeric.polarToCartesian(1, targetPoint[-1])
#    pylab.quiver(targetPoint[0], targetPoint[1], vectDir[0], vectDir[1], color='g')
#    pylab.show()
#    return False
#
#
#    #print "best strLabel.. for current pos"
#    return ('BB' ==  tMap.getBestLabel(np.array([0,-6,0,0,0,0]), maxDistance=1.8, maxVisionAngle=math.pi/4))


def test_getMove():
    import rvizWrapper
    tMap = TopologicalMap()

    tMap.addPoint6DToLocal(strLabel='AA', aPose=[0,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[1,0,0,0,0,-math.pi/6.0])
    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='testB', aPose=[8,2,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='BB', aPose=[0,1,0,0,0,-math.pi/6.0])
    #tMap.addPoint6D(strLabel='AAAi', pose=[0,1.1,0,0,0,math.pi/6.0])

    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='BB', aPose=[4,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='UU', aPose=[0,-5,0,0,0,-math.pi/6.0])

    tMap.forgetViewerPos()
    tMap.addPoint6DToLocal(strLabel='AA', aPose=[5,0,0,0,0,-math.pi/6.0])
    tMap.addPoint6DToLocal(strLabel='VV', aPose=[0,0,0,0,0,math.pi/6.0])

    tMap._updateGlobalVectorSpaceUsingAmer(0, 'testB')
    tMap._updateGlobalVectorSpaceUsingAmer(1, 'testB')
    tMap._updateGlobalVectorSpaceUsingAmer(2, 'BB')
    pos = tMap.aRobotCurPos6d
    tMap._updateGlobalVectorSpaceUsingAmer(3, 'AA')
    tMap.aRobotCurPos6d = pos

    tMap.aVss[0].strLabel = 'I1'
    tMap.aVss[1].strLabel = 'I2'
    tMap.aVss[2].strLabel = 'I3'
    tMap.aVss[3].strLabel = 'I4'

    #tMap.bDebug=True
    #tMap.aRobotCurPos6d = np.array([-6,-1.1,0,0,0,math.pi/2])
    tMap.aRobotCurPos6d = np.array([-8, -2, 0, 0, 0, 0])
    tMap.draw()
    import pylab
    #pylab.show()

    tMap.updateTopology()
    tMap.strLastUsedAmer = 'UU'
    rvizInterface = rvizWrapper.MarkerArrayInterface()
    tMap.drawRviz()
    for _ in range(20):
        import pylab
        pylab.figure()
        #path = tMap.getNextWayPoints('I4')
        #tMap.drawPath(path)
        dest = tMap.getMove('I4')
        print dest
        tMap.aRobotCurPos6d = dest.theoriticalPose
        vectDir = numeric.polarToCartesian(1, dest.yaw)
        tMap.draw()
        pylab.quiver(dest.theoriticalPose[0], dest.theoriticalPose[1], vectDir[0], vectDir[1], color='g')
        pylab.show()
        #tMap.drawRviz()

        rvizInterface.setRobotPose(tMap.aRobotCurPos6d)
        rvizInterface.plot()
    assert(False)  ## il y a un proleme au dessus.. debugger et mettre les asserts



def test_computeGlobalObjectP6DUsingAmer():
    aZeroP6D = np.zeros(6, dtype=np.float)
    aRes = topology.computeGlobalObjectP6DUsingAmer(aZeroP6D, aZeroP6D, aZeroP6D)
    np.testing.assert_almost_equal(aRes, np.zeros(6))

    aLocalPoint = np.array([1.0, 1.0, 2.0, 0.0, 0.0, 0.0])
    aPivotPoint = np.array([10.0, 10.0, 10.0, 0.0, 0.0, math.pi/2.0])
    aGlobalPivot = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    aRes = topology.computeGlobalObjectP6DUsingAmer(aLocalPoint, aPivotPoint, aGlobalPivot)
    print aRes
    np.testing.assert_almost_equal(aRes, np.array([-9, 9, -8, 0, 0, -math.pi/2.0]))
    return


    aLocalPoint = np.array([1.0, 1.0, 2.0, 0.0, 0.0, 0.0])
    aPivotPoint = np.array([10.0, 10.0, 10.0, 0.0, 0.0, 0.0])
    aGlobalPivot = np.array([2.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    aRes = topology.computeGlobalObjectP6DUsingAmer(aLocalPoint, aPivotPoint, aGlobalPivot)
    print aRes
    np.testing.assert_almost_equal(aRes, np.array([-9+2.0, -9, -8, 0, 0, 0]))

    aLocalPoint = np.array([1.0, 1.0, 2.0, 0.5, 0.0, 0.3])
    aPivotPoint = np.array([10.0, 10.0, 10.0, 0.8, 1.0, -0.8])
    aGlobalPivot = np.array([2.0, 3.3, 0.0, 0.0, 0.2, 0.7])
    aRes = topology.computeGlobalObjectP6DUsingAmer(aLocalPoint, aPivotPoint, aGlobalPivot)
    aOldRes =  np.array([ 13.49079514,  -4.43566799,  -5.84132576,  -0.3       , -0.8       ,   1.8       ])
    np.testing.assert_almost_equal(aRes, aOldRes)


#def test_getPose6DToVs():
#    import serialization_tools
#    import pylab
#    np.set_printoptions(precision=3, suppress=True)
#    topoMap = serialization_tools.loadObjectFromFile("abcdk/mapCouloirTest.pickle")
#    #print topoMap.aRobotCurPos6d
#    #[  1.90916062e+00  -3.85844066e-01  -5.28176249e-02   8.16142731e-05 -5.41414793e-02   1.51947934e+00]
#    topoMap.updateGlobalMap()
#    #topoMap.aRobotCurPos6d = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
#    topoMap.curPosGlobal = np.array([  2.90916062e+00,  -4.85844066e-01,  -5.28176249e-02,   8.16142731e-05, -5.41414793e-02,   1.51947934e+00])
#    print topoMap.curPosGlobal
#    print topoMap.getPose6DToVs('C')
#    print topoMap.getPose6DToVs('D')
#    pose6DToDest = topoMap.getPose6DToVs('D')
#    print numeric.norm2D(pose6DToDest[:2])
#
#    topoMap.lastMarkUsed = '217'
#    ## le bug vient de getMove
#    move = topoMap.getMove('C', maxStep=0.40)
#    print move
#
#
#    topoMap.draw()
#    #pylab.show()

## TODO : remmetre ce test en place

#def test_getMoveToTarget_Stable_XY():
 #  """
 #  check that moving on dx/dy in frame Robot, does not change the orientation in X,Y axis (robot stay on the ground)
 #  :return:
 #  """
 #  tMap = topology.TopologicalMap() # serialization_tools.loadObjectFromFile("/home/lgeorge/projects/test/appu_shared/sdk/abcdk/tests/mapCouloirTest.pickle")

 #  for i in range(10):
 #      tMap.aRobotCurPos6d = np.random.rand(6)
 #      aTarget = np.random.rand(6)
 #      aRes = tMap.getMoveToTarget(aTarget, 200)
 #      np.testing.assert_almost_equal(aTarget[4], aRes.theoriticalPose[4])
 #      np.testing.assert_almost_equal(aTarget[5], aRes.theoriticalPose[5])

def test_getMoveToTarget():
    import pylab
    import serialization_tools
    np.set_printoptions(precision=3, suppress=True)

    tMap = topology.TopologicalMap() # serialization_tools.loadObjectFromFile("/home/lgeorge/projects/test/appu_shared/sdk/abcdk/tests/mapCouloirTest.pickle")

    tMap.aRobotCurPos6d = np.array([0 , 0, 0, 0, 0, 0])
    targetPoint = np.zeros(6)
    move = tMap.getMoveToTarget(targetPoint, 5)
    np.testing.assert_almost_equal(move.dx, 0)
    np.testing.assert_almost_equal(move.dy, 0)
    np.testing.assert_almost_equal(move.dtheta, 0)
    np.testing.assert_almost_equal(move.theoriticalPose, np.zeros(6))


    tMap.aRobotCurPos6d = np.array([1 , 1, 0, 0, 0, 0])
    targetPoint = np.zeros(6)
    move = tMap.getMoveToTarget(targetPoint, 5)
    np.testing.assert_almost_equal(move.dx, -1)
    np.testing.assert_almost_equal(move.dy, -1)
    np.testing.assert_almost_equal(move.dtheta, 0)
    np.testing.assert_almost_equal(move.theoriticalPose, np.zeros(6))

    tMap.aRobotCurPos6d = np.array([1 , 1, 0, 0.0, 0.0, math.pi/2.0])
    targetPoint = np.zeros(6)
    move = tMap.getMoveToTarget(targetPoint, 5)
    np.testing.assert_almost_equal(move.dx, -1, decimal=3)
    np.testing.assert_almost_equal(move.dy, 1, decimal=3)
    np.testing.assert_almost_equal(move.dtheta, 0, decimal=3)
    np.testing.assert_almost_equal(move.theoriticalPose, np.array([0,0,0,0,0,math.pi/2.0]), decimal=3)



    #np.testing.assert_almost_equal(topology.computePoseAfterMove(np.zeros(6), dxTorso=1, dyTorso=0, dtheta=0), np.array([1., 0., 0., 0., 0., 0.]))

    #tMap.lastMarkUsed = '217'
    #maxStep = 1.0

    #targetPoint = np.array([-1,-1,0,0,0,0])
    #move = tMap.getMoveToTarget(targetPoint, 5)
    #print move
    #baOk1 = (move.dx == -1.0) and (move.dy==-1.0) and np.allclose(move.dtheta,-2.35619) and np.allclose(move.theoriticalPose, np.array([-1, -1, 0, 0, 0, -2.3586]), atol=0.01)
    #print baOk1

    #targetPoint = np.array([1,1,0,0,0,0])
    #move = tMap.getMoveToTarget(targetPoint, 5)
    #baOk2 = (move.dx == 1.0) and (move.dy==1.0) and np.allclose(move.dtheta,0.785, atol=0.01) and np.allclose(move.theoriticalPose, np.array([1, 1, 0, 0, 0, 0.785]), atol=0.01)
    #print baOk2
#
    #targetPoint = np.array([-1,1,0,0,0,0])
    #move = tMap.getMoveToTarget(targetPoint, 5)
    #baOk3 = (move.dx == -1.0) and (move.dy==1.0) and np.allclose(move.dtheta,0.785+math.pi/2, atol=0.01) and np.allclose(move.theoriticalPose, np.array([-1, 1, 0, 0, 0, 0.785+math.pi/2]), atol=0.01)
    #print baOk3
#
    #targetPoint = np.array([1,-1,0,0,0,0])
    #move = tMap.getMoveToTarget(targetPoint, 5)
    #baOk4 = (move.dx == 1.0) and (move.dy==-1.0) and np.allclose(move.dtheta,0.785-math.pi/2, atol=0.01) and np.allclose(move.theoriticalPose, np.array([1, -1, 0, 0, 0, 0.785-math.pi/2]), atol=0.01)
    #print baOk4
#
#
    #tMap.curPosGlobal = np.array([1 , 1, 0, 0, 0, 0])
    #targetPoint = np.array([1,1,0,0,0,0])
    #move = tMap.getMoveToTarget(targetPoint, 5)
    #bbOk1 = (move.dx == 0.0) and (move.dy==0.0) and np.allclose(move.dtheta,0, atol=0.01) and np.allclose(move.theoriticalPose, np.array([1, 1, 0, 0, 0, 0]), atol=0.01)
    #print move
    #print("bbOk1 %s" % str(bbOk1))
#
#
    #targetPoint = np.array([1,1,0,0,0,math.pi/2])
    #move = tMap.getMoveToTarget(targetPoint, 5)
    #print move
    #bbOk2 = (move.dx == 0.0) and (move.dy==0.0) and np.allclose(move.dtheta,0, atol=0.01) and np.allclose(move.theoriticalPose, np.array([1, 1, 0, 0, 0, 0]), atol=0.01)
    #print("bbOk2 %s" % str(bbOk2))
#
#
    #targetPoint = np.array([0,1,0,0,0,0])
    #move = tMap.getMoveToTarget(targetPoint, 5)
    #print move
    #bbOk3 = (move.dx == -1.0) and (move.dy==0.0) and np.allclose(move.dtheta,3.14159, atol=0.01) and np.allclose(move.theoriticalPose, np.array([0, 1, 0, 0, 0, 3.14159]), atol=0.01)
    #print("bbOk3 %s" % str(bbOk3))
#
#
    #targetPoint = np.array([0,1,0,0,0,0])
    #move = tMap.getMoveToTarget(targetPoint, 0.1)
    #print move
    #bbOk4 = (move.dx == -0.1) and (move.dy==0.0) and np.allclose(move.dtheta,3.14159, atol=0.01) and np.allclose(move.theoriticalPose, np.array([0.9, 1, 0, 0, 0, 3.14159]), atol=0.01)
    #print("bbOk4 %s" % str(bbOk3))
#
    ##targetPoint = np.array([1,-1,0,0,0,0])
    ##move = tMap.getMoveToTarget(targetPoint, 5)
#
#   # ## un peu plus dure :
    ##targetPoint = np.array([-1,-1,0,0,0,0])
#   # #print tMap.getBestLabel(targetPoint, maxDistance=8)
#   # #move = tMap.getMoveToTarget(targetPoint, 0.20)
#   # #print move
    #tMap.draw()
#   # #pylab.show()
#
    #res = baOk1 and baOk2 and baOk3 and baOk4 and bbOk1 and bbOk2 and bbOk3 and bbOk4
    #print("TEST OK : %s" % str(res))
    #assert(res)


#def test_getMovebis():
#
#    import pylab
#    import serialization_tools
#    np.set_printoptions(precision=3, suppress=True)
#    tMap = serialization_tools.loadObjectFromFile("abcdk/mapCouloirTest.pickle")
#    tMap.curPosGlobal = np.array([0 , 0, 0, 0, 0, math.pi/2])
#    tMap.curPosGlobal = np.array([0 , 0, 0, 0, 0, 0])
#    tMap.lastMarkUsed = '217'
#    print(tMap.getMove('D'))
#    tMap.draw()
#    #pylab.show()

#def test_performance():
#    import serialization_tools
#    import cProfile
#    import pylab
#    topoMap = serialization_tools.loadObjectFromFile('/home/lgeorge/aldebaran3rdfloor_v2.pickle')
#    #topoMap = serialization_tools.loadObjectFromFile('./aldebaran3rdfloor_v2.pickle')
#    startTime = time.time()
#    profile = cProfile.Profile(subcalls=True)
#    profile.runctx('res = topoMap.updateGlobalMap()', globals(), locals())
#    profile.dump_stats('/tmp/profile_run_A.stats')
#    rDuration = (time.time() -  startTime)
#    print("Duration %f seconds" % rDuration)
#    assert(rDuration < 1.0)
#
#    topoMap.updateTopology()
#    topoMap.updateGlobalMap()
#    topoMap.draw()
#    #pylab.show()
#
