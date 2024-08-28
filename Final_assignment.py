import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def fetch_movies(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

def extract_movie_data(soup):
    movie_data = []

    if soup:
        movie_names = soup.find_all('a', class_='ipc-title-link-wrapper')
        movie_ratings = soup.find_all('span', class_='sc-b189961a-1 kcRAsW')

        for name, rating in zip(movie_names, movie_ratings):
            movie_name = name.text.strip()

            rating_match = re.search(r'\d+\.\d+', rating.text)
            if rating_match:
                movie_rating_str = rating_match.group()
                try:
                    movie_rating = float(movie_rating_str)
                    movie_data.append((movie_name, movie_rating))
                except ValueError:
                    print(f"Could not convert rating '{movie_rating_str}' for movie '{movie_name}' to a float.")
            else:
                print(f"Could not find a valid rating for movie '{movie_name}'.")

    return movie_data

def save_to_csv(movies, filename="movies.csv"):
    df = pd.DataFrame(movies, columns=["Title", "Rating"])
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def load_movies(filename="movies.csv"):
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

def suggest_movies_by_genre(df, genre, min_rating=0):
    filtered_movies = df[df["Title"].str.contains(genre, case=False, na=False)]
    sorted_movies = filtered_movies[filtered_movies["Rating"] >= min_rating].sort_values(by="Rating", ascending=False)

    if not sorted_movies.empty:
        print(f"\nMovies found for genre '{genre}' with rating >= {min_rating}:")
        print(sorted_movies.to_string(index=False))
    else:
        print(f"No movies found for the given genre '{genre}' with rating >= {min_rating}.")

# Main program
url = "https://www.imdb.com/chart/moviemeter"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

soup = fetch_movies(url, headers)
movies = extract_movie_data(soup)

if movies:
    save_to_csv(movies)
    df_movies = load_movies()
    if df_movies is not None:
        genre = input("Enter a Movie title to get movie suggestions: ")
        try:
            min_rating = float(input("Enter the minimum rating (e.g., 7.5): "))
            suggest_movies_by_genre(df_movies, genre, min_rating)
        except ValueError:
            print("Please enter a valid number for the rating.")
else:
    print("No movies were found or an error occurred.")
