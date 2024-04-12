#
# Plans for the future:
#   1. Get searches to filter by genre. - DONE
#   2. Get searches to filter by rating.
#   3. Reformat front end to ask questions that will lead to a suggestion.
#           - Mentors need to explain to us how to do this.
#

from flask import Flask, render_template, request, redirect, url_for
import requests
import datetime
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendation', methods=['POST'])
def recommendation():
    if request.method == 'POST':
        genre = request.form['genre']
        min_rating = float(request.form['min_rating'])
        min_year = int(request.form['release_year'])
        # common_words = ['the', 'of', 'and', 'to', 'in', 'a', 'is', 'it', 'you', 'that', 'I', 'we', 'me']

        tmdb_api_key = '309a6b31fde795ba3283ca1bf5e9c22f' # TMDB API Key
        #  omdb_api_key = 'b1072873'  # OMDB API Key

        # Creates array where genre names will be stored
        genre_names = []

        # Search all titles from min year to current year and store them in search_results.
        search_results = search_titles(tmdb_api_key, '', min_year)

        # Maps genre numbers to genre names
        genres_translated = get_genre_names(tmdb_api_key)

        # For each result in search results...
        for result in search_results:
            # Change genre numbers attached to each movie into genre names
            genre_names.append(translate_genre_ids_to_names(result["genre_ids"], genres_translated))

            # for result in search_results:
            #     complete_results.append(result)

        #response = requests.get(omdb_url)

        movies_data, genre_names = filter_movies_by_genre(search_results, genre_names, genre)
        movies_data = filter_movies_by_min_rating(movies_data, min_rating)
        return render_template('recommendation.html', movies_data=movies_data, genres=genre_names)


def search_titles(api_key, search_query, min_year):
    current_year = datetime.datetime.now().year

    complete_results = []

    # For each year between minimum year and the current year...
    for i in range(min_year, current_year+1):
        # Make a request for a year of movies and store it in current_result
        url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&sort_by=popularity.desc&page=1&primary_release_year={i}&api_key={api_key}"
        response = requests.get(url)
        current_result = response.json().get('results', [])

        # for each result in the received results...
        for result in current_result:
            # Append the result to an array that will store the results from all the years
            complete_results.append(result)

    if response.status_code == 200:
        return complete_results
    else:
        return None

# This method gets the relationship between numerical genres and the names for the genres
def get_genre_names(api_key):
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()
    genres = {}
    for genre in data['genres']:
        genres[genre['id']] = genre['name']
    return genres

# This translates the array of numbered genres to the names for the genres
def translate_genre_ids_to_names(genre_ids, genre_names):
    return [genre_names[genre_id] for genre_id in genre_ids]


def filter_movies_by_genre(movies, genres, genre):
    filtered_movies = []
    filtered_genres = []

    # Iterate over both movies and genres at the same time using zip
    for movie, genre_list in zip(movies, genres):
        
        # For each genre in genre list, add the lowercase version to lowercase_genre_list
        lowercase_genre_list = [g.lower() for g in genre_list]
        
        # if the genre we are looking for is in the lowercase_genre_list...
        if genre.lower() in lowercase_genre_list:
            # Add the movie and its list of genres to the filtered arrays
            filtered_movies.append(movie)
            filtered_genres.append(genre_list)

    return filtered_movies, filtered_genres

def filter_movies_by_min_rating(movies, min_rating):
    filtered_movies = []
    
    # For each movie in the movies list...
    for movie in movies:
        # If the vote average for the movie exists and is higher than minimum rating...
        if movie.get('vote_average', '') != 'N/A' and float(movie.get('vote_average', 0)) >= min_rating:
            # Add the movie to the filtered list
            filtered_movies.append(movie)
    
    return filtered_movies

def filter_movies_by_min_year(movies, min_year):
    filtered_movies = []
    for movie in movies:
        if float(movie.get('Year', 0)) >= min_year:
            filtered_movies.append(movie)
    return filtered_movies

if __name__ == '__main__':
    app.run(debug=True)