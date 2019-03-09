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

# def get_stemmed_content(content, stemmer):
#     for k in range(len(content)):
#         content[k] = stemmer.stem(content[k]).encode('utf-8')

def get_stemmed_terms(terms, stemmer):
    for k in range(len(terms)):
        terms[k] = stemmer.stem(terms[k]).encode('utf-8')

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
                        content = re.sub(r"[^a-zA-Z0-9]",
                        				 " ", 
                        				 content.lower())
                        # get the stermmed content
                        contents = content.split()
                        get_stemmed_terms(contents, stemmer)
                        for term in contents:
                            #control the length of the term 
                            # and exclude all stopwords
                            if len(term) < 3 or len(term) > 20 or is_stopwords(term, swlist):
                                continue
                            if term not in index:
                                index[term] = {}
                                index[term]["token"] = term
                            if doc_id not in index[term]:
                                index[term][doc_id] = {
                                    "tf": 0,
                                    "tf-idf": 0
                                }
                            index[term][doc_id]["tf"] += 1
    
    index = calculate_tfidf(index)

    with open("index.json","w") as f:
        json.dump(index, f)
    return index


def search(user_input, index, bookkeeping):
    stemmer = SnowballStemmer('english')
    swlist = set(stopwords.words('english'))

    urls=[]
    #cleaned user terms
    user_input = re.sub(r"[^a-zA-Z0-9]", " ", user_input.lower())
    
    user_terms = user_input.split()
    get_stemmed_terms(user_terms, stemmer)
    user_terms = filter(lambda x: not is_stopwords(x, swlist), user_terms)
    N = 37492.0
    doc_id = "qry"
    user_index = {}

     # no need to consider other terms non-existing
    for term in user_terms:
        if term not in user_index:
            user_index[term] = {}

        user_index[term][doc_id] = {
                                        "tf": 0,
                                        "tf-idf": 0
                                    }
        user_index[term][doc_id]["tf"] += 1
       

    #now get document-frequency from index
    for term in user_terms:
        user_index[term][doc_id]["df"] = len(index[term])
        print "index[term] length", len(index[term])

    #calculate tf-idf for all users
    #user_index = calculate_tfidf(user_index)
    #print "user_index",user_index
    for term in user_index :
        for docid in user_index[term]:
            tf = user_index [term][docid]["tf"]
            df = user_index [term][docid]["df"]
            if tf == 0 or df == 0:
                user_index[term][docid]["tf-idf"] = 0
            else:
                user_index[term][docid]["tf-idf"] = (1 + np.log10(tf)) * (np.log10(N / df))
   
   # return index

    #get tf-idf from the index
    docScores = {}
    for term in user_terms:
        # only deal with index
        if term in index:
            #get all documents id for the term
            docIDs = index[term].keys()
            #print "key:", docIDs
            for docid in docIDs:
               # print "user_index[term]", user_index[term].keys()
                if docid in docScores:
                   #if docid in user_index[term].keys():
                        docScores[docid] += index[term][docid]["tf-idf"] * user_index[term][doc_id]["tf-idf"]
                        print "docScores[docid]:", docScores[docid]
                    #else:
                        #pass
                else:
                    #if docid in user_index[term].keys():
                        docScores[docid] = index[term][docid]["tf-idf"] * user_index[term][doc_id]["tf-idf"]
                        print "docScores[docid]:", docScores[docid]
                   # else:
                        #docScores[docid] = 0


    # collect 10 result
    count = 0
    result = []
    for key, value in sorted(docScores.iteritems(), key=lambda (k,v): (v,k)):
        count = count + 1
        result.append({'rank': count, 'docID': key, 'score': value, 'url': book_keeping[key]})
        if count > 10: 
            break
    return result


  
# create main function for primary entrance

index = get_json("/Users/irenewang/SearchEngine-master/codes/searchEngine/index.json")

book_keeping = get_json("/Users/irenewang/WEBPAGES_RAW/bookkeeping.json")
user_input = raw_input("Please input your search keyword: ")
search_result = search(user_input, index, book_keeping)
print search_result
  
  




