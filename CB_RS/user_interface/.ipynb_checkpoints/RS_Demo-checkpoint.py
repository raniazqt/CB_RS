#!/usr/bin/env python
# -*- coding: latin-1 -*-
import pandas as pd 
import numpy as np 
import csv
import logging
from SPARQLWrapper import SPARQLWrapper,JSON, SPARQLWrapper2, POST,XML,GET
import query_helper_functions as q_helper
import sparql_query as sparql_query
import movies_df_helper_functions as d_helper
import gensim
from gensim.models.doc2vec import Doc2Vec
import re
import imp
imp.reload(q_helper)
imp.reload(d_helper)
imp.reload(sparql_query)

from os import system, name 
from tabulate import tabulate


def select_values(to_keep_val, other_val):
    if (str(to_keep_val) != "NOT_FOUND"):
        return to_keep_val
    else:
        return other_val

#retrieves movie features from lod (dbpedia and yago)
def retrieve_features_from_lod(movie_title):
    dbpedia_results= query_dbpedia_by_title(movie_title)
    yago_results = query_yago_by_title(movie_title)
    
    yago_results= yago_results.fillna("NOT_FOUND")
    #group yago results
    yago_grouped = yago_results.groupby(['movie_id','title'], as_index=False)
    yago_info_df = yago_grouped.agg({
                                        'director_name':lambda x: '|'.join(set(x)),
                                        'genre':lambda x: '|'.join(set(x)),                                      
                                        'country':lambda x:  '|'.join(set(x)),
                                        'actor_name':lambda x: '|'.join(set(x))
                                        })
    #Group pedia results
    dbpedia_results= dbpedia_results.fillna("NOT_FOUND")
    dbpedia_grouped = dbpedia_results.groupby(['movie_id','title'], as_index=False)
    dbpedia_info_df = dbpedia_grouped.agg({
                                        'director_name':lambda x:  '|'.join(set(x)),
                                        'writer_name':lambda x: '|'.join(set(x)),                                      
                                        'country':lambda x: '|'.join(set(x)),
                                        'actor_name':lambda x: '|'.join(set(x))
                                        })
    result_df = yago_info_df.merge(dbpedia_info_df, how="inner", on=['movie_id','title'])
    if len(result_df) >0:
        #keep dbpedia value if both exist
        result_df['actor_name'] = result_df.apply(lambda row: select_values(row.actor_name_y, row.actor_name_x), axis=1)
        #keep director from yago if exists in both
        result_df['director_name'] = result_df.apply(lambda row: select_values(row.director_name_x, row.director_name_y), axis=1)
        #keep director from yago if exists in both
        result_df['country'] = result_df.apply(lambda row: select_values(row.country_x, row.country_y), axis=1)
    
        result_df = result_df[['movie_id','title','actor_name','director_name','writer_name','country','genre']].copy()
    
    print(result_df)
    return result_df

def query_dbpedia_by_title(query_movie_title):
    endpoint = "https://dbpedia.org/sparql"
    return_format = XML
    request_method= POST
    query = sparql_query.dbpedia_query_by_title
    query_title_list ='\"""' + '\""",\"""' + query_movie_title.lower() + '\"""' 
    q_results= q_helper.execute_query_for_movies_list(query, query_title_list,endpoint,return_format,request_method)
    q_results_df= q_helper.get_sparql_dataframe(q_results)
    return q_results_df

def query_yago_by_title(query_movie_title):
    endpoint="https://yago-knowledge.org/sparql/query"
    return_format = JSON
    request_method= POST
    query = sparql_query.yago_query_by_title
    query_title_list ='\"""' + '\""",\"""' + query_movie_title.lower() + '\"""' 
    q_results= q_helper.execute_query_for_movies_list(query, query_title_list,endpoint,return_format,request_method)
    q_results_df= q_helper.get_sparql_dataframe(q_results)
    return q_results_df

def get_movie_sentence(movie_df):
        movie_df = movie_df.replace("NOT_FOUND",None)
        movie_df = data_processing(movie_df, 'actor_name')
        movie_df = data_processing(movie_df, 'writer_name')
        movie_df = data_processing(movie_df, 'genre')
        movie_df = data_processing(movie_df, 'country')
        movie_df = data_processing(movie_df, 'director_name')
        movie_df['movie_id']=movie_df['movie_id'].str.lower()
        movie_df['title']=movie_df['title'].str.lower()
        movie_df['movie_sentence']= movie_df.apply(lambda row:  build_movie_sentence(row.actor_name, row.director_name, row.writer_name, row.genre, row.country), axis=1)
        return movie_df['movie_sentence'].to_list()             

def find_similar_movie(movie_sent):
    model = Doc2Vec.load('models/exp3/model')
    model.infer_vector(movie_sentence)
    
def print_sim_list(sim_list):
    print(tabulate(sim_list, headers= ['Movie ID', 'Similarity']))
    
def data_processing(df, col_name):    
    regex = "\(.*?\)"
    df[col_name] = df[col_name].apply(lambda 
                                      row: re.sub(regex,'',row) if row != None  else row)
    df[col_name] = df[col_name].apply(lambda row: 
                                      row.lower().strip().replace(' ','_').split('|') if row != None   else row)
    df[col_name] = df[col_name].apply(lambda 
                                      row: [item.strip() for item in row] if row != None   else row)
    return df

def build_movie_sentence(actor,director,writer,genre,country):
    sent= []
    if actor != None:
        sent = sent + actor
    if director != None:
        sent = sent + director
    if writer != None:
        sent = sent + writer
    if genre != None:
        sent = sent + genre
    if country != None:
        sent = sent + country
    return sent

def isNaN(string):
    return string != string

#**************************************************************************************************

def main():
    query_movie_title = "enter"
    train_data_df = pd.read_csv('train_data.csv')
    model = Doc2Vec.load('model')
    headers=['Actor','Director', 'Writer', 'Genre', 'Country']
    while (query_movie_title != quit):
        sim_list=[]
        query_movie_title = ""
        
        query_movie_title = input("Enter your movie title to search or 'quit/q' to exit: ") 
        if (len(query_movie_title)==0):
            print("Empty input! please try again")
        else:
            system('cls') 
            if query_movie_title.lower() in ['quit','q']:
                break;


            print("Searching for movies similar to {}".format(query_movie_title))

            #Search for movie title in the current training data.
            #if found, retrieve movie_id
            #if not found, query LOD for the movie features
            query_movie_id = d_helper.find_movie_id_by_title(query_movie_title, train_data_df)

            if len(query_movie_id) == 0:    
                print("movie {} was not found. Retrieve movie information from LOD".format(query_movie_title))    
                query_movie_df = retrieve_features_from_lod(query_movie_title)

                if len(query_movie_df) >0:
                    print("Movie deatils found! ")
                    query_movie_df['genre']=None

                    print(tabulate(query_movie_df[['actor_name','director_name','writer_name','genre','country']], headers= headers))

                    movie_sentence = get_movie_sentence(query_movie_df) 
                    movie_sentence= movie_sentence[0]
                    infer_vector = model.infer_vector(movie_sentence)
                    sim_list= model.docvecs.most_similar([infer_vector])

                else:
                    print("Movies details were not found!! Try different movie")
            else:
                print("movie {} was found in local database. Searching for similar movie".format(query_movie_title))
                sim_list = model.docvecs.most_similar(query_movie_id)

            if len(sim_list) == 0 :
                 print("Error finding similar movie! please try again.")
            else:
                print_sim_list(sim_list)
            
if __name__ == "__main__":
    main()