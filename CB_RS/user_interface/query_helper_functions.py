#!/usr/bin/env python
# -*- coding: latin-1 -*-
import pandas as pd # pandas is a data manipulation library
from SPARQLWrapper import SPARQLWrapper,JSON, SPARQLWrapper2, POST,XML,GET
from tqdm.notebook import tqdm


def retrieve_data_for_movies_list(query, search_list, chunck_size, search_data_type, endpoint, return_format,request_method):
    
    done = False
    start = 0
    end = 0
    chunk = chunck_size
    data_length = len(search_list)
    all_results_df = pd.DataFrame()
    failed_movies_list=[]
    while (not done):
        try:
            start = end
            end = end + chunk

            if (end > data_length):
                end = data_length

            data_slice= search_list[start:end] 
            data_chunck =[]
            if (str(search_data_type) == "string"):
                print("Searching by movie title")
                data_chunck = [movie.strip().lower() for movie in data_slice]
                final_search_list = '\"""' + '\""",\"""'.join(data_chunck) + '\"""' 
            else:
                if (str(search_data_type) == "url"):
                    print("Searching by movie URL")
                    data_chunck = [' <'+ data + '> ' for data in data_slice]
                    final_search_list = ','.join(data_chunck) 
                
            
            print("Processing movies between {} {}\n".format(start, end))

            try:
                results = execute_query_for_movies_list(query,final_search_list,endpoint, return_format,request_method)              
                all_results_df = all_results_df.append(get_sparql_dataframe(results))  
                
            except Exception as ex:
                print(ex)
                print("Chunck Failed : {}".format(final_search_list))
                split_movies_list = final_search_list.split(",")
                for movie in split_movies_list:
                    failed_movies_list.append(movie)

            if (end >= data_length):
                done = True
            print("Results data frame length = {} \n".format(len(all_results_df)))
            #print(all_results_df)
        except Exception as ex:
            print (ex)
        
    return [all_results_df, failed_movies_list]

def get_sparql_dataframe(result):
    """
    Helper function to convert SPARQL results into a Pandas data frame.
    """
    processed_results = result.fullResult
    processed_results
    cols = processed_results['head']['vars']
   # print(cols)

    out = []
    for row in processed_results['results']['bindings']:
        item = []
        for c in cols:
            item.append(row.get(c, {}).get('value'))
        out.append(item)

    return pd.DataFrame(out, columns=cols)

#function to retrieve the actors for list of movies
def execute_query(query, endpoint, return_format):
    sparql = SPARQLWrapper2(endpoint)  
    sparql.setQuery(query) 
    sparql.setReturnFormat(return_format)   
    sparql.setMethod(POST)
  
    results = sparql.query()
    return results

def execute_query_for_movies_list(query,movies_list, endpoint,return_format,request_method):
    sparql = SPARQLWrapper2(endpoint)  
    sparql.setQuery(query%movies_list) 
   # print(sparql.queryString)
    sparql.setReturnFormat(return_format)   
    sparql.setMethod(request_method)
   # print(sparql)
    results = sparql.query()
    
    return results


    
#function to retrieve movies information for list of movies
def prepare_and_run_query(count_query, data_query, endpoint, return_format):
    all_results_df = pd.DataFrame()
        
    results = execute_query(count_query, endpoint, return_format)
    
    for result in results.bindings:
        count = [result["cnt"].value]        
    count = int(count[0])    
    
    print ("Number of records expected by the query to retrieve all movies info except for the actors is {}".format(count))
    
    start= 0
    step = 5000
    
    for i in tqdm(range(step, count + step, step)):
        
        end = i
        if end>count:
            end=count
               
        query = data_query + " LIMIT " + str(step) + " OFFSET " + str(start)
        
        #print(newQuery)
        
        try:
            results = execute_query(query,endpoint,return_format)              
            all_results_df = all_results_df.append(get_sparql_dataframe(results))               
        except Exception as ex:
            print(ex)
            print("Failed to retrieve movies info for the range with offset {} step {}".format(offset, step))

        print("Results data frame length = {} \n".format(len(all_results_df)))
        start = end        
    return all_results_df
        