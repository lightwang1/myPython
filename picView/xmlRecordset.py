#coding:utf8
'''
Created on 2015-9-20

@author: Administrator
'''
from xml.etree.ElementTree import * 
import os.path

class XmlRecordset():
    def __init__(self):
        self.__doc = None
        self.__savePath = None
        
    def open(self, path):
        if not os.path.exists(path):
            self.__createNew()
        else:
            self.__doc = ElementTree(path)
        self.__savePath = path
    
    def save(self, path = None):
        savePath = path or self.__savePath
        if None == savePath:
            return False
        self.__doc.write(self.__savePath, encoding = 'utf-8')
    
    def __createNew(self):
        root = Element(u'photoAlbums')
        doc = ElementTree(root)
        self.__doc = doc
        
    def getAlbumNode(self, path):
        def _getNode(albumsNode):
            if albumsNode == None:
                return None
            for albumNode in albumsNode:
                tmpPath = albumNode.attrib['path']
                if path == tmpPath:
                    return albumNode
                if len(path) > len(tmpPath):
                    if path.startswith(tmpPath):
                        subAlbumsNode = albumNode.find('subAlbums')
                        return _getNode(subAlbumsNode)
                
            return None
        
        ret = _getNode(self.__doc.getroot())
        return ret
    
class PhotoAlbum:
    def __init__(self, path):
        self.__fullPath = path
        self.__subAlbumList = []
        self.__defaultInfo  = None
        self.__photoList = []
        self.__isEnable = True
        
    def fromXmlElement(self, elem):
        subAlbumsNode = elem.find('subAlbums')
        if None == subAlbumsNode:
            return False
        subAlbumList = []
        for albumNode in subAlbumsNode:
            album = PhotoAlbum(albumNode.attrib['path'])
            if False == album.fromXmlElement(albumNode):
                print 'read sub PhotoAlbum error'
                return False
            subAlbumList.append(album)
        
        defaultInfoNode = elem.find('defaultInfo')
        if None == defaultInfoNode:
            return False
        defaultInfo = PhotoInfo()
        if False == defaultInfo.fromXmlElement(defaultInfoNode):
            return False
        
        photosNode = elem.find('photos')
        if None == photosNode:
            return False
        photoList = []
        for photoNode in photosNode:
            key = photoNode.attrib['name']
            infoNode = photoNode.find('info')
            info = None
            if None != infoNode:
                info = PhotoInfo()
                if False == info.fromXmlElement(infoNode):
                    return False
            photoList.append((key, info))
            
        self.__defaultInfo = defaultInfo
        self.__photoList = photoList
        self.__subAlbumList = subAlbumList
        return True
    
    def toXmlElement(self):
        pass
        
        
class PhotoInfo:
    def __init__(self):
        self.__tags = []
        self.__level = None
        
    def setTag(self, tag):
        if tag in self.__tags:
            return
        self.__tags.append(tag)
        
    def setLevel(self, level):
        self.__level = level
        
    def fromXmlElement(self, elem):
        try: 
            lv = elem.attrib['level']
            lv = int(lv)
        except: 
            return False
        self.__level = lv
        return True
    
    def toXmlElement(self):
        return Element('info', {'level':str(self.__level), 'hasTag':'0'})