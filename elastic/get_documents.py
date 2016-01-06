#!/usr/bin/python
from os import environ
from config import es as default_es

def get_documents(terms, term_field, fields=["text"], es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    results = {}

    if len(terms) > 0:

        for term in terms:
            query = {
                "query": {
                    "term": {
                        term_field: term
                    }
                },
                "fields": fields
            }

            res = es.search(body=query, 
                            index=es_index,
                            doc_type=es_doc_type)

            if res['hits']['hits']:
                hits = res['hits']['hits']

                records = []
                for hit in hits:
                    record = {}
                    if not hit.get('fields') is None:
                        record = hit['fields']
                    record['id'] =hit['_id']
                    records.append(record)
                results[term] = records           
            
    return results


def get_more_like_this(urls, fields=[], pageCount=200, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    docs = [{"_index": es_index, "_type": es_doc_type, "_id": url} for url in urls]

    with open(environ['DDT_HOME']+'/elastic/stopwords.txt', 'r') as f:
        stopwords = [word.strip() for word in f.readlines()] 

    query = {
        "query":{
            "more_like_this": {
                "fields" : ["text"],
                "docs": docs,
                "min_term_freq": 1,
                "stop_words": stopwords
            }
        },
        "fields": fields,
        "size": pageCount
    }

    res = es.search(body=query, index = es_index, doc_type = es_doc_type)
    hits = res['hits']['hits']

    results = []
    for hit in hits:
        fields = hit['fields']
        fields['id'] = hit['_id']
        results.append(fields)
 
    return results

def get_most_recent_documents(opt_maxNumberOfPages = 200, mapping=None, fields = [], opt_filter = None, es_index = 'memex', es_doc_type = 'page', es = None):

    if mapping == None:
        print "No mappings found"
        return []

    if es is None:
        es = default_es

    query = { 
        "size": opt_maxNumberOfPages,
        "sort": [
            {
                mapping["timestamp"]: {
                    "order": "desc"
                }
            }
        ]
    }

    match_q = {
        "match_all": {}
    }
            
    if not mapping.get("content_type") is None:
        match_q = {
            "match": {
                mapping["content_type"]: "text/html"
            }
        }


    if opt_filter is None:
        query["query"] = {
            "filtered": {
                "query": match_q,
                "filter":{
                    "exists": {
                        "field": mapping['text']
                    }
                }
            }
        }
    else:
        query["query"] = {
            "query_string": {
                "fields" : [mapping['text']],
                "query": ' and  '.join(opt_filter.split(' ')),
            }
        }

    if len(fields) > 0:
        query["fields"] = fields
    
    res = es.search(body=query, index = es_index, doc_type = es_doc_type)
    hits = res['hits']['hits']
    
    results = []
    for hit in hits:
        fields = hit['fields']
        fields['id'] = hit['_id']
        results.append(fields)

    return results

def get_all_ids(pageCount = 100000, es_index = 'memex', es_doc_type = 'page', es = None):
    if es is None:
        es = default_es

    query = {
        "query": {
            "match_all": {}
        },
        "fields": ['url']
    }

    try:
        res = es.search(body=query, index = es_index, doc_type = es_doc_type, size = pageCount)
        hits = res['hits']['hits']
    
        urls = []
        for hit in hits:
            urls.append(hit['fields']['url'][0])
            
        return urls
    except IndexMissingException:
        print 'Index Missing ', es_index
        return []

def get_documents_by_id(ids=[], fields=[], es_index = 'memex', es_doc_type = 'page', es = None):
    if es is None:
        es = default_es
        
    query = {
        "query": {
            "ids": {
                "values": ids
            }
        },
        "fields": fields
    } 

    res = es.search(body=query, index = es_index, doc_type = es_doc_type, size=len(ids))

    hits = res['hits']['hits']

    results = []
    for hit in hits: 
        if hit.get('fields'):
            fields = hit['fields']
            fields['id'] = hit['_id']
            results.append(fields)
    return results

if __name__ == "__main__":
    urls = []
    with open(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/results.txt', 'r') as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    docs = get_documents(urls)

