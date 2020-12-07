import re
def find_movie_id_by_title(title,movies_df):
    return list(movies_df[movies_df['title'].str.lower() == title.lower()].movie_id)


def find_movie_sent_by_title(title,movies_df):
    return list(movies_df[movies_df['title'].str.lower() == title.lower()].movie_sentence)

def find_movie_sent_by_id(movie_id, movies_df):
    return list(movies_df[movies_df['movie_id'].str.lower() == movie_id.lower()].movie_sentence)[0]


def find_movie_genre_by_id(movie_id,movies_df):
    return movies_df[movies_df['movie_id'].str.lower() == movie_id.lower()].genre

def find_movie_title_by_id(movie_id, movies_df):
    return movies_df[movies_df['movie_id'].str.lower() == movie_id.lower()].title

def find_movie_by_id(movie_id,movies_df):
    return movies_df[movies_df['movie_id'].str.lower() == movie_id.lower()]

def find_actors_by_movie_id(movie_id, movies_df):
    return movies_df[movies_df['movie_id'].str.lower() == movie_id.lower()].actor_name.to_list()
    
def find_movies_by_col_value(col_name, col_value, train_data_df):
    df= train_data_df.loc[train_data_df.apply(lambda row: True if col_value in row[col_name] else False, axis=1)]
    return df.movie_id
    

def find_actors_vectors(actors):
    actors_vectors=[]
    for name in actors:
        actors_vectors.append(words_vectors[name])
    return(actors_vectors)

def build_sentence_from_col(actor_name, genre_id, director_name,writer_name,country_id):
    sent = []
    if actor_name is not None:
        (sent.append(item) for item in actor_name)
    if genre_id is not None:
        (sent.append(item) for item in genre_id)
    if director_name is not None:
        for item in director_name:
            sent.append(item)        
    if writer_name is not None:
        for item in writer_name:
            sent.append(item)
    if country_id is not None:
        for item in country_id:
            sent.append(item)
    
    return list(set(sent))

def validate_model_infrence(movie_id, movie_sentence, movies_df):
    found= Fals
    sub_sent=[]
    
    results={}
    if (len(movie_sentence) >1):
        random.seed(4)
        random.shuffle(movie_sentence)
        sub_sent_size = len(movie_sentence) // 2
        sub_sent= movie_sentence[0: sub_sent_size]
        infered_movie = model.infer_vector(sub_sent)
        similar_to_infered = docs_vectors.most_similar([infered_movie], topn=5, )        
        for idx,item in enumerate(similar_to_infered):
            if item[0] == movie_id:  
                found= True
                results = {
                    'movie_id':movie_id,                
                    'sampled_sent': sub_sent,
                    'rank' : idx+1,
                    'similarity' : similar_to_infered[idx][1]
                }
                
    
    if (found == False):
        results={
                 'movie_id':movie_id,                
                'sampled_sent': sub_sent,
                'rank' : None,
                'similarity' : None
        }
    return(pd.Series(results))

def print_similar_movies_sentence(similar_movies,df):
    for id, similarity in similar_movies:
        print("similarity_score {}".format(similarity))  
        print(df.find_movie_sent_by_id(id))
        print('-' * 50)
        
def calculate_genre_dist(data_df):
    #Genre statistics
    genres = []
    genres_list = data_df.genre.values

    for genre in genres_list:
        genres = genres + genre
    genres_names_list = set(genres)

    all_genres=[]
    for g in tqdm(genres_names_list):
        cnt = data_df.genre.apply(lambda genres: 1 if g in genres else 0 )
        all_genres.append({'Genre':g, 'Count':sum(cnt)})
    genres_df = pd.DataFrame(all_genres)
    genres_df= genres_df.sort_values(by=['Count'],ascending=False)
    genres_df ['Genre']= genres_df.Genre.str.upper()
    display(genres_df[['Genre','Count']])

def data_processing(df, col_name):    
    regex = "\(.*?\)"
    df[col_name] = df[col_name].apply(lambda 
                                      row: re.sub(regex,'',row) if isNaN(row)== False  else row)
    df[col_name] = df[col_name].apply(lambda row: 
                                      row.lower().strip().replace(' ','_').split('|') if isNaN(row)== False  else row)
    df[col_name] = df[col_name].apply(lambda 
                                      row: [item.strip() for item in row] if isNaN(row)== False  else row)
    return df

def build_movie_sentence(actor,director,writer,genre,country):
    return list(set(actor+director+writer+genre+country))

def isNaN(string):
    return string != string