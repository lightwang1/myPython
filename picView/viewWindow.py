#coding:utf8
'''
Created on 2015-9-3

@author: Administrator
'''

import pygame
import os
import thread
from time import sleep

def createPlayContext(recorder, playList):
    if recorder == None or playList == None:
        return None
    if not isinstance(recorder, dict):
        return None
    if not isinstance(playList, list):
        return None
    if len(playList) == 0:
        return None
    ret = {}
    ret.setdefault('recorder', recorder)
    ret.setdefault('playList', playList)
    return ret

def clamp(v, l, r):
    if v <= l: return l
    if v >= r: return r
    return v

class TransfromCtrl:
    def __init__(self, winSz, imgSz):
        self.winSz = winSz
        self.imgSz = imgSz
        self.__bltPos = (0, 0)
        self.__maxScale = 4.0
        self.__isMoving = False
        
    def adjustCenter(self):
        szImg = self.imgSz
        szWin = self.winSz
        sw = float(szWin[0]) / szImg[0]
        sh = float(szWin[1]) / szImg[1]
        scale = sw < sh and sw or sh
        if scale < 1.0:
            self.__scale = scale
            self.__minScale = scale
        else:
            self.__scale = 1.0  
            self.__minScale = 1.0
        self.__bltPos = self.__adjustBltPos((0, 0))
        
    def __winToPic(self, pos):
        rx = (pos[0] - self.__bltPos[0]) / self.__scale
        ry = (pos[1] - self.__bltPos[1]) / self.__scale
        return (rx, ry) 
    
    def __picToWin(self, pos):
        rx = pos[0] * self.__scale + self.__bltPos[0]
        ry = pos[1] * self.__scale + self.__bltPos[1]
        return (rx, ry) 
    
    def __isInPic(self, pos):
        if pos[0] < 0 or pos[0] > self.imgSz[0]:
            return False
        if pos[1] < 0 or pos[1] > self.imgSz[1]:
            return False
        return True
        
    def startMove(self, pos):
        picPos = self.__winToPic(pos)
        if not self.__isInPic(picPos):
            return
        self.__isMoving = True
        self.__startPos = pos
        self.__tmpBltPos = self.__bltPos
        
    def endMove(self, pos):
        if self.__isMoving == False:
            return
        self.__isMoving = False
        pbx = pos[0] - self.__startPos[0] + self.__bltPos[0]
        pby = pos[1] - self.__startPos[1] + self.__bltPos[1]
        self.__bltPos = self.__adjustBltPos((pbx, pby))
        
    def Moving(self, pos):
        if not self.__isZoomed():
            return
        pbx = pos[0] - self.__startPos[0] + self.__bltPos[0]
        pby = pos[1] - self.__startPos[1] + self.__bltPos[1]
        self.__tmpBltPos = self.__adjustBltPos((pbx, pby))
        
    def __zoom(self, factor, winPos):
        picPos = self.__winToPic(winPos)
        if not self.__isInPic(picPos):
            return
        scale = self.__scale * factor
        scale = clamp(scale, self.__minScale, self.__maxScale)
        if scale == self.__scale:
            return False
        if self.__isMoving:
            return False
        px = int(winPos[0] - picPos[0] * scale)
        py = int(winPos[1] - picPos[1] * scale)
        self.__scale = scale
        self.__bltPos = self.__adjustBltPos((px, py))
        return True
        
    def zoomIn(self, pos):
        return self.__zoom(1.2, pos)
        
    def zoomOut(self, pos):
        return self.__zoom(0.8, pos)
        
    def __adjustBltPos(self, pos):
        (px, py) = (0, 0)
        dx = self.winSz[0] - self.imgSz[0] * self.__scale
        if dx >= 0:
            px = int(dx / 2)
        else:
            if pos[0] >= 0:
                px = 0
            else:
                px = max(dx, pos[0])
        dy = self.winSz[1] - self.imgSz[1] * self.__scale
        if dy >= 0:
            py = int(dy / 2)
        else:
            if pos[1] >= 0:
                py = 0
            else:
                py = max(dy, pos[1])
        return (px, py)
        
    def __isZoomed(self):
        return self.__scale != self.__minScale
        
    def isScaled(self):
        return self.__scale != 1.0
    
    def getBltPos(self):
        if self.__isMoving:
            return self.__tmpBltPos
        return self.__bltPos
    
    def getNewImgSize(self):
        return (int(self.imgSz[0] * self.__scale), int(self.imgSz[1] * self.__scale))
    
class PlayCtrl:
    def __init__(self, playList, recordDict):
        self.__playList = playList
        self.__recordDict = recordDict
        self.__curPlayId = 0
        self.__loopPlay = False
        self.__preDelIndex = None
    
    def getLoopPlay(self):
        return self.__loopPlay
               
    def changeLoopPlay(self):
        self.__loopPlay = not self.__loopPlay
        
    def prepareDelete(self):
        self.__preDelIndex = self.__curPlayId
        
    def markStar(self, star):
        if star not in [1, 2, 3, 4, 5]:
            return
        curFn = self.getCurrent()
        if curFn == None:
            return
        if curFn in self.__recordDict:
            self.__recordDict[curFn] = star
        else:
            self.__recordDict.setdefault(curFn, star)
            
    def __verifyId(self, id):
        plen = len(self.__playList)
        if plen == 0:
            return 0
        if self.__loopPlay:
            if id < 0:
                id += plen
                while id < 0:
                    id += plen
            elif id >= plen:
                id -= plen
                while id >= plen:
                    id -= plen
        else:
            if id < 0:
                id = 0
            elif id >= plen:
                id = plen - 1
        return id
    
    def __modifyId(self, offset):
        id = self.__curPlayId + offset
        id = self.__verifyId(id)
        if id == self.__curPlayId and not self.__loopPlay:
            return False
        self.__curPlayId = id
        return True
            
    def MoveNext(self):
        return self.__modifyId(1)
    
    def MovePrev(self):
        return self.__modifyId(-1)
    
    def getCurrent(self):
        if len(self.__playList) == 0:
            return None
        return self.__playList[self.__curPlayId]
    
    def getOffset(self, offset):
        if len(self.__playList) == 0:
            return None
        id = self.__curPlayId + offset
        id = self.__verifyId(id)
        if not self.__loopPlay and id != self.__curPlayId + offset:
            return None
        return self.__playList[id]
    
    def procEnter(self):
        if self.__preDelIndex == self.__curPlayId:
            self.removeCur()
        self.__preDelIndex = None
    
    def removeCur(self):
        fn = self.getCurrent()
        try:
            os.remove(fn)
        except:
            pass
        if fn in self.__recordDict:
            self.__recordDict.pop(fn)
        self.__playList.pop(self.__curPlayId)
        self.__curPlayId = self.__verifyId(self.__curPlayId)
        
class ViewCtrlOne:
    level_text_map = {
                      1 : 'set level 111111',
                      2 : 'set level 222222',
                      3 : 'set level 333333',
                      4 : 'set level 444444',
                      5 : 'set level 555555',
                      }
    
    def __init__(self, playCtrl, textCtrl, winSz):
        self.__playCtrl = playCtrl
        self.__textCtrl = textCtrl
        self.__transCtrl = None
        self.__needUpdate = False
        self.__bkImg = None
        self.__bkBlt = None
        self.__winSz = winSz
        self.__autoPlay = False
        self.__autoInterver = 1000
        self.__lastTick = 0
        self.__loadCurrent()
        
    def __handleAutoPlay(self):
        if not self.__autoPlay:
            return
        curTick = pygame.time.get_ticks()
        if self.__lastTick == 0:
            self.__lastTick = curTick
            return
        if curTick - self.__lastTick > self.__autoInterver:
            self.__playNext()
            self.__lastTick = curTick
        
    def tick(self):
        self.__handleAutoPlay()
        return self.__needUpdate
        
    def update(self, sur):
        if self.__bkBlt == None or self.__transCtrl == None:
            return
        sur.blit(self.__bkBlt, self.__transCtrl.getBltPos())
        self.__needUpdate = False    
    
    def __loadImg(self, fn):
        try:
            self.__bkImg = pygame.image.load(fn)
        except:
            return False
        self.__transCtrl = TransfromCtrl(self.__winSz, self.__bkImg.get_size())
        self.__transCtrl.adjustCenter()
        if self.__transCtrl.isScaled():
            self.__bkBlt = pygame.transform.smoothscale(self.__bkImg, self.__transCtrl.getNewImgSize())
        else:
            self.__bkBlt = self.__bkImg
        return True
        
    def __loadCurrent(self):
        while True:
            fn = self.__playCtrl.getCurrent()
            if fn == None:
                self.__textCtrl.setOutputText('play list is empty')
                return
            if self.__loadImg(fn):
                break
            else:
                self.__playCtrl.removeCur()
        self.__needUpdate = True
        self.__textCtrl.clearText()
        
    def __playNext(self):
        ret = self.__playCtrl.MoveNext()
        if not ret:
            self.__textCtrl.setOutputText('no more image')
        else:
            self.__loadCurrent()
            
    def __playPrev(self):
        ret = self.__playCtrl.MovePrev()
        if not ret:
            self.__textCtrl.setOutputText('no more image')
        else:
            self.__loadCurrent()
            
    def procWinSzChange(self, winSz):
        self.__winSz = winSz
        self.__loadCurrent()
            
    def procLeft(self):
        self.__playPrev()
    
    def procRight(self):
        self.__playNext()
            
    def procAuto(self):
        self.__autoPlay = not self.__autoPlay
        if self.__autoPlay:
            self.__textCtrl.setOutputText('auto play %d ms' % self.__autoInterver)
        else:
            self.__textCtrl.setOutputText('disable auto play')
            
    def __procAutoCh(self, f):
        if self.__autoPlay == False:
            self.__textCtrl.setOutputText('auto play is disable')
            return
        val = int(self.__autoInterver * f)
        self.__autoInterver = clamp(val, 100, 10000)
        self.__lastTick = 0
        self.__textCtrl.setOutputText('auto play %d ms' % self.__autoInterver)
            
    def procAutoInc(self):
        self.__procAutoCh(1.1)
        
    def procAutoDec(self):
        self.__procAutoCh(0.9)
       
    def getFuncSetLevel(self, v):
        if v not in [1,2,3,4,5]:
            return None
        def __inProc():
            self.__playCtrl.markStar(v)
            self.__textCtrl.setOutputText(ViewCtrlOne.level_text_map[v])
        return __inProc
    
    def reload(self):
        self.__loadCurrent()
        
    def procMouseDown(self, e):
        if self.__transCtrl == None:
            return
        needUpdate = False
        if e.button == 1:
            self.__transCtrl.startMove(e.pos)
        elif e.button == 3:
            self.__playNext()
        elif e.button == 4:
            if pygame.mouse.get_pressed()[2]:
                self.__playPrev()
            else:
                needUpdate = self.__transCtrl.zoomIn(e.pos)
        elif e.button == 5:
            if pygame.mouse.get_pressed()[2]:
                self.__playNext()
            else:
                needUpdate = self.__transCtrl.zoomOut(e.pos)
        if needUpdate:
            self.__needUpdate = needUpdate
            self.__bkBlt = pygame.transform.smoothscale(self.__bkImg, self.__transCtrl.getNewImgSize())
    
    def procMouseUp(self, e):
        if self.__transCtrl == None:
            return
        if e.button == 1:
            self.__transCtrl.endMove(e.pos)
            self.__needUpdate = True
    
    def procMouseMove(self, e):
        if e.buttons[0] == False:
            return
        if self.__transCtrl == None:
            return
        self.__transCtrl.Moving(e.pos)
        self.__needUpdate = True
        
class LoadResult:
    def __init__(self, sur):
        self.sur = sur
        self.firstW = 0
        self.isLoadOk = False
        
    def reset(self):
        self.isLoadOk = False
        
class SurLoader:
    JOB_NONE = 0
    JOB_LOAD_NEXT = 1
    JOB_LOAD_CUR = 2
    
    def __init__(self, playCtrl, winSz):
        self.__playCtrl = playCtrl
        self.__winSz = winSz
        self.__imgSurList = []
        self.__surBlt = pygame.Surface((self.__winSz[0] * 2, self.__winSz[1]))
        self.__workLock = thread.allocate_lock()
        self.__runningLock = thread.allocate_lock()
        self.__runningFlag = True
        self.__workThread = thread.start_new(self.__threadProc, (self.__workLock,))
        self.__isLoadOk = False
        self.__jobFlag = SurLoader.JOB_NONE
        
    def stop(self):
        self.__runningFlag = False
        self.__runningLock.acquire()
        self.__runningLock.release()
        
    def __loadImgSur(self, fn):
        try:
            sur = pygame.image.load(fn)
        except:
            return None
        imgSz = sur.get_size()
        newImgW = float(imgSz[0]) * self.__winSz[1] / imgSz[1]
        sur = pygame.transform.smoothscale(sur, (int(newImgW), self.__winSz[1]))
        return sur
    
    def __loopLoadCur(self):
        while True:
            fn = self.__playCtrl.getCurrent()
            if fn == None:
                return None
            sur = self.__loadImgSur(fn)
            if sur == None:
                self.__playCtrl.removeCur()
            break
        return sur
    
    def __loopLoadOffset(self, offset):
        while True:
            fn = self.__playCtrl.getOffset(offset)
            if fn == None:
                return (None, offset)
            sur = self.__loadImgSur(fn)
            if sur == None:
                offset += 1
            break
        return (sur, offset)
    
    def __loadBltSur(self):
        bltX = 0
        if len(self.__imgSurList) != 0:
            for sur in self.__imgSurList:
                self.__surBlt.blit(sur, (bltX, 0))
                bltX += sur.get_size()[0]
        else:
            sur = self.__loopLoadCur()
            if None == sur:
                return False
            self.__surBlt.blit(sur, (bltX, 0))
            bltX += sur.get_size()[0]
            self.__imgSurList.append(sur)
        
        firstImgW = self.__imgSurList[0].get_size()[0]
        bltXRight = firstImgW + self.__winSz[0]
        offset = len(self.__imgSurList)
        while bltX < bltXRight:
            sur, offset = self.__loopLoadOffset(offset)
            if sur == None:
                return False
            self.__surBlt.blit(sur, (bltX, 0))
            bltX += sur.get_size()[0]
            self.__imgSurList.append(sur)
            offset += 1
        return True
        
    def __threadProc(self, param):
        self.__runningLock.acquire()
        while self.__runningFlag:
            if self.__jobFlag == SurLoader.JOB_NONE:
                sleep(0.01)
                continue
            if self.__jobFlag == SurLoader.JOB_LOAD_NEXT:
                if not self.__workLock.acquire(1) : continue
                self.__playCtrl.MoveNext()
                self.__imgSurList = self.__imgSurList[1:]
                self.__isLoadOk = self.__loadBltSur()
                self.__jobFlag = SurLoader.JOB_NONE
                self.__workLock.release()
            elif self.__jobFlag == SurLoader.JOB_LOAD_CUR:
                if not self.__workLock.acquire(1) : continue
                self.__isLoadOk = self.__loadBltSur()
                self.__jobFlag = SurLoader.JOB_NONE
                self.__workLock.release()
        self.__runningLock.release()
        
    def startLoadNextJob(self):
        isWorking = self.__workLock.locked()
        if isWorking:
            return False
        self.__jobFlag = SurLoader.JOB_LOAD_NEXT
        return True
    
    def startLoadCurJob(self):
        isWorking = self.__workLock.locked()
        if isWorking:
            return False
        self.__jobFlag = SurLoader.JOB_LOAD_CUR
        return True
    
    def getJobResult(self, result):
        if self.__jobFlag != SurLoader.JOB_NONE:
            return False
        if not self.__workLock.acquire(0):
            return False
        if self.__isLoadOk:
            result.sur.blit(self.__surBlt, (0, 0))
            result.firstW = self.__imgSurList[0].get_size()[0]
            result.isLoadOk = True
        else:
            result.isLoadOk = False
        self.__workLock.release()
        return True
    
class ViewCtrlTwo:
    level_text_map = {
                      1 : 'set level 111111',
                      2 : 'set level 222222',
                      3 : 'set level 333333',
                      4 : 'set level 444444',
                      5 : 'set level 555555',
                      }
    
    PLAY_STATE_STOP = 1
    PLAY_STATE_START = 2
    PLAY_STATE_PAUSE = 3
    PLAY_STATE_ENDING = 4
    
    LOADER_STATE_READY = 0
    LOADER_STATE_CREATING_JOB = 1
    LOADER_STATE_WORKING = 2
    
    JOB_LOAD_NEXT = 1
    JOB_LOAD_CUR = 2
    
    def __init__(self, playCtrl, textCtrl, winSz):
        self.__textCtrl = textCtrl
        self.__needUpdate = False
        self.__playFSM = ViewCtrlTwo.PLAY_STATE_STOP
        self.__imgW = 0
        self.__curImgX = 0
        self.__stepLen = 1
        self.__interval = 10
        self.__lastTick = 0
        self.__surBlt = pygame.Surface((winSz[0] * 2, winSz[1]))
        self.__surLoader = SurLoader(playCtrl, winSz)
        self.__loaderFsm = ViewCtrlTwo.LOADER_STATE_READY
        self.__eventList = []
        self.__eventParam = []
        self.__loadResult = LoadResult(self.__surBlt)
        self.__loaderFsmEventLoadCur()
        
    def cleanUp(self):
        self.__surLoader.stop()
        
    def __loaderFsmEventLoadNext(self):
        if ViewCtrlTwo.JOB_LOAD_NEXT in self.__eventList:
            return
        self.__eventList.append(ViewCtrlTwo.JOB_LOAD_NEXT)
        self.__eventParam.append({'isAuto':True})
        
    def __loaderFsmEventJumpToNext(self):
        self.__eventList.append(ViewCtrlTwo.JOB_LOAD_NEXT)
        self.__eventParam.append({'isAuto':False})
        
    def __loaderFsmEventLoadCur(self):
        self.__eventList.append(ViewCtrlTwo.JOB_LOAD_CUR)
        self.__eventParam.append(None)
        
    def __loaderFsmTick(self):
        if self.__loaderFsm == ViewCtrlTwo.LOADER_STATE_READY:
            if len(self.__eventList) == 0:
                return
            self.__loaderFsmProcHeaderJob()   
        elif self.__loaderFsm == ViewCtrlTwo.LOADER_STATE_CREATING_JOB:
            self.__loaderFsmProcHeaderJob() 
        elif self.__loaderFsm == ViewCtrlTwo.LOADER_STATE_WORKING:
            self.__loaderFsmProcWaitResult()
            
    def __loaderFsmProcWaitResult(self):
        ret = self.__surLoader.getJobResult(self.__loadResult)
        if ret:
            if not self.__loadResult.isLoadOk:
                self.__textCtrl.setOutputText('no more image')
                self.__fsmLoadFail(self.__eventList[0], self.__eventParam[0])
            else:
                self.__fsmLoadDone(self.__eventList[0], self.__eventParam[0])
            self.__loaderFsm = ViewCtrlTwo.LOADER_STATE_READY
            self.__eventList = self.__eventList[1:]
            self.__eventParam = self.__eventParam[1:]
        
            
    def __loaderFsmProcHeaderJob(self):
        event = self.__eventList[0]
        if event == ViewCtrlTwo.JOB_LOAD_NEXT:
            ret = self.__surLoader.startLoadNextJob()
        elif event == ViewCtrlTwo.JOB_LOAD_CUR:
            ret = self.__surLoader.startLoadCurJob()
            
        if ret:
            self.__loaderFsm = ViewCtrlTwo.LOADER_STATE_WORKING
            self.__loadResult.reset()
        else:
            self.__loaderFsm = ViewCtrlTwo.LOADER_STATE_CREATING_JOB
                
    def __fsmLoadFail(self, e, p):
        if self.__playFSM == ViewCtrlTwo.PLAY_STATE_START:
            self.__playFSM = ViewCtrlTwo.PLAY_STATE_ENDING
            
    def __fsmLoadDone(self, e, p):
        if self.__playFSM == ViewCtrlTwo.PLAY_STATE_STOP:
            self.__playFSM = ViewCtrlTwo.PLAY_STATE_START
        if ViewCtrlTwo.JOB_LOAD_NEXT == e:
            if p['isAuto']:
                self.__curImgX -= self.__imgW
            else:
                self.__curImgX = 0
            self.__imgW = self.__loadResult.firstW
        elif ViewCtrlTwo.JOB_LOAD_CUR == e:
            self.__curImgX = 0
            self.__imgW = self.__loadResult.firstW
            
    def __fsmEndTick(self):
        if self.__curImgX > self.__imgW:
            self.__playFSM = ViewCtrlTwo.PLAY_STATE_STOP
            
    def __delay(self):
        if pygame.time.get_ticks() - self.__lastTick < self.__interval:
            return True
        self.__lastTick = pygame.time.get_ticks()
        return False
        
    def tick(self):
        self.__loaderFsmTick()
        if self.__delay():
            return self.__needUpdate
        if self.__playFSM == ViewCtrlTwo.PLAY_STATE_PAUSE:
            return self.__needUpdate
        if self.__playFSM == ViewCtrlTwo.PLAY_STATE_STOP:
            return self.__needUpdate
        if self.__playFSM == ViewCtrlTwo.PLAY_STATE_START:
            self.__curImgX += self.__stepLen
            if self.__curImgX > self.__imgW:
                self.__loaderFsmEventLoadNext()
            self.__needUpdate = True
            return True
        if self.__playFSM == ViewCtrlTwo.PLAY_STATE_ENDING:
            self.__fsmEndTick()
            return True
    
    def update(self, sur):
        sur.blit(self.__surBlt, (-self.__curImgX, 0))
        self.__needUpdate = False    
        
    def procWinSzChange(self, winSz):
        pass
        
    def getFuncSetLevel(self, v):
        if v not in [1,2,3,4,5]:
            return None
        def __inProc():
            self.__playCtrl.markStar(v)
            self.__textCtrl.setOutputText(ViewCtrlOne.level_text_map[v])
        return __inProc
    
    def procMouseDown(self, e):
        pass
    
    def procMouseUp(self, e):
        pass
    
    def procMouseMove(self, e):
        pass
    
    def procLeft(self):
        self.__loaderFsmEventLoadCur()
    
    def procRight(self):
        self.__loaderFsmEventJumpToNext()
    
class TextCtrl:
    def __init__(self):
        pygame.font.init()
        fontName = pygame.font.get_default_font()
        self.__font = pygame.font.SysFont(fontName, 36)
        self.__textSur = None
        self.__textPos = (10, 10)
        self.__textColor = (180,10,200)
        self.__needUpdate = False
        
    def tick(self):
        return self.__needUpdate
        
    def setOutputText(self, s):
        self.__textSur = self.__font.render(s, 0, self.__textColor)
        self.__needUpdate = True
        
    def updateText(self, sur):
        if self.__textSur == None:
            return
        sur.blit(self.__textSur, self.__textPos)
        self.__needUpdate = False
        
    def clearText(self):
        self.__textSur = None
        self.__needUpdate = True
        
class MainWindow:
    def __init__(self, playContext):
        pygame.init()
        self.__winInitSize = (1024, 768)
        self.__isFullScreen = False
        self.__isRunning = True
        self.__initWindow()
        self.__initEventMap()
        self.__textCtrl = TextCtrl()
        self.__playCtrl = PlayCtrl(playContext['playList'], playContext['recorder'])
        self.__viewCtrl = None
        self.__mode = None
        self.__setMode('mode1')
        self.__lastTick = 0
        
    def __initWindow(self):
        if self.__isFullScreen:
            self.__win = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
        else:
            self.__win = pygame.display.set_mode(self.__winInitSize)
        
    def __initEventMap(self):
        keyMap = {
                  pygame.K_ESCAPE : self.__procExit,
                  pygame.K_KP_PLUS : self.__procSwitchFullScreen,
                  pygame.K_KP_ENTER : self.__procEnter,
                  pygame.K_RETURN : self.__procEnter,
                  pygame.K_DELETE : self.__procDelete,
                  pygame.K_KP_PERIOD : self.__procDelete,
                  pygame.K_KP8 : self.__procLoop,
                  pygame.K_KP_DIVIDE : self.__procSwitchMode,
                  }
        
        self.__keyMap = keyMap
        
    def __setKeyMap(self, mode):
        if mode == 'mode1':
            keyMap = {
                      pygame.K_LEFT : self.__viewCtrl.procLeft,
                      pygame.K_RIGHT : self.__viewCtrl.procRight,
                      pygame.K_KP0 : self.__viewCtrl.procAuto,
                      pygame.K_UP : self.__viewCtrl.procAutoInc,
                      pygame.K_DOWN : self.__viewCtrl.procAutoDec,
                      pygame.K_KP1 : self.__viewCtrl.getFuncSetLevel(1),
                      pygame.K_KP2 : self.__viewCtrl.getFuncSetLevel(2),
                      pygame.K_KP3 : self.__viewCtrl.getFuncSetLevel(3),
                      pygame.K_KP4 : self.__viewCtrl.getFuncSetLevel(4),
                      pygame.K_KP5 : self.__viewCtrl.getFuncSetLevel(5),
                      }
            self.__keyMap.update(keyMap)
        elif mode == 'mode2':
            keyMap = {
                      pygame.K_LEFT : self.__viewCtrl.procLeft,
                      pygame.K_RIGHT : self.__viewCtrl.procRight,
                      pygame.K_KP1 : self.__viewCtrl.getFuncSetLevel(1),
                      pygame.K_KP2 : self.__viewCtrl.getFuncSetLevel(2),
                      pygame.K_KP3 : self.__viewCtrl.getFuncSetLevel(3),
                      pygame.K_KP4 : self.__viewCtrl.getFuncSetLevel(4),
                      pygame.K_KP5 : self.__viewCtrl.getFuncSetLevel(5),
                      }
            self.__keyMap.update(keyMap)
            
    def __cleanViewCtrl(self):
        if self.__viewCtrl != None and self.__mode == 'mode2':
            self.__viewCtrl.cleanUp()
    
    def __setMode(self, mode):
        if mode not in ['mode1', 'mode2']:
            return
        if self.__mode == mode:
            return
        self.__cleanViewCtrl()
        self.__mode = mode
        if mode == 'mode1':
            self.__viewCtrl = ViewCtrlOne(self.__playCtrl, self.__textCtrl, self.__win.get_size())
        elif mode == 'mode2':
            self.__viewCtrl = ViewCtrlTwo(self.__playCtrl, self.__textCtrl, self.__win.get_size())
        self.__setKeyMap(mode)
    
    def run(self):
        while self.__isRunning:
            for e in pygame.event.get():
                if e.type == pygame.QUIT :
                    self.__isRunning = False
                elif e.type == pygame.KEYDOWN:
                    self.__keyProc(e.key)
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.__viewCtrl.procMouseDown(e)
                elif e.type == pygame.MOUSEBUTTONUP:
                    self.__viewCtrl.procMouseUp(e)
                elif e.type == pygame.MOUSEMOTION:
                    self.__viewCtrl.procMouseMove(e)        
            
            needUpdate = self.__viewCtrl.tick()
            needUpdate = needUpdate or self.__textCtrl.tick()
            if needUpdate:
                self.__win.fill((0,0,0))
                self.__viewCtrl.update(self.__win)
                self.__textCtrl.updateText(self.__win)
                pygame.display.flip() 
            
            curTick = pygame.time.get_ticks()
            dx = curTick - self.__lastTick
            if dx < 10:
                pygame.time.delay(10 - dx)
                self.__lastTick = curTick
        self.__cleanViewCtrl()
            
    def __procExit(self):
        self.__isRunning = False
        
    def __procSwitchMode(self):
        if self.__mode == 'mode1':
            self.__setMode('mode2')
        elif self.__mode == 'mode2':
            self.__setMode('mode1')
    
    def __procSwitchFullScreen(self):
        self.__isFullScreen = not self.__isFullScreen
        self.__initWindow()
        self.__viewCtrl.procWinSzChange(self.__win.get_size())
        
    def __procLoop(self):
        self.__playCtrl.changeLoopPlay()
        if self.__playCtrl.getLoopPlay():
            self.__textCtrl.setOutputText('loop play enable')
        else:
            self.__textCtrl.setOutputText('loop play disable')
        
    def __procDelete(self):
        self.__playCtrl.prepareDelete()
        self.__textCtrl.setOutputText('press enter to delete')
    
    def __procEnter(self):
        self.__playCtrl.procEnter()
        self.__viewCtrl.reload()
            
    def __keyProc(self, k):
        if k in self.__keyMap:
            procFunc = self.__keyMap[k]
            procFunc()
        
