#coding:utf8
'''
Created on 2015-9-20

@author: Administrator
'''

from xml.etree.ElementTree import * 
import os.path
import pickle

def insertPhotoAlbumNode(parent, path):
    albumNode = SubElement(parent, 'photoAlbum', {'path':path})
    SubElement(albumNode, 'defaultInfo', {'level':'0', 'hasTag':'0'})
    SubElement(albumNode, 'subAlbums')
    SubElement(albumNode, 'photos')
    return albumNode

def insertPhotoNode(parent, name, level):
    photoNode = SubElement(parent, 'photo', {'name':name})
    SubElement(photoNode, 'info', {'level':str(level), 'hasTag':'0'})

def setPhoto(albumNode, val, name):
    photosNode = albumNode.find('photos')
    if None == photosNode:
        print 'photosNode error'
        return
    for photoNode in photosNode:
        if photoNode.attrib['name'] == name:
            print 'name not unique'
            return
    insertPhotoNode(photosNode, name, val)
        

def convertRepToXml():
    xmlSavePath = u'E:\\app_data\\picView\\test\\rep.xml'
    repPath = u'E:\\app_data\\picView\\test\\pro_mtl.rep'
    PhoteAlbumRoot = u'F:\\url_pic_center\\meitulu'
    
    with open(repPath, 'r') as fr:
        repObj = pickle.load(fr)
        
    root = Element(u'photoAlbums')
    xmlDoc = ElementTree(root)
    albumNode = insertPhotoAlbumNode(root, PhoteAlbumRoot)
    albumListNode = albumNode.find(u'subAlbums')
    
    subAlbumMap = {}
    for path, val in repObj.items():
        path = path.decode('gbk').encode('utf8')
        subDir, base = os.path.split(path)
        if subDir == '' or os.path.dirname(subDir) != PhoteAlbumRoot:
            print 'sub dir error : %s' % os.path.dirname(subDir)
            continue
        if base == '':
            print 'base name error'
            return
        
        subAlbumNode = None
        if subDir in subAlbumMap:
            subAlbumNode = subAlbumMap[subDir]
        else:
            subAlbumNode = insertPhotoAlbumNode(albumListNode, subDir)
            subAlbumMap.setdefault(subDir, subAlbumNode)
        setPhoto(subAlbumNode, val, base)
    
    xmlDoc.write(xmlSavePath, encoding='utf-8')
        
def main():
    convertRepToXml()
    
if __name__ == '__main__':
    main()