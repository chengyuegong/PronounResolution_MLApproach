# _*_coding:utf-8_*_
import os
import codecs
from stanfordcorenlp import StanfordCoreNLP

#path of stanford corenlp
local_corenlp_path = r'./stanford-corenlp-full-2018-02-27'
online_corenlp_path = r'http://corenlp.run'

#获取当前路径
basepath = os.path.abspath('')

#define a stack
class MyStack:
        def __init__(self):
                self.items = []

        def isEmpty(self):
                return self.items == []

        def size(self):
                return len(self.items)

        def push(self, item):
                self.items.append(item)

        def top(self):
                return self.items[len(self.items)-1]

        def pop(self):
                self.items.pop()

class FindNounPhrase:
        def __init__(self, rawFile, destFile):
                self.nlp = StanfordCoreNLP(local_corenlp_path, memory='8g', lang='zh')
                self.filePath = basepath+r'/'+rawFile
                self.destPath = basepath+r'/'+destFile
                self.fileList = []
                self.s = ""
                self.resultList = [[],[],[],[],[],[],[],[],[],[],[]]
                self.cnt = 1

        def close(self):
                self.nlp.close()
	    
        def get_directory(self):
                #从上到下遍历文件
                for (root, dirs, files) in os.walk(self.filePath,topdown=True):
                        for elements in files:
                                self.fileList.append(elements)

        def read_meterial_YM(self, filename):
                with codecs.open(self.filePath+r'/'+filename, encoding='utf-8') as fileObj:
                    self.s = fileObj.read()
                i,index = 0,0
                while self.s.find('这',i)!=-1:
                    index = self.s.find('这',i)
                    self.finding('这','>','<',i)
                    print("resultList =", self.resultList)
                    resultList_NP = [[],[],[],[],[],[],[],[],[],[],[]]
                    j = 0
                    for sentence in self.resultList:
                        if (type(sentence) == list or sentence == ''):
                                j += 1
                                continue
                        NPList = self.getAllNounPhrase(sentence)
                        resultList_NP[j] = NPList
                        j += 1
                    #写入文件
                    destname = str(self.cnt)+r'.txt'
                    with open(self.destPath+r'/'+destname, 'w') as writeObj:
                        writeObj.write(str(self.resultList))
                        writeObj.write('\n')
                        writeObj.write(str(resultList_NP))
                        writeObj.write('\n')
                    print("File", destname, "is done!\n")
                    self.resultList=[[],[],[],[],[],[],[],[],[],[],[]]
                    self.cnt=self.cnt+1
                    i = index+1

        def read_meterial_CCL(self, filename):
                with codecs.open(self.filePath+r'/'+filename, encoding='utf-8') as fileObj:
                    self.s = fileObj.read()
                i,index = 0,0
                while self.s.find('那',i)!=-1:
                    index = self.s.find('那',i)
                    self.finding('那','】','【',i)
                    print("resultList =", self.resultList)
                    resultList_NP = [[],[],[],[],[],[],[],[],[],[],[]]
                    j = 0
                    for sentence in self.resultList:
                        if (type(sentence) == list or sentence == ''):
                                j += 1
                                continue
                        NPList = self.getAllNounPhrase(sentence)
                        resultList_NP[j] = NPList
                        j += 1
                    #写入文件
                    destname = str(self.cnt)+r'.txt'
                    with open(self.destPath+r'/'+destname, 'w') as writeObj:
                        writeObj.write(str(self.resultList))
                        writeObj.write('\n')
                        writeObj.write(str(resultList_NP))
                        writeObj.write('\n')
                    print("File", destname, "is done!\n")
                    self.resultList=[[],[],[],[],[],[],[],[],[],[],[]]
                    self.cnt=self.cnt+1
                    i = index+1

        def finding(self, dest_str, stop_str1, stop_str2, i):
                PUList = ['，', '。', '；', '？', '！']
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
                        if self.s[index-1] in PUList:
                                j=j+1
                        elif self.s[index-1]==stop_str1:
                                j=j+1
                                break
                        index=index-1
                index=index+1
                for k in range(j-1):
                        tmpS = ''
                        while self.s[index] not in PUList:
                                tmpS=tmpS+self.s[index]
                                index=index+1
                        self.resultList[6-j] = tmpS.replace(' ','')
                        index = index+1
                        j=j-1
		        #向后寻找5句话
                j=0
                index = tmpIndex
                while j!=6:
                        if self.s[index+1] in PUList:
                                j=j+1
                        elif self.s[index+1]==stop_str2:
                                break
                        index=index+1
                for k in range(j):
                        tmpS=''
                        while self.s[tmpIndex] not in PUList:
                                tmpS=tmpS+self.s[tmpIndex]
                                tmpIndex=tmpIndex+1
                        self.resultList[5+k] = tmpS.replace(' ','')
                        tmpIndex = tmpIndex+1

        def getAllNounPhrase(self, sentence):
                print(sentence, "is processing!")
                NPIndexList = []
                NPlist = []
                parsestr = ''
                parsestr = self.nlp.parse(sentence)
                # print(parsestr)
                NOUNPHRASE = 'NP'
                begin = 0
                NPindex = parsestr.find(NOUNPHRASE, begin)
                while (NPindex != -1):
                        if (parsestr[NPindex-1] == '('):
                                NPIndexList.append(NPindex)
                        begin = NPindex+1
                        NPindex = parsestr.find(NOUNPHRASE, begin)
                # print(NPIndexList)
                for i in NPIndexList:
                        nphrase = ''
                        cur = i+3
                        st = MyStack()
                        st.push('(')
                        while (not st.isEmpty()):
                                if(parsestr[cur] == ' ' or parsestr[cur] == '\n'):
                                        cur += 1
                                elif(parsestr[cur] == '('):
                                        cur += 1
                                        st.push('(')
                                elif(parsestr[cur] == ')'):
                                        cur += 1
                                        st.pop()
                                elif(parsestr[cur] >= 'A' and parsestr[cur] <= 'Z'):
                                        cur += 1
                                else:
                                        nphrase += parsestr[cur]
                                        cur += 1
                        NPlist.append(nphrase)
                print(sentence, "is finished!")
                return NPlist

if __name__ == '__main__':
        a = FindNounPhrase('rawMaterial','result')
        a.get_directory()
        # print(a.fileList)
        fileList = a.fileList
        for element in fileList:
                if element != '.DS_Store':
                        a.read_meterial_CCL(element)
        a.close()
