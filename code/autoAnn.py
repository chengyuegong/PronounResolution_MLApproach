# -*- coding: utf-8 -*-
# Author: Gong Chengyue & Zhang Hongwei
# Orgnization: Zhejiang University
# Version: 1.1
# Date Updated: 04/25/2018

import os
from termcolor import *
import urllib.request
from stanfordcorenlp import StanfordCoreNLP

# Feature Vector[9] = [ant_arg0, ant_arg1, ana_arg0, ana_arg1, same_target, ana_pronoun, string_match, center_match, distance] - shape=[n_samples, 9]
# Result Vector - shape=[n_samples]

class AutomaticAnnotation:
	# Please pass absolute path to initialize the object
	def __init__(self, inputDirPath, outputDirPath):
		#path of stanford corenlp
		local_corenlp_path = r'./stanford-corenlp-full-2018-02-27'
		online_corenlp_path = r'http://corenlp.run'
		self.nlp = StanfordCoreNLP(local_corenlp_path, memory='8g', lang='zh')
		self.inputDirPath = inputDirPath # input file path
		self.outputDirPath = outputDirPath # output file path
		self.outputFV = open(self.outputDirPath+'/featureVectors.txt', 'w') # create a file for saving feature vectors
		self.outputResult = open(self.outputDirPath+'/result.txt', 'a') # create a file for saving result
		# self.fileList = [] # input file list
		# self.get_input_fileList() # get all input file
		self.sentenceSeg = [] # list of sentence
		self.NVList = [] # list of NP and VP
		self.synonym_dict = {} # dictionary of synonym
		self.create_dictionary() # create a dictionary from the file
		self.fVector = [0, 0, 0, 0, 0, 0, 0, 0, 0] # feature vector
		self.WORD = '那' # keyword

	def init_fVector(self):
		self.fVector = [0, 0, 0, 0, 0, 0, 0, 0, 0]

	def close_file(self):
		self.outputFV.close()

	def close_corenlp(self):
		self.nlp.close()

# outdated
   #  def get_input_fileList(self):
   #  	for (root, dirs, files) in os.walk(self.inputDirPath,topdown=True):
			# for fileName in files:
			# 	if fileName != '.DS_Store':
			# 		self.fileList.append(fileName)

# outdated
	# def get_distance(self, antecedent):
	# 	# determination of feature 8
	# 	offset = 0;
	# 	for elements_list in self.NVList:
	# 		if elements_list and (antecedent in elements_list):
	# 			break
	# 		offset += 1
	# 	self.fVector[8] = round((0.5+(offset-5)/10),1)

	def gen_args(self, content):
	    tmpList = []
	    tmpStr = ''
	    indexA1 = 0
	    while content.find('A1',indexA1)!=-1 or content.find('A0',indexA1)!=-1:
	        indexA1 = content.find('A',indexA1)
	        if content[indexA1+1]!='1' and content[indexA1+1]!='0':
	        	indexA1 = indexA1+1
	        	continue
	        indexA1c = content.rfind('[',0,indexA1)
	        for k in range(indexA1-indexA1c-2):
	            tmpStr = tmpStr+content[indexA1c+1+k]
	        tmpList.append(tmpStr.replace(' ',''))
	        tmpList.append('arg'+content[indexA1+1])
	        indexA1 = indexA1+1
	        tmpStr = ''
	    return tmpList

	def get_semantic_role(self):
		# determination of feature 0-4
		url_base = "http://api.ltp-cloud.com/analysis/?"
		api_key  = "71387141h3MIFv4IXp7aiPXFWQ6dOqlSrualbOoc"
		pattern  = "srl"
		format = 'plain'
		changeBit1=0
		changeBit2=0
		tmp_resultVector = []
		tmpcnt_arglist = 0
		argList = []
		for element in self.sentenceSeg:
			if element:
				print(element, "is being processed!")
				text = urllib.request.quote(element)
				url  = (url_base + "api_key=" + api_key + "&" + "text=" + text + "&"+ "format="+ format + "&" + "pattern=" + pattern)
				result = urllib.request.urlopen(url)
				content = result.read().strip().decode()
				argList = self.gen_args(content)
				if (tmpcnt_arglist!=5) and self.NVList[tmpcnt_arglist]:
					for elements in self.NVList[tmpcnt_arglist]:
						if (elements in argList) and argList[argList.index(elements)+1]=='arg0':
							tmp_resultVector.append([1,0,0,0,0])
						elif (elements in argList) and argList[argList.index(elements)+1]=='arg1':
							tmp_resultVector.append([0,1,0,0,0])
						else:
							tmp_resultVector.append([0,0,0,0,0])
				elif (tmpcnt_arglist==5) and self.NVList[tmpcnt_arglist]:
					cnt_zhe_argList = 0
					flag=-1
					for elements in argList:
						if self.WORD in elements:
							break
						cnt_zhe_argList = cnt_zhe_argList+1
					if cnt_zhe_argList!=len(argList):
						if argList[cnt_zhe_argList+1]=='arg0':
							flag=0
							changeBit1=1
							changeBit2=0
						elif argList[cnt_zhe_argList+1]=='arg1':
							flag=1
							changeBit1=0
							changeBit2=1
					for elements in self.NVList[tmpcnt_arglist]:
						if (elements in argList) and (self.WORD not in elements) and argList[argList.index(elements)+1]=='arg0':
				 			tmp_resultVector.append([1,0,changeBit1,changeBit2,changeBit1])
						elif (elements in argList) and (self.WORD not in elements) and argList[argList.index(elements)+1]=='arg1':
							tmp_resultVector.append([0,1,changeBit1,changeBit2,changeBit2])
						elif (self.WORD not in elements):
							tmp_resultVector.append([0,0,changeBit1,changeBit2,0])
			for elements in tmp_resultVector:
				elements[2] = changeBit1
				elements[3] = changeBit2
			tmpcnt_arglist = tmpcnt_arglist+1
		return tmp_resultVector # 2 dimensional list containing the information of .txt
		
	def is_ana_pronoun(self, props):
		# determination of feature 5
		# PN-1, DT-0
		if props['pos_tag'] == 'PN':
			self.fVector[5] = 1

	def is_string_match(self, antecedent):
		# determination of feature 6
		# this method should be called after is_ana_pronoun
		if self.fVector[5] == 0: # tag == 'DT'
			sentence = self.sentenceSeg[5]
			ant_pos_list = self.nlp.pos_tag(antecedent)
			ant_NN_list = []
			for element in ant_pos_list:
				if element[1] == 'NN':
					ant_NN_list.append(element[0])
			for element in ant_NN_list:
				if sentence.find(element) != -1:
					self.fVector[6] = 1
					return

	def is_center_match(self, antecedent):
		# determination of feature 7
		# this method should be called after is_ana_pronoun
		if self.fVector[5] == 0: # tag == 'DT'
			sentence = self.sentenceSeg[5]
			denp_parse = self.nlp.dependency_parse(antecedent)
			ant_word_token = self.nlp.word_tokenize(antecedent)
			ant_center = ant_word_token[denp_parse[0][2]-1]
			sent_word_token = self.nlp.word_tokenize(sentence)
			for word in sent_word_token:
				if (word in self.synonym_dict) and (ant_center in self.synonym_dict):
					if self.synonym_dict[word] == self.synonym_dict[ant_center]:
						self.fVector[7] = 1
						return
				else:
					if word == ant_center:
						self.fVector[7] = 1
						return

	def create_dictionary(self):
		with open("./Dict/synonym_dictionary.txt", 'r') as f:
			lines = f.readlines()
		for line in lines:
			line_list = line.split(' ')
			value = line[0]
			for i in range(1, len(line_list)-1):
				self.synonym_dict[line[i]] = value

	def write_feature_vector(self, n):
		self.outputFV.write(str(n)+' '+str(self.fVector)+'\n')
		self.outputFV.flush()
		print("Feature Vector", self.fVector, "has been written into the output file!")

	def write_result(self, n, result, total):
		if result == 0:
			self.outputResult.write(str(n)+' 0\n')
		else:	
			tvec = [0] * total
			for i in result:
				tvec[i] = 1
			self.outputResult.write(str(n)+' '+str(tvec)+'\n')
			self.outputResult.flush()
			print("Result", tvec, "has been written into the output file!")	

	def auto_annotating(self):
		file_n = 1
		while (os.path.exists(self.inputDirPath+'/'+str(file_n)+'.txt')):
			with open(self.inputDirPath+'/'+str(file_n)+'.txt','r') as fileObj:
				s = fileObj.read()
				[resultList, resultList2, props, blank] = s.split('\n')
				self.sentenceSeg = eval(resultList)
				self.NVList = eval(resultList2)
				props = eval(props)

			tmpVector = []
			print(colored("****************************************","yellow"))
			print(colored(str(file_n)+".txt is being automatically annotated!","red"))

			dis_list = []
			tmp_dis_cnt=0
			cnt=0 # number of NP&VP -> len(tmpVector)
			for elements in self.NVList:				
				if elements:
					for elementss in elements:
						if elementss and elementss.find(self.WORD) == -1:							
							tmpVector.append(elementss)
							dis_list.append(round((0.5+(tmp_dis_cnt-5)/10),1))
							# print(colored(str(cnt)+'. '+elementss,'blue'))
							cnt=cnt+1
				tmp_dis_cnt += 1

			# automatic annotation begins!
			srlist = self.get_semantic_role() # 2D
			for k in range(len(tmpVector)):
				self.fVector[0:5] = srlist[k][0:5]
				print(colored("Segmentic Role OK!","blue"))
				self.is_ana_pronoun(props)
				print(colored("Anaphora is PN or DT OK!","blue"))
				self.is_string_match(tmpVector[k])
				print(colored("String Match OK!","blue"))
				self.is_center_match(tmpVector[k])
				print(colored("Center Match Role OK!","blue"))
				self.fVector[8] = dis_list[k]
				print(colored("Distance OK!","blue"))
				# if k in c_n:
					# self.fVector[9] = 1
				self.write_feature_vector(file_n)
				self.init_fVector()
			file_n += 1

		self.close_file()
		self.close_corenlp()

	def man_annotating(self):
		with open(self.outputDirPath+'/page.txt', 'r') as fobj:
			file_n = int(fobj.read())
		pageFile = open(self.outputDirPath+'/page.txt', 'w')
		while (os.path.exists(self.inputDirPath+'/'+str(file_n)+'.txt')):
			with open(self.inputDirPath+'/'+str(file_n)+'.txt','r') as fileObj:
				s = fileObj.read()
				[resultList, resultList2, props, blank] = s.split('\n')
				self.sentenceSeg = eval(resultList)
				self.NVList = eval(resultList2)
				props = eval(props)

			# manual annotation begins!
			tmpVector = []
			print(colored("****************************************","yellow"))
			print(colored(str(file_n)+".txt is being manually annotated!","red"))

			i = 0
			print(colored('The original text is:','green'))
			for elements in self.sentenceSeg:
				if elements and i == 5:
					print(colored(elements,"red"), end=' ')
				elif elements:
					print(elements, end=' ')
				i += 1
			print()

			print(colored('The possible NPs and VPs corresponding to '+self.WORD+' are:','green'))

			cnt = 0 # number of NP&VP -> len(tmpVector)
			for elements in self.NVList:				
				if elements:
					for elementss in elements:
						if elementss and elementss.find(self.WORD) == -1:							
							tmpVector.append(elementss)
							print(colored(str(cnt)+'. '+elementss,'blue'))
							cnt=cnt+1

			c_n=eval(input(colored('Choose the ones that correspond to '+self.WORD+' (Enter the number in form of [1,2,3]): [Enter 0 to skip]' ,'green')))
			while c_n != 0 and type(c_n) != list:
				print(colored("Wrong format!! Enter agian:",'red'))
				c_n=eval(input(colored('Choose the ones that correspond to '+self.WORD+' (Enter the number in form of [1,2,3]): [Enter 0 to skip]' ,'green')))
			print(colored("Choice accpeted!",'green'))

			self.write_result(file_n, c_n, len(tmpVector))
			file_n += 1
			pageFile.seek(0,0)
			pageFile.write(str(file_n))

		pageFile.close()
		self.close_file()
		self.close_corenlp()

if __name__ == '__main__':
	inputpath = os.path.abspath('./result')
	outputpath = os.path.abspath('./labeled')
	a = AutomaticAnnotation(inputpath, outputpath)
	a.auto_annotating()
	# a.man_annotating()
