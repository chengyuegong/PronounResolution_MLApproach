#!/usr/bin/python 
# -*- coding: utf-8 -*-
import os
import codecs
#获取当前路径
basepath = os.path.abspath('')
class pS:
    def __init__(self, rawFile, destFile):
        self.filepath = basepath+r'/'+rawFile
        self.destPath = basepath+r'/'+destFile
        self.fileList = []
        self.s = ""
        self.resultList = [[],[],[],[],[],[],[],[],[],[],[]]
        self.cnt = 1
        
    def get_directory(self):
        #从上到下遍历文件
        for (root, dirs, files) in os.walk(self.filepath,topdown=True):
            for elements in files:
                self.fileList.append(elements)

    def read_meterial_YM(self, filename):
        with codecs.open(self.filepath+r'/'+filename, encoding='utf-8') as fileObj:
            self.s = fileObj.read()
        i,index = 0,0
        while self.s.find('这',i)!=-1:
            index = self.s.find('这',i)
            self.finding('这','>','<',i)
            #写入文件
            destname = str(self.cnt)+r'.txt'
            with open(self.destPath+r'/'+destname, 'w') as writeObj:
                writeObj.write(str((self.resultList)))
            self.resultList=[[],[],[],[],[],[],[],[],[],[],[]]
            self.cnt=self.cnt+1
            i = index+1
    def read_meterial_CCL(self, filename):
        with codecs.open(self.filepath+r'/'+filename, encoding='utf-8') as fileObj:
            self.s = fileObj.read()
        i,index = 0,0
        while self.s.find('那',i)!=-1:
            index = self.s.find('那',i)
            self.finding('那','】','【',i)
            #写入文件
            destname = str(self.cnt)+r'.txt'
            with open(self.destPath+r'/'+destname, 'w') as writeObj:
                writeObj.write(str((self.resultList)))
            self.resultList=[[],[],[],[],[],[],[],[],[],[],[]]
            self.cnt=self.cnt+1
            i = index+1


    def finding(self, dest_str,stop_str1,stop_str2,i):
    #向前寻找
        j=0
        flag=0
        index = self.s.find(dest_str,i)
        tmpIndex = index
        tmpIndex2 = index
        while j!=6:
            if j==1 and flag==0:
                tmpIndex=index+1
                flag=1
            if self.s[index-1]=='，' or self.s[index-1]=='。' or self.s[index-1]=='；' or self.s[index-1]=='？':
                j=j+1
            elif self.s[index-1]==stop_str1:
                j=j+1
                break
            index=index-1
        index=index+1
        for k in range(j-1):
            tmpS = ''
            while self.s[index]!='，' and self.s[index]!='。' and self.s[index]!='；' and self.s[index]!='？':
                tmpS=tmpS+self.s[index]
                index=index+1
            self.resultList[6-j] = tmpS.replace(' ','')
            index = index+1
            j=j-1
        #向后寻找5句话
        j=0
        index = tmpIndex
        while j!=6:
            if self.s[index+1]=='，' or self.s[index+1]=='。' or self.s[index+1]=='；' or self.s[index+1]=='？':
                j=j+1
            elif self.s[index+1]==stop_str2:
                break
            index=index+1
        for k in range(j):
            tmpS=''
            while self.s[tmpIndex]!='，' and self.s[tmpIndex]!='。' and self.s[tmpIndex]!='；' and self.s[tmpIndex]!='？':
                tmpS=tmpS+self.s[tmpIndex]
                tmpIndex=tmpIndex+1
            self.resultList[5+k] = tmpS.replace(' ','')
            tmpIndex = tmpIndex+1
            
