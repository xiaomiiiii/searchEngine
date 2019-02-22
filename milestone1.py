#!/usr/bin/env python
# coding: utf-8

# In[108]:


import json
from lxml.html.clean import Cleaner
import re
import collections

def get_json(file):
    with open(file) as f:
        return json.load(f)

def inverted_index():
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
                    #TODO: 处理04/288报错document is empty，暂时用了try except。04/288里全是乱码。
                    try:
                        content= cleaner.clean_html(raw_content)
                    except:
                        continue
                    #remove tags. only leave texts
                    reg = re.compile('<[^>]*>')
                    content = reg.sub(' ', content)
                    if content:
                        #TODO：只做了移除符号，大小写转换，没加stemming，stopWord等处理
                        content = re.sub(r"[^a-zA-Z0-9]", " ", content.lower())
                        for term in content.split():
                            #control the length of the term
                            if len(term) < 3 or len(term) > 20:
                                continue
                            if term not in index:
                                index[term] = {}
                            if doc_id not in index[term]:
                                index[term][doc_id] = {
                                    "tf": 0,
                                    "tf-idf": 0,
                                    "other_info": "to be improved in milestone 2"
                                }
                            index[term][doc_id]["tf"] += 1
    with open("index.json","w") as f:
        json.dump(index, f)
    return index

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

# my_index = inverted_index()
# print "Finished"
user_input = raw_input("Please input your search keyword: ")
search_result = search(user_input)
if search_result:
    for url in search_result:
        print url
else:
    print "No related content."
    



# In[ ]:




