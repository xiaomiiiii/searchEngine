
#!/usr/bin/env python
# coding: utf-8
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import json
from lxml.html.clean import Cleaner
import re
import collections
import numpy as np

def get_json(file):
    with open(file) as f:
        return json.load(f)

def get_stemmed_content(content, stemmer):
	for k in range(len(content)):
        content[k] = stemmer.stem(content[k]).encode('utf-8')

def is_stopwords(word, stopwordsList):
    if word in stopwordsList:
        return True
    else:
        return False

def calculate_tfidf(index):
	N = 37492
    for term in index:
        df = len(index[term])
        for doc_id in index[term]:
            tf = index[term][doc_id]["tf"]
            if tf == 0 or df == 0:
                index[term][doc_id]["tf-idf"] = 0
            else:
                index[term][doc_id]["tf-idf"] = (1 + np.log10(tf)) * (np.log10(N / df))
    with open("index.json","w") as f:
        json.dump(index, f)
    return index


def inverted_index():
    # initialization for stemmer and stopword processor for faster performance
    stemmer = SnowballStemmer('english')
    swlist = set(stopwords.words('english'))

    index = {}
    for i in range(75):
        print "Processing folder " + str(i)
        if i < 74:
            doc_num = 500
        else:
            doc_num = 497
        for j in range(doc_num):
            doc_id = "%s"%i + "/" + "%s"%j
            doc_path = "WEBPAGES_RAW/" + doc_id
            #path in WEBPAGES_RAW
            with open(doc_path) as page:
                raw_content = page.read()
                #remove css, scripts, js in the HTML file
                cleaner = Cleaner(style = True, scripts = True, comments = True, javascript = True, page_structure = False, safe_attrs_only = False)
                if raw_content:
                    try:
                        content= cleaner.clean_html(raw_content)
                    except:
                        continue
                    #remove tags. only leave texts
                    reg = re.compile('<[^>]*>')
                    content = reg.sub(' ', content)
                    if content:
                        #TODO：只做了移除符号，大小写转换，没加stemming，stopWord等处理
                        content = re.sub(r"[^a-zA-Z0-9]",
                        				 " ", 
                        				 content.lower())
                        # get the stermmed content
                        get_stemmed_content(content, stemmer) 
                        for term in content.split():
                            #control the length of the term 
                            # and exclude all stopwords
                            if len(term) < 3 or len(term) > 20 or is_stopwords(term, swlist):
                                continue
                            if term not in index:
                                index[term] = {}
                            if doc_id not in index[term]:
                                index[term][doc_id] = {
                                    "tf": 0,
                                    "tf-idf": 0
                                }
                            index[term][doc_id]["tf"] += 1
    
    N = 37492
    for term in index:
        df = len(index[term])
        for doc_id in index[term]:
            tf = index[term][doc_id]["tf"]
            if tf == 0 or df == 0:
                index[term][doc_id]["tf-idf"] = 0
            else:
                index[term][doc_id]["tf-idf"] = (1 + np.log10(tf)) * (np.log10(N / df))
    with open("index.json","w") as f:
        json.dump(index, f)
    return calculate_tfidf(index)

#TODO：增加index内容，排序，relevance scoring function，减小index（现在是570M），减少搜索时间，词组搜索，GUI。。。


def search(user_input):
    #TODO: 对user input的处理
    user_input = user_input.lower()
    urls=[]
    book_keeping = get_json("WEBPAGES_RAW/bookkeeping.json")
    index = get_json("index.json")
    #index = get_json("test.json")
    if user_input in index:
        for doc in index[user_input]:
            urls.append(book_keeping[doc])
            if len(urls) >= 10:
                break
    return urls
  
# create main function for primary entrance
if __name__ == "__main__":
	user_input = raw_input("Please input your search keyword: ")
	search_result = search(user_input)
	if search_result:
	    for url in search_result:
	        print url
	else:
	    print "No related content."




