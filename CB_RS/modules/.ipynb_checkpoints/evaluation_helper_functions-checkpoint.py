import pandas as pd
import decimal
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from tabulate import tabulate
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import movies_df_helper_functions as helper_fn

from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import SmoothingFunction
import gensim.models.doc2vec
import gensim
from gensim.models.doc2vec import Doc2Vec, TaggedDocument




decimal.getcontext().rounding = decimal.ROUND_DOWN

def calculate_rank_score(model, test_data, top):
    
    score_list=[]

    score_per_movie_group=[]

    for idx, movies_group in enumerate(test_data):
        score= 0
        #print(movies_group)
        for movie in movies_group:
            sims = model.docvecs.most_similar([movie], topn=top)
            for i in range(len(sims)):
                movie_id= sims[i][0]
                if movie_id in movies_group:
                    score = score + (top - i)
        movie_group_score = {'group_id': movie, 'group_score': score}
        score_list.append(movie_group_score)
        
    return score_list

def sum_scores(score_list):
    total_score = 0
    for score in score_list:
        total_score= total_score + score['group_score']
    return total_score

def calculate_model_rank_score(model, test_data, top):
    score_list = calculate_rank_score(model, test_data, top)
    return sum_scores(score_list)

def calculate_model_bleu_score(model, test_data, train_data_df, top):
    score_list=[]
    for idx, movies_group in enumerate(test_data):
        bleu_score = 0
        for movie in movies_group:
            sims = model.docvecs.most_similar([movie], topn=top)
            
            score_results = calculate_BLEU_score(movie,sims, train_data_df)
            bleu_score = bleu_score + score_results[0]
        score_list.append(bleu_score/len(movies_group))
    return sum(score_list)/len(score_list)

def calculate_BLEU_score(anchor_movie, sim_list, df):
    sim_movies= [sim[0] for sim in sim_list]
    b_score=[]
    print_list=[]
    cand_text= [helper_fn.find_movie_sent_by_id(movie_id, df) for movie_id in sim_movies]
    ref_text= helper_fn.find_movie_sent_by_id(anchor_movie, df)
    smooth_fn= SmoothingFunction().method4
    for idx,text in enumerate(cand_text):
        score= sentence_bleu([ref_text],text , weights=(1,0,0,0), smoothing_function= smooth_fn)
        b_score.append(round(score,2))
        title = df[df['movie_id'] == sim_list[idx][0]].title.values[0]
        print_list.append([title,round(score,2)])
        
    final_score=round(sum(b_score)/len(sim_list),2)
    print_list.append(['Average BLEU Score', final_score])
    
    return [final_score, print_list]

def model_parameters_search(train_data, test_data, param_list, train_data_df, top):
    models_scores= []
    for params in param_list:
        print("training model with the parameters {}".format(params))
        model = None
        try:
            #configure the model with parameters from the search parms list

            #load model
            #model = Doc2Vec.load('C:/Users/rania\OneDrive/AI Master/Project/Python_Code/Final_Code/YAGO_DBPEDIA_ML_DATA/models/baseline_exp/model')
            model = Doc2Vec(train_data,
                          dm=params['dm'], 
                          vector_size=params['vector_size'], 
                          window=params['window'], 
                          min_count=params['min_count'], 
                          epochs= params['epochs'], 
                          hs=params['hs'],
                          ns_exponent = params['ns_exponent'],
                          dbow_words=params['dbow_words'],
                          negative = params['negative'])

            params['rank_score'] = calculate_model_rank_score(model, test_data,top)
            params['bleu_score'] = calculate_model_bleu_score(model, test_data, train_data_df,top)
            #params['model'] = model
            models_scores.append(params)
            score_doc2vec = pd.DataFrame(models_scores)
            score_doc2vec.to_csv('model_score_dm_0.csv', index=False)
        except Exception as ex:
            print(f'An exception occured while trying to evaluate the model with the params {params} raised exception: {ex}')
            continue
    return models_scores

def build_movie_sequel_test_data(train_df, titles_list):
    test_data_list = []
    for title in titles_list:
        
        movies_list = find_movie_sequel(train_df, title)
        if movies_list is not None:
            test_data_list.append(movies_list)
        #print("find movies with titles matching: {}".format(title))
        #print("{}".format(movies_list), sep='\n')
    return test_data_list   

def find_movie_sequel(df, movie_name):
    movie_name_regex= '^' + movie_name + "(.*)$"
    matched_movies = df[df['title'].str.match(movie_name_regex.lower())]
    return matched_movies.movie_id.values.tolist() if len(matched_movies) >0 else None

def calculate_self_similarity(model, train_data):
    ranks = []
    second_ranks = []
    model_length = len(model.docvecs)
    for movie in tqdm(train_data):
        movie_id = movie.tags[0]
        movie_words= movie.words
        inferred_vector = model.infer_vector(movie_words)
        sims = model.docvecs.most_similar([inferred_vector], topn= model_length)
        rank = [idx for idx, sim in sims].index(movie_id)
        ranks.append(rank)
        second_ranks.append(sims[1])        
    return ranks, second_ranks


def calculate_precision_data_sample(add_n, iter_num, movies_sample, movie_sent_dict, sim_treshold):
    #create dataframe to hold the precision results for the number of iter
    row_lable= ["precision"]
    col_label = []
    top_n=0
    for idx in range(iter_num):
        top_n = top_n + add_n
        col_label.append("top_" + str(top_n))
    precision_df= pd.DataFrame(index= row_lable, columns= col_label)
    #print(precision_df)
    
    precision_list=[]
    top_n= 0
    #loop the number of times in iter_num to generate topn for the sample movie
    for idx in range(iter_num):
        top_n= top_n + add_n
        #print("TOP N = {}".format(top_n))
        precision_list=[]
        #for topn 
        for target_movie_id in movies_sample:
            #print("find {} similar movies for movie_id {}".format(top_n,target_movie_id))
            topn_list = model.docvecs.most_similar([target_movie_id], topn= top_n)
            #print("sim list size = {}".format(len(topn_list)))
           # print(topn_list)
            
            #calculate the precsion of the generated movie list for the target movie
            precision = calculate_precision(target_movie_id, topn_list, movie_sent_dict, sim_treshold)
            #print(precision)
            precision_list.append(precision)
            
           # print(precision_list)
        #calculate the average precision for the topn
        p_topn = sum(precision_list)/len(precision_list)
        #print("Average precision @{} ------- {}".format(top_n, p_topn))
        #precision_df[columns:"top_" + str(top_n), value:p_topn]
            
        precision_df.xs('precision')["top_" + str(top_n)]= round(p_topn ,2) *100
    
    return precision_df

def calculate_sent_ratio(target_sentence, sent):
    common_attr = set(target_movie_sent).intersection(sent)
    sim_ratio = len(common_attr)/len(sent)
    sim_ratio = round(sim_ratio,2)
    #sim_ratio = Levenshtein.ratio(' '.join(target_sentence), ' '.join(sent))
    sim_ratio = round(sim_ratio,2)
    return sim_ratio

def calculate_precision(target_movie_id, sim_list, movie_sent_dict, treshold):
    relative_cnt=0
    precision= 0
    
    target_sent = movie_sent_dict[target_movie_id]
         
    for sim in sim_list:
        sent = movie_sent_dict[sim[0]] 
        sim_ratio = calculate_sent_ratio(target_sent, sent)    
        if (sim_ratio >= treshold):
            relative_cnt +=1        

    precision= relative_cnt/len(sim_list)   
    return precision


                 
    

def print_sim_list(sim_list):
    print(tabulate(sim_list, headers= ['Movie ID', 'Similarity']))
    
def construct_titles_list(titles):
    all_titles= [title for title in titles]
    return all_titles

def find_common_attrs_in_list(movies_df, query_movie_id, search_movie_id_list, dataset):
    #titles for the movies to compare against are used as the column name
    cols= [title for title in search_movie_id_list]
    cols.insert(0, 'title')
    
    cnt_list=[]
    query_movie_title = movies_df[movies_df.movie_id== query_movie_id].title.values    

    for search_movie_id in search_movie_id_list:
        common_atrs_s = find_common_attrs(movies_df, query_movie_id, search_movie_id, dataset)
        cnt_list.append(common_atrs_s.loc['total_cnt'])
        
    cnt_list.insert(0,query_movie_title) 
    cnt_s = pd.Series(data= cnt_list, index= cols)
    return cnt_s

def find_common_attrs(movies_df,query_movie_id, search_movie_id, dataset):
    common_s=pd.DataFrame()
    query_movie= movies_df[movies_df.movie_id == query_movie_id]
    
    search_movie= movies_df[movies_df.movie_id == search_movie_id]
    
    common_actors= count_sim(query_movie, search_movie, 'actor_name')
    common_directors= count_sim(query_movie, search_movie, 'director_name')
    common_writers= count_sim(query_movie, search_movie, 'writer_name')
    common_genres= count_sim(query_movie, search_movie, 'genre')
    
    if dataset !='IMDb':
        common_country= count_sim(query_movie, search_movie, 'country')
        
    common_total_cnt =  common_actors+common_directors+common_writers+common_genres
    if dataset !='IMDb':
        common_total_cnt = common_total_cnt + common_country
        common_s = pd.Series([search_movie_id, common_actors, common_directors,common_writers,common_genres, common_country, common_total_cnt]
                         , index=['movie_id','actors_cnt', 'directors_cnt','writers_cnt','genres_cnt','country_cnt','total_cnt'])
    else:
        common_s = pd.Series([search_movie_id, common_actors, common_directors,common_writers,common_genres, common_total_cnt]
                         , index=['movie_id','actors_cnt', 'directors_cnt','writers_cnt','genres_cnt','total_cnt'])
    return common_s



def count_sim(query_movie, search_movie, col_name):
    
    search_list = search_movie[col_name].values[0] if len(search_movie[col_name]) >0 else []
    query_list= query_movie[col_name].values[0] if len(query_movie[col_name]) >0 else []
    common_list= set(query_list).intersection(search_list)
    return len(common_list)


#----------------------------------------
def get_common_attrs_val(movies_df,query_movie_id, search_movie_id, dataset):
    common_s=''
    data=''

    query_movie= movies_df[movies_df.movie_id == query_movie_id]
    
    search_movie= movies_df[movies_df.movie_id == search_movie_id]
    
    common_actors= get_common_val_for_feature(query_movie, search_movie, 'actor_name')
    common_directors= get_common_val_for_feature(query_movie, search_movie, 'director_name')
    common_writers= get_common_val_for_feature(query_movie, search_movie, 'writer_name')
    common_genres= get_common_val_for_feature(query_movie, search_movie, 'genre')
    if dataset != 'IMDb':
        common_country= get_common_val_for_feature(query_movie, search_movie, 'country')
        common_s = pd.Series([search_movie_id, common_actors, common_directors,common_writers,common_genres, common_country]
                             , index=['movie_id','actors_cnt', 'directors_cnt','writers_cnt','genres_cnt','country_cnt'])
        
        data = {'movie_id': [search_movie_id] ,'common_actors': [common_actors],
        'common_directors':[common_directors], 'common_writers': [common_writers],
        'common_genres': [common_genres],'common_country':[common_country]
       }
        cols= ['movie_id', 'common_actors', 'common_directors','common_writers','common_genres', 'common_country']
    else:
        common_s = pd.Series([search_movie_id, common_actors, common_directors,common_writers,common_genres]
                             , index=['movie_id','actors_cnt', 'directors_cnt','writers_cnt','genres_cnt'])
    
        data = {'movie_id': [search_movie_id] ,'common_actors': [common_actors],
                'common_directors':[common_directors], 'common_writers': [common_writers],
                'common_genres': [common_genres]
               }
        cols= ['movie_id', 'common_actors', 'common_directors','common_writers','common_genres']
    print(len(cols))
    print(len(data))
    return pd.DataFrame(data= data, columns=cols)
                        

def get_common_val_for_feature(query_movie, search_movie, col_name):
    
    search_list = search_movie[col_name].values[0] if len(search_movie[col_name]) >0 else []
    query_list= query_movie[col_name].values[0] if len(query_movie[col_name]) >0 else []
    common_list= set(query_list).intersection(search_list)
    return common_list

def find_common_attrs_val_in_list(movies_df, query_movie_id, search_movie_id_list):
    #titles for the movies to compare against are used as the column name
    cols= [title for title in search_movie_id_list]
    cols.insert(0, 'title')
    
    cnt_list=[]
    query_movie_title = movies_df[movies_df.movie_id== query_movie_id].title.values    

    for search_movie_id in search_movie_id_list:
        common_atrs_s = find_common_attrs(movies_df, query_movie_id, search_movie_id)
        cnt_list.append(common_atrs_s.loc['total_cnt'])
        
    cnt_list.insert(0,query_movie_title) 
    cnt_s = pd.Series(data= cnt_list, index= cols)
    return cnt_s
 
def get_common_attrs_cnt_for_sim_list(train_data_df, similar_movies_list, query_movie_id, dataset) :  
    #Count common attributes between the query movie and the movies in the result list
    query_movie_title = helper_fn.find_movie_title_by_id(query_movie_id, train_data_df)
    query_movie_title = query_movie_title.values.tolist()[0]
    #calculate and print the common attribure matrix between the query movie and the movies in the result list
    common_attr_matrix = find_common_attrs_in_list(train_data_df, query_movie_id, similar_movies_list,dataset)

    attrs_df = pd.DataFrame({'Title':common_attr_matrix.index, 'Common Features Count':common_attr_matrix.values})
    attrs_df= attrs_df.drop(0).reset_index(drop= True)
    
    
    return attrs_df