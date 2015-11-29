#coding:utf8
'''
Created on 2015-9-3

@author: Administrator
'''
import os.path
import pickle
from viewWindow import createPlayContext, MainWindow
import random

DUMP_FILE_PATH = 'E:\\app_data\\picView\\pro_mtl.rep'
SCAN_DIR = 'F:\\url_pic_center\\meitulu'
#SCAN_DIR = 'F:\\url_pic_center\\meitulu_test'
FILTER_TYPE = [0]
EXT_NAME_LIST = ['.jpg']
   
def scanDir(repDict, hasLevel0 = True):
    if not os.path.exists(SCAN_DIR):
        return []
    retDict = {}
    if hasLevel0:
        for dir, _, files in os.walk(SCAN_DIR):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext.lower() in EXT_NAME_LIST:
                    fn = os.path.join(dir, file)
                    if fn in repDict:
                        level = repDict[fn]
                    else:
                        level = 0
                    retDict.setdefault(fn, level)
    else:
        for dir, _, files in os.walk(SCAN_DIR):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext.lower() in EXT_NAME_LIST:
                    fn = os.path.join(dir, file)
                    if fn in repDict:
                        level = repDict[fn]
                        retDict.setdefault(fn, level)
    return retDict

def filterItem(toPlayDict):
    ret = []
    for k in toPlayDict:
        if toPlayDict[k] in FILTER_TYPE:
            ret.append(k)
    random.shuffle(ret)
    return ret

def play(repObj, itemList):
    if len(itemList) == 0:
        print 'no file to play'
        return
    print 'play count %d' % len(itemList)
    playContext = createPlayContext(repObj, itemList)
    if None == playContext:
        print 'create play context failed'
        return
    MainWindow(playContext).run()

def saveRep(repObj):
    with open(DUMP_FILE_PATH, 'w') as fw:
        pickle.dump(repObj, fw)
    
def loadRep():
    if not os.path.exists(DUMP_FILE_PATH):
        return {}
    with open(DUMP_FILE_PATH, 'r') as fr:
        repObj = pickle.load(fr)
    return repObj
        
def main():
    repObj = loadRep()
    hasLevel0 = False
    if 0 in FILTER_TYPE:
        hasLevel0 = True
    toPlayDict = scanDir(repObj, hasLevel0)
    playList = filterItem(toPlayDict)
    play(repObj, playList)
    saveRep(repObj)
    
if __name__ == '__main__':
    main()