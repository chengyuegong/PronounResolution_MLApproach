# _*_coding:utf-8_*_
# Author: Gong Chengyue & Zhang Hongwei
# Orgnization: Zhejiang University
# Version: 1.1
# Date Updated: 04/29/2018

import os
import codecs
from stanfordcorenlp import StanfordCoreNLP

# define a stack
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

# get all NP & VP
class GetMarkables:
    def __init__(self, rawFile, destFile):
        # path of stanford corenlp
        local_corenlp_path = r'./stanford-corenlp-full-2018-02-27'
        # online_corenlp_path = r'http://corenlp.run'
        self.nlp = StanfordCoreNLP(local_corenlp_path, memory='8g', lang='zh') # stanford corenlp tool
        self.srcPath = rawFile # path of input directory
        self.destPath = destFile # path of output directory
        self.fileList = [] # file list of input directory
        self.gen_fileList()
        self.s = '' # stores the reading
        self.sentenceList = ['','','','','','','','','','',''] # stores the 11 sentences (sentenceList[5] contains anaphora)
        self.cnt = 1 # count the number of output file
        self.nvpnum = 0 # count the number of NP and VP
        self.TAGList = ['DT', 'PN'] # the pos_tag we need for annotation


    def close_corenlp(self):
        self.nlp.close()

    def gen_fileList(self):
        for (root, dirs, files) in os.walk(self.srcPath, topdown=True):
            for filename in files:
                if filename != '.DS_Store':
                    self.fileList.append(filename)

    def read_meterial_YM(self, filename):
        print("---------------+++++++++++++++---------------")
        print(filename, "is being processed!")
        with codecs.open(self.srcPath+'/'+filename, encoding='utf-8') as fileObj:
            self.s = fileObj.read()
        index = 0
        while self.s.find('这',index) != -1:
            index = self.s.find('这',index)
            self.finding('这','>','<',index)
            tag = self.get_pos_tag(self.sentenceList[5], '这')
            if tag in self.TAGList:
                props = {}
                props['pos_tag'] = tag
                props['filename'] = filename
                print("sentenceList =", self.sentenceList)
                NVList = [[],[],[],[],[],[],[],[],[],[],[]]
                j = 0
                for sentence in self.sentenceList:
                    if sentence == '':
                        j += 1
                        continue
                    NPList = self.getAllNounPhrase(sentence)
                    VPList = self.getAllVerbPhrase(sentence)
                    self.nvpnum += len(NPList) + len(VPList)
                    NVList[j] = NPList+VPList
                    j += 1
                print("NVList =", NVList)
                print("Total number of N&V Phrase =", self.nvpnum)
                # write into the file
                destname = str(self.cnt)+'.txt'
                with open(self.destPath+'/'+destname, 'w') as writeObj:
                    writeObj.write(str(self.sentenceList))
                    writeObj.write('\n')
                    writeObj.write(str(NVList))
                    writeObj.write('\n')
                    writeObj.write(str(props))
                    writeObj.write('\n')
                print("File", destname, "is done!\n")
                self.sentenceList = ['','','','','','','','','','','']
                self.cnt += 1
            else:
                print(tag, "is filtered out!")
            index += 1

    def read_meterial_CCL(self, filename):
        with codecs.open(self.srcPath+r'/'+filename, encoding='utf-8') as fileObj:
            lines = fileObj.readlines()
        for line in lines:
            self.s = line
            print("---------------+++++++++++++++---------------")
            print("sentence =", self.s)
            index = 0
            while self.s.find('那',index) != -1:
                index = self.s.find('那',index) 
                self.finding('那',':','【',index)
                print("sentenceList =", self.sentenceList)
                tag = self.get_pos_tag(self.sentenceList[5], '那')
                if tag in self.TAGList:
                    props = {}
                    props['pos_tag'] = tag
                    sent_num_end = self.s.find(':')
                    props['sent_num'] = eval(self.s[:sent_num_end])
                    NVList = [[],[],[],[],[],[],[],[],[],[],[]]
                    j = 0
                    for sentence in self.sentenceList:
                        if sentence == '':
                            j += 1
                            continue
                        NPList = self.getAllNounPhrase(sentence)
                        VPList = self.getAllVerbPhrase(sentence)
                        self.nvpnum += len(NPList) + len(VPList)
                        NVList[j] = NPList+VPList
                        j += 1
                    print("NVList =", NVList)
                    print("Total number of N&V Phrase =", self.nvpnum)
                    # write into the file
                    destname = str(self.cnt)+'.txt'
                    with open(self.destPath+'/'+destname, 'w') as writeObj:
                        writeObj.write(str(self.sentenceList))
                        writeObj.write('\n')
                        writeObj.write(str(NVList))
                        writeObj.write('\n')
                        writeObj.write(str(props))
                        writeObj.write('\n')
                    print("File", destname, "is done!\n")
                    self.cnt += 1
                else:
                    print(tag, "is filtered out!")
                self.sentenceList = ['','','','','','','','','','','']
                index += 1

    def finding(self, dest_str, stop_str1, stop_str2, index):
        PUList = ['，', '。', '；', '？', '！', '：', ',', ':', ';', '?', '!']
        # get 5 sentences before anaphora
        j=0
        flag=0
        tmpIndex = index
        while j!=6:
            if j==1 and flag==0:
                tmpIndex=index+1
                flag=1
            if self.s[index-1] in PUList:
                j=j+1
            elif self.s[index-1]==stop_str1:
                j=j+1
                if j==1 and flag==0:
                    tmpIndex=index
                index=index-1
                break
            index=index-1
        index=index+1
        for k in range(j-1):
            tmpS = ''
            while self.s[index] not in PUList and self.s[index] != stop_str1:
                tmpS=tmpS+self.s[index]
                index=index+1
            self.sentenceList[6-j] = tmpS.replace(' ','').replace('\u3000','').replace('\t','')
            index=index+1
            j=j-1
        # get 5 sentences after anaphora
        j=0
        index = tmpIndex
        while j!=6:
            if self.s[index+1] in PUList:
                j=j+1
            elif self.s[index+1]==stop_str2:
                j=j+1
                break
            index=index+1
        index = tmpIndex
        for k in range(j):
            tmpS=''
            while self.s[index] not in PUList and self.s[index] != stop_str2:
                tmpS=tmpS+self.s[index]
                index=index+1
            self.sentenceList[5+k] = tmpS.replace(' ','').replace('\u3000','').replace('\t','')
            index = index+1

    def getAllNounPhrase(self, sentence):
        print(sentence, "is being processed! -- NP")
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
        print(sentence, "is finished! -- NP")
        return NPlist
    
    def getAllVerbPhrase(self, sentence):
        print(sentence, "is being processed! -- VP")
        VPIndexList = []
        VPList = []
        parsestr = ''
        parsestr = self.nlp.parse(sentence)
        # print(parsestr)
        VERBPHRASE = 'VP'
        begin = 0
        VPindex = parsestr.find(VERBPHRASE, begin)
        while (VPindex != -1):
            if (parsestr[VPindex-1] == '('):
                VPIndexList.append(VPindex)
            begin = VPindex+1
            VPindex = parsestr.find(VERBPHRASE, begin)
        # print(VPIndexList)
        for i in VPIndexList:
            vphrase = ''
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
                    vphrase += parsestr[cur]
                    cur += 1
            VPList.append(vphrase)
        print(sentence, "is finished!")
        return VPList

    def get_pos_tag(self, sentence, word):
        postag_list = self.nlp.pos_tag(sentence) # list of tuples - [(word0, pos_tag0),(word1, pos_tag1), ...]
        for item in postag_list:
            if (item[0].find(word) != -1):
                return item[1]

    def preprocessing(self):
        for fobj in self.fileList:
            # o.read_meterial_YM(fobj)
            self.read_meterial_CCL(fobj)
                

if __name__ == '__main__':
    inputDir = os.path.abspath('./rawMaterial')
    outputDir = os.path.abspath('./result')
    o = GetMarkables(inputDir,outputDir)
    o.preprocessing()
    o.close_corenlp()
