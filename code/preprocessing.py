#!/usr/bin/python 
# -*- coding: utf-8 -*-

import logging
from stanfordcorenlp import StanfordCoreNLP

local_corenlp_path = r'./stanford-corenlp-full-2018-02-27'
online_corenlp_path = r'http://corenlp.run'

sentence = '这是浙江大学‘

with StanfordCoreNLP(local_corenlp_path, memory='8g', lang='zh') as nlp:
# with StanfordCoreNLP(online_corenlp_path, port=80, memory='8g', lang='zh') as nlp:
	print(nlp.word_tokenize(sentence))
	print(nlp.pos_tag(sentence))
	print(nlp.ner(sentence))
	print(nlp.parse(sentence))
	print(nlp.dependency_parse(sentence))
	# props = {'annotators': 'tokenize,ssplit,pos,ner,parse', 'pipelineLanguage': 'zh', 'outputFormat': 'text'}
	# print(nlp.annotate(sentence, properties=props))

