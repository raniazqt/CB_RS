bad_lod_movies_info_query="""
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?pedia_movie ?yago_movie ?title ?writer_name ?director_name ?country ?genre

WHERE{
  ?pedia_movie rdf:type dbo:Film.
  ?yago_movie a schema:Movie.
  ?pedia_movie rdfs:label ?title.
  ?yago_movie rdfs:label ?title.
  FILTER (LANG(?title) = "en")
  
  #Writer from DBpedia
  OPTIONAL{?pedia_movie dbo:writer ?writer}.  
  OPTIONAL{?writer rdfs:label ?writer_name. FILTER (LANG(?writer_name) = "en")}.
     
  #Director from either YAGO or DBPedia
  OPTIONAL{?yago_movie schema:director ?director}.
  OPTIONAL{?pedia_movie dbo:director ?director}.
  
  #Director Name from either YAGO or DBPedia  
  OPTIONAL{?director rdfs:label ?director_name}. 
  OPTIONAL{?pedia_movie dbp:director ?director_name}.
  FILTER (LANG(?director_name) = "en")
  
  #Genre from YAGO
  OPTIONAL{?yago_movie schema:genre ?genre}.
  
  #Country from YAGO or DBpedia
  OPTIONAL{?yago_movie schema:countryOfOrigin ?country}.
  OPTIONAL{?pedia_movie dbo:country ?country}   
  
  FILTER (STR(LCASE(?title)) in (%s))
}
"""

lod_movies_info_query="""PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX schema: <http://schema.org/>
PREFIX dbp: <http://dbpedia.org/property/>

SELECT DISTINCT ?pedia_movie ?yago_movie ?title ?writer_name ?director_name

WHERE{
  ?pedia_movie rdf:type dbo:Film.
  ?pedia_movie owl:sameAs ?yago_movie.
  ?yago_movie a schema:Movie.
  
   #movie title
  OPTIONAL{
    ?yago_movie rdfs:label ?title.
    ?dbpedia foaf:name ?title.
    FILTER (LANG(?title) = "en")  	
  }
  
  #writer
  OPTIONAL{
    ?pedia_movie dbo:writer ?writer.  
    ?writer rdfs:label ?writer_name. 
    FILTER (LANG(?writer_name) = "en")
  }
  OPTIONAL{
    ?pedia_movie dbp:writer ?writer_name
  }
  
  #Director from either YAGO or DBPedia
  OPTIONAL{?yago_movie schema:director ?director.}
  OPTIONAL{?pedia_movie dbo:director ?director.}
  OPTIONAL{?director rdfs:label ?director_name. FILTER (LANG(?director_name) = "en")}
      

   OPTIONAL{
       ?pedia_movie dbp:director ?director_name.
  }
    
  #Genre from YAGO
  OPTIONAL{?yago_movie schema:genre ?genre}.
  
  #Country from YAGO
  OPTIONAL{
    ?yago_movie schema:countryOfOrigin ?country.
    ?pedia_movie dbp:country ?country.
    ?pedia_movie dbo:country ?country.
   }
  
  FILTER CONTAINS( STR(?yago_movie), "yago").      

  FILTER (STR(LCASE(?title)) in (%s))
  
}
"""

lod_actors_query ="""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?yago_movie ?pedia_movie ?title ?actor_name
WHERE{
  ?pedia_movie rdf:type dbo:Film.
  ?yago_movie owl:sameAs ?pedia_movie.
  ?yago_movie a schema:Movie. 
   #movie title
  ?yago_movie rdfs:label ?title.
  FILTER (LANG(?title) = "en")  
  
  #Actors from either YAGO or DBPedia
  OPTIONAL{?yago_movie schema:actor ?actor}.
  OPTIONAL{?pedia_movie dbo:starring ?actor}.
    
  #Actors Name from either YAGO or DBPedia  
  OPTIONAL{?actor rdfs:label ?actor_name . FILTER (LANG(?actor_name) = "en")}.
    
  FILTER CONTAINS( STR(?pedia_movie), "dbpedia.org/resource").      
  FILTER (STR(LCASE(?title)) in (%s))   
}"""

bad_lod_actors_query ="""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?pedia_movie ?yago_movie ?title ?actor# DISTINCT (COUNT(DISTINCT ?pedia_movie) AS ?cnt)#DISTINCT ?pedia_movie ?yago_movie ?title ?actor

WHERE{
  ?pedia_movie rdf:type dbo:Film.
  ?yago_movie rdf:type schema:Movie.
  ?pedia_movie rdfs:label ?title.
  ?yago_movie rdfs:label ?title.
  FILTER (LANG(?title) = "en")
  
  OPTIONAL {?pedia_movie dbo:starring ?actor}.
  OPTIONAL {?yago_movie schema:actor ?actor}.  
  OPTIONAL {?actor rdfs:label ?actor_name . FILTER (LANG(?actor_name) = "en")}.
  
  FILTER (STR(LCASE(?title)) in (%s))  
}

"""

dbpedia_movies_info_query="""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>


SELECT DISTINCT ?pedia_movie ?title ?writer_name ?director_name ?country

WHERE{
  ?pedia_movie rdf:type dbo:Film.

  #movie title
  ?pedia_movie foaf:name ?title.
  FILTER (LANG(?title) = "en")

  #writer
  OPTIONAL{
    ?pedia_movie dbo:writer ?writer.  
    ?writer rdfs:label ?writer_name. 
    FILTER (LANG(?writer_name) = "en")
  }.
  OPTIONAL{
    ?pedia_movie dbp:writer ?writer_name
  }
    
  #director
  OPTIONAL{
    ?pedia_movie dbo:director ?dbo_director.
    ?dbo_director rdfs:label ?director_name.    
    FILTER (LANG(?director_name) = "en")
  }
  OPTIONAL{
    ?pedia_movie dbp:director ?director_name
  }

  #country
  OPTIONAL{?pedia_movie dbp:country ?country}.
  OPTIONAL{?pedia_movie dbo:country ?country}.
  
  
  FILTER (STR(LCASE(?title)) in (%s))  
}

"""
dbpedia_movies_actors_query="""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>


SELECT DISTINCT ?pedia_movie ?title ?actor_name
WHERE{
  ?pedia_movie rdf:type dbo:Film.
  #movie title
  ?pedia_movie foaf:name ?title.
  FILTER (LANG(?title) = "en")
  #actor
  OPTIONAL{
    ?pedia_movie dbo:starring ?actor.
    ?actor rdfs:label ?actor_name.
    FILTER (LANG(?actor_name) = "en")
  }  
   FILTER (STR(LCASE(?title)) in (%s))  
}

"""
yago_movie_info_query="""
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>


SELECT DISTINCT ?yago_movie ?title ?director_name ?country ?genre

WHERE{
  ?yago_movie a schema:Movie.
  
  #movie title
  ?yago_movie rdfs:label ?title.
  FILTER (LANG(?title) = "en").
  #director
  OPTIONAL{
    ?yago_movie schema:director ?yago_director.
    ?yago_director rdfs:label ?director_name.    
    FILTER (LANG(?director_name) = "en")
  }
  #country
  OPTIONAL{?yago_movie schema:countryOfOrigin ?country_id}.
  BIND(if (BOUND(?country_id), STRAFTER (STR(?country_id),"yago-knowledge.org/resource/"), "") AS ?country). 
  #genre
  OPTIONAL{?yago_movie schema:genre ?genre_id } .
  BIND(if (BOUND(?genre_id), STRAFTER (STR(?genre_id),"yago-knowledge.org/resource/"),"") AS ?genre) .       
 
  FILTER (STR(LCASE(?title)) in (%s))  
}
"""

yago_movies_actors_query="""
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>


SELECT DISTINCT ?yago_movie ?title ?actor_name

WHERE{
  ?yago_movie a schema:Movie.
  #movie title
  ?yago_movie rdfs:label ?title.
  FILTER (LANG(?title) = "en")
    
  #actor
  OPTIONAL{
    ?yago_movie schema:actor ?yago_actor.
    ?yago_actor rdfs:label ?actor_name.    
    FILTER (LANG(?actor_name) = "en")
  }
 
  FILTER (STR(LCASE(?title)) in (%s))  
}
"""

dbpedia_query_by_title="""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo: <http://dbpedia.org/ontology/>


SELECT DISTINCT ?movie_id ?title ?writer_name ?director_name ?country ?actor_name

WHERE{
  ?pedia_movie rdf:type dbo:Film.
  BIND(STRAFTER (STR(?pedia_movie),"dbpedia.org/resource/") AS ?movie_id). 

  #movie title
  ?pedia_movie foaf:name ?title.
  FILTER (LANG(?title) = "en")

  #writer
  OPTIONAL{
    ?pedia_movie dbo:writer ?writer.  
    ?writer rdfs:label ?writer_name. 
    FILTER (LANG(?writer_name) = "en")
  }.
  OPTIONAL{
    ?pedia_movie dbp:writer ?writer_name
  }
    
  #director
  OPTIONAL{
    ?pedia_movie dbo:director ?dbo_director.
    ?dbo_director rdfs:label ?director_name.    
    FILTER (LANG(?director_name) = "en")
  }
  OPTIONAL{
    ?pedia_movie dbp:director ?director_name
  }
  #actor
  OPTIONAL{
    ?pedia_movie dbo:starring ?actor.
    ?actor rdfs:label ?actor_name.
    FILTER (LANG(?actor_name) = "en")
  }  

  #country
  OPTIONAL{?pedia_movie dbp:country ?country}.
  OPTIONAL{?pedia_movie dbo:country ?country}.
  
  
  FILTER (STR(LCASE(?title)) in (%s))  
}

"""

yago_query_by_title="""

PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>


SELECT DISTINCT ?movie_id ?title ?director_name ?country ?genre ?actor_name

WHERE{
  ?yago_movie a schema:Movie.
  
  #movie title
  ?yago_movie rdfs:label ?title.
  FILTER (LANG(?title) = "en").
  
  BIND(STRAFTER (STR(?yago_movie),"yago-knowledge.org/resource/") AS ?movie_id). 
  
  #director
  OPTIONAL{
    ?yago_movie schema:director ?yago_director.
    ?yago_director rdfs:label ?director_name.    
    FILTER (LANG(?director_name) = "en")
  }
  #country
  OPTIONAL{?yago_movie schema:countryOfOrigin ?country_id}.
  BIND(if (BOUND(?country_id), STRAFTER (STR(?country_id),"yago-knowledge.org/resource/"), "") AS ?country). 
  #genre
  OPTIONAL{?yago_movie schema:genre ?genre_id } .
  BIND(if (BOUND(?genre_id), STRAFTER (STR(?genre_id),"yago-knowledge.org/resource/"),"") AS ?genre) .   
  
     
  #actor
  OPTIONAL{
    ?yago_movie schema:actor ?yago_actor.
    ?yago_actor rdfs:label ?actor_name.    
    FILTER (LANG(?actor_name) = "en")
  }
 
 
  FILTER (STR(LCASE(?title)) in (%s))  
  
}

"""