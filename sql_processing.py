"""
A file that does all the necessary SQL processing for the data set. Creates an SQL database that acts like a graph

This is created because the raw graph takes upwards of 15 GB of RAM to use, and that is simply too much.
"""
import sqlite3 as sql
import csv
import os
from collections import deque

ID_TO_ACTOR = 'data_files/name.basics.tsv'
ID_TO_MOVIE = 'data_files/title.basics.tsv'
MOVIE_TO_ACTOR = 'data_files/title.principals.tsv'
RATINGS = 'data_files/title.ratings.tsv'

DATABASE_NAME = 'data_files/actors_and_movies.db'


class FileFormatError(Exception):
    """
    An error raised during file reading if the format of the file is incorrect
    """

    def __str__(self):
        """
        Return a string representation of this exception
        """
        return "The file attempted to be read is not in the correct format"


def create_database(id_to_actor: str, id_to_movie: str, movie_to_actor: str, ratings: str, database_name: str,
                    create_weights: bool) -> bool:
    """
    Creates a new file with the path 'DATABASE_NAME' and creates the necessary tables and such to act as a graph

    If a database with that name already exists, then delete it, then recreate. This is to ensure the database has
    precisely the wanted data.

    >>> create_database('small_data_files/actor_names_small.tsv', 'small_data_files/movie_names_small.tsv', 'small_data_files/movie_to_actor_small.tsv', 'small_data_files/ratings_small.tsv', 'small_data_files/small_db.db')
    True
    """
    if id_to_actor == '':
        id_to_actor = ID_TO_ACTOR
    if id_to_movie == '':
        id_to_movie = ID_TO_MOVIE
    if movie_to_actor == '':
        movie_to_actor = MOVIE_TO_ACTOR
    if database_name == '':
        database_name = DATABASE_NAME
    if ratings == '':
        ratings = RATINGS

    if os.path.exists(database_name):
        return False

    db = sql.connect(database_name)

    db.execute("""PRAGMA journal_mode = OFF""")
    db.commit()

    cur = db.cursor()

    cur.execute("""CREATE TABLE actor(
                id PRIMARY KEY,
                name)""")
    cur.execute("""CREATE TABLE movie(
                id PRIMARY KEY,
                title)""")
    cur.execute("""CREATE TABLE edge(
                movie_id,
                actor_id,
                distance_from_popular,
                FOREIGN KEY(movie_id) REFERENCES movie(id),
                FOREIGN KEY(actor_id) REFERENCES actor(id))""")
    cur.execute("""CREATE TABLE rating(
                id PRIMARY KEY,
                rating,
                votes
    )""")
    cur.execute("""CREATE UNIQUE INDEX idx_actor_id ON actor(id)""")
    cur.execute("""CREATE UNIQUE INDEX idx_movie_id ON movie(id)""")
    cur.execute("""CREATE INDEX idx_edge ON edge(movie_id, actor_id)""")

    with open(id_to_actor) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['nconst', 'primaryName', 'birthYear', 'deathYear', 'primaryProfession',
                                'knownForTitles']:
            raise FileFormatError

        mass_insert_list = []

        for line in reader:
            # print(line)
            if 'actor' in line[4] or 'actress' in line[4]:
                # print(f'"{line[0]}", "{line[1]}"')
                mass_insert_list.append((line[0], line[1]))
        cur.executemany("""INSERT OR IGNORE INTO actor VALUES (?, ?)""", mass_insert_list)
        db.commit()

    with open(id_to_movie) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'isAdult', 'startYear',
                                'endYear', 'runtimeMinutes', 'genres']:
            raise FileFormatError

        mass_insert_list = []

        for line in reader:
            if 'movie' == line[1]:
                # print(line)
                mass_insert_list.append((line[0], line[2]))
        cur.executemany("""
                    INSERT INTO movie VALUES
                        (?, ?)
                """, mass_insert_list)
        db.commit()

    with open(movie_to_actor) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['tconst', 'ordering', 'nconst', 'category', 'job', 'characters']:
            raise FileFormatError

        mass_insert_list = []
        for line in reader:
            if line[3] == 'actor' or line[3] == 'actress':
                # print(line[0])
                mass_insert_list.append((line[0], line[2]))
        cur.executemany("""
            INSERT INTO edge VALUES
                (?, ?, NULL)
        """, mass_insert_list)
        db.commit()

    with open(ratings) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['tconst', 'averageRating', 'numVotes']:
            raise FileFormatError

        mass_insert_list = []

        for line in reader:
            mass_insert_list.append((line[0], line[1], line[2]))
        cur.executemany("""
            INSERT INTO rating VALUES
                (?, ?, ?)
        """, mass_insert_list)
        db.commit()

        if not create_weights:
            cur.close()
            db.close()
            return True

# Process the edge weights based on distance from the most popular movie in the database
    most_popular_movies = cur.execute("""
                        SELECT id FROM rating ORDER BY votes
                        """).fetchall()

    most_popular_movie = most_popular_movies[0]

    for movie in most_popular_movies:
        if cur.execute("""SELECT * FROM movie WHERE id = ?""", (movie[0],)).fetchone() is not None:
            most_popular_movie = movie[0]

    queue = deque()
    queue.append((most_popular_movie, 0))
    visited = set()
    visited.add(most_popular_movie)

    while queue:
        curr_path = queue.popleft()
        curr_node = curr_path[0]
        curr_distance = curr_path[1]
        print("Currently checking " + curr_node + " with a distance of " + str(curr_distance))

        if curr_node[0:2] == 'tt':
            actors = cur.execute("""
            SELECT actor_id FROM edge WHERE
            movie_id = ?
            """, (curr_node,)).fetchall()

            # Unpacks the list of tuples
            adjacent_nodes = {actor[0] for actor in actors}
        else:
            movies = cur.execute("""
            SELECT movie_id FROM edge WHERE
            actor_id = ?
            """, (curr_node,)).fetchall()

            # Unpacks the list of tuples
            adjacent_nodes = {movie[0] for movie in movies}

        mass_insert_list = []

        for adjacent in adjacent_nodes:
            # print(adjacent)
            if adjacent not in visited:
                if curr_node[0:2] == 'tt':
                    mass_insert_list.append((curr_distance, curr_node, adjacent))
                else:
                    mass_insert_list.append((curr_distance, adjacent, curr_node))
                visited.add(adjacent)
                queue.append((adjacent, curr_distance + 1))
        cur.executemany("""
                UPDATE edge
                SET distance_from_popular = ?
                WHERE movie_id = ? AND actor_id = ?
        """, mass_insert_list)
        db.commit()

    cur.close()
    db.close()
    return True


if __name__ == '__main__':
    actor_id_to_name_file = input("What will your source of actor IDs to names be? ")
    movie_id_to_name_file = input("What will your source of movie IDs to titles be? ")
    actor_played_in_file = input("What will your source of actor to movie relations be? ")
    ratings_file = input("What will your source of movie ratings be? ")
    name_of_database = input("What would you like the database to be stored into? ")
    create_weights = input("Would you like to create edge weights? (Y/N) ").lower().strip()

    if create_weights == 'y':
        create_weights = True
    elif create_weights == 'n':
        create_weights = False
    else:
        raise IOError

    if not create_database(actor_id_to_name_file, movie_id_to_name_file,
                           actor_played_in_file, ratings_file, name_of_database, create_weights):
        print("That database already existed, will not create a new database")
    else:
        print("Have created a new data base in " + name_of_database + ".")
