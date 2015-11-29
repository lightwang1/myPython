#coding:gb2312
'''
Created on 2013-6-8

@author: Administrator
'''
import numpy
import random

def __getstrArea(area):
    ret = ""
    for line in area:
        ret += __getstrLine(line) + "\n"
    ret += "---------------------------\n"
    return ret

def __getstrLine(line):
    sl = [str(i) for i in line]
    return "[" + ", ".join(sl) + "]"

def __initGlobal():
    global result
    global able
    global allset
    area = [[0] * 9 for i in range(9)]
    able = [[None] * 9 for i in range(9)]
    result = numpy.array(area)
    allset = set([i for i in range(10)])

def __getBlock(x, y, data):
    xs = x / 3 * 3
    ys = y / 3 * 3
    return data[ys:(ys+3), xs:(xs+3)]
  
def __getAvailable(x, y):
    used = set()
    for v in result[y, :]:
        used.add(v)
    for v in result[:, x]:
        used.add(v)
    for li in __getBlock(x, y, result):
        for v in li:
            used.add(v)
    return allset - used

def __getPos(cid):
    return (cid % 9, cid / 9)

def __removeCur(cid):
    """
        返回集合是否为空
    """
    x, y = __getPos(cid)
    result[y][x] = 0
    return len(able[y][x]) == 0

def __moveBack(cid):
    while True:
        cid -= 1
        if cid < 0 or not __removeCur(cid): 
            break
    return cid

def __rands(s):
    r = random.randint(0, len(s))
    return s[r]

def __popRand(s):
    l = list(s)
    ret = random.choice(l)
    s.remove(ret)
    return ret

def __checkLine(line):
    state = [-1] * 10
    ret = set()
    for i in range(9):
        val = line[i]
        if val == 0: continue
        if state[val] != -1:
            ret.add(state[val])
            ret.add(i)
        state[val] = i
    return ret   

def __getLineInBlk(data, xs, ys):
    ret = []
    for y in [0, 1, 2]:
        for x in [0, 1, 2]:
            ret.append(data[ys+y][xs+x])
    return ret

def checkError(data):
    ret = set()
    for y in range(9):
        line = data[y]
        for i in __checkLine(line):
            ret.add((i, y))
    for x in range(9):
        line = data[:, x]
        for i in __checkLine(line):
            ret.add((x, i))
    for blk in range(9):
        xs = blk % 3 * 3
        ys = blk / 3 * 3
        line = __getLineInBlk(data, xs, ys)
        for i in __checkLine(line):
            ret.add((i%3 + xs, i/3 + ys))
    return ret    

def getSameVal(x, y, data, val):
    ret = []
    row = data[y, :]
    for id, v in enumerate(row):
        if v == val:
            ret.append((id, y))
    col = data[:, x]
    for id, v in enumerate(col):
        if v == val:
            ret.append((x, id))
    xs = x / 3 * 3
    ys = y / 3 * 3
    for yi in range(3):
        for xi in range(3):
            if data[ys+yi][xs+xi] == val:
                ret.append(xs+xi, ys+yi)
    return ret

def getit():
    __initGlobal()
    cid = 0
    while cid >= 0:
        x, y = __getPos(cid)
        av = __getAvailable(x, y)
        if len(av) == 0:
            cid = __moveBack(cid)
            x, y = __getPos(cid)
        else:
            able[y][x] = av
        result[y][x] = __popRand(able[y][x])
        if cid == 80: #end
            yield result
            __removeCur(cid)
            cid = __moveBack(cid)
            x, y = __getPos(cid)
            result[y][x] = __popRand(able[y][x])
        cid += 1

def getSingle():
    __initGlobal()
    cid = 0
    while cid >= 0:
        x, y = __getPos(cid)
        av = __getAvailable(x, y)
        if len(av) == 0:
            cid = __moveBack(cid)
            x, y = __getPos(cid)
        else:
            able[y][x] = av
        result[y][x] = __popRand(able[y][x])
        if cid == 80: #end
            return result
        cid += 1

#######################################################################
#test
def testCheckLine():
    line = [random.randint(1,9) for i in range(9)]
    print("line is", line)
    ret = __checkLine(line)
    print("ret is", ret)
    
def testCheckError():
    data = getSingle()
    data[1][1] = data[1][2]
    
    print(__getstrArea(data))
    print("result")
    print(checkError(data))
    
def alltest():
    testCheckLine()
    testCheckError()
    
def main():
    gen = getit()
    with open("ret.txt", "w") as f:
        i = 0
        for ret in gen:
            strret = __getstrArea(ret)
            f.write(strret)
            i += 1
            print('bilid %d' % i)
            if i == 50000 : break
    print("done")

##init
result = None
able = None
allset = None
 
if __name__ == "__main__":
    main()
    #alltest()
