#coding=gb2312
'''
Created on 2013-6-8

@author: Administrator
'''

import Tkinter
import tkMessageBox
import tkFont
import sd
import random

class cell():
    _font = None
    def __init__(self, l, t, r, b, cv):
        self.x = (l + r) / 2.0
        self.y = (t + b) / 2.0
        self.cv = cv
        self.id = 0
        self.fixed = False
        self.isError = False
        self.__num = 0
        
    def changeNum(self, num):
        self.__num = num
        self.__redrawText()
          
    def getNum(self):
        return self.__num
    
    def isDone(self):
        return not self.isError and self.__num != 0
    
    def __redrawText(self):
        if self.id != 0 :
            self.cv.delete(self.id)
            self.id = 0
        if self.__num == 0 : return
        if self.isError : cl = "red"
        elif self.fixed : cl = "blue"
        else : cl = "black"
        self.id = self.cv.create_text(self.x, self.y, text = "%d" % self.__num, 
                                      font = cell._font, fill = cl)
    
    def setFixed(self):
        self.fixed = True
        self.__redrawText()
        
    def setError(self):
        self.isError = True
        self.__redrawText()
        
    def clearError(self):
        if self.isError:
            self.isError = False
            self.__redrawText()
        
    def clean(self):
        self.__num = 0
        self.fixed = False
        self.isError = False
        self.__redrawText()
        
class sdFrm(Tkinter.Frame):
    keymap = {87:1, 88:2, 89:3, 83:4, 84:5, 85:6, 79:7, 80:8, 81:9,
              49:1, 50:2, 51:3, 52:4, 53:5, 54:6, 55:7, 56:8, 57:9,
              32:0}
    def __init__(self, master, **kw):
        Tkinter.Frame.__init__(self, master, **kw)
        self.size = (450, 450)
        self.cposx = self.cposy = 0
        self.isStart = False
        self.setLevel(1)
        
        cv = Tkinter.Canvas(self, width="450", height="450")
        cv.pack()
        self.__addGraph(cv)
        cv.bind("<Motion>", self.__moveOnCv)
        self.bind("<Key>", self.__keyOnCv)
        self.focus_force()
       
    def __moveOnCv(self, event):
        self.cposx = (event.x - self.st) / self.wsp
        self.cposy = (event.y - self.st) / self.hsp
        
    def __getCurCell(self):
        return self.cells[self.cposy][self.cposx]
    
    def __getCellById(self, x, y):
        return self.cells[y][x]
    
    def __checkError(self):
        for line in self.cells:
            for c in line:
                c.clearError()
        errors = sd.checkError(self.data)
        for x, y in errors:
            self.cells[y][x].setError()
    
    def __checkDone(self):
        for line in self.cells:
            for c in line:
                if not c.isDone():
                    return False
        return True
                        
    def __keyOnCv(self, event):
        if not self.isStart : return
        curcell = self.__getCurCell()
        if curcell.fixed : return
        if event.keycode in sdFrm.keymap:
            kval = sdFrm.keymap[event.keycode]
            curcell.changeNum(kval)
            self.data[self.cposy][self.cposx] = kval
            self.__checkError()
            if self.__checkDone():
                self.isStart = False
                tkMessageBox.showinfo(u"搞定", u"搞定了,尝试下更高级别的吧")
      
    def __addGraph(self, cv):
        w = h = 442
        wsp = w / 9
        hsp = h / 9
        st = 4
        self.wsp = wsp
        self.hsp = hsp
        self.st = st
        
        for i in range(10):
            if i % 3 == 0 : lw = 4
            else : lw = 2
            if i == 0 or i == 9:
                cl = "red"
                lw = 4 
            else : cl = "black"
            cv.create_line(0+st, i*hsp+st, w+st, i*hsp+st, width=lw, fill=cl)
            cv.create_line(i*wsp+st, 0+st, i*wsp+st, h+st, width=lw, fill=cl)
         
        self.cells = []   
        for y in range(9):
            line = []
            t = y * hsp + st
            b = (y+1) * hsp + st
            for x in range(9):
                l = x * wsp + st
                r = (x+1) * wsp + st
                line.append(cell(l,t,r,b, cv))
            self.cells.append(line)
    
    def __randBool(self):
        return random.random() < self.seed
    
    def newGame(self):
        self.isStart = True
        for line in self.cells:
            for c in line:
                c.clean()
        
        self.data = sd.getSingle()
        for y in range(9):
            for x in range(9):
                if self.__randBool():
                    self.cells[y][x].setFixed()
                    self.cells[y][x].changeNum(self.data[y][x])
                else:
                    self.data[y][x] = 0
    
    def setLevel(self, level):
        self.seed = (8 - level / 2.0) / 10.0
    
def Cmd_NewGame(sdfrm):
    def _execute():
        sdfrm.newGame()
    return _execute

def Cmd_Level(sdfrm, level, lbBtn):
    def _execute():
        sdfrm.setLevel(level)
        lbBtn["text"] = u"级别%d" % level
        sdfrm.newGame()
    return _execute
          
def main():
    root = Tkinter.Tk()
    root.title(u"数独")
    root.geometry("450x500+500+100")
    root.resizable(False, False)
    
    cell._font = tkFont.Font(size="32", weight="bold")
    
    sdf = sdFrm(root)
    sdf.pack(side="bottom")
    
    topfrm = Tkinter.Frame(root, width = "450", height = "50")
    topfrm.pack(side = "left")
    
    lbLevel = Tkinter.Menubutton(topfrm, text=u"级别1", direction="below")
    mLevel = Tkinter.Menu(lbLevel)
    for i in range(1,9):
        cmd = Cmd_Level(sdf, i, lbLevel)
        mLevel.add_command(label=u"级别%d"%i, command=cmd)
    lbLevel["menu"] = lbLevel.menu = mLevel
    lbLevel.pack(side="left")
    
    cmd_NewGame = Cmd_NewGame(sdf)
    Tkinter.Button(topfrm, text="new game", command=cmd_NewGame).pack(side="left")
    
    sdf.newGame()
    
    root.mainloop()

if __name__ == '__main__':
    main()
