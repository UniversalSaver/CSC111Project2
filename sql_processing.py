"""
A file that does all the necessary SQL processing for the data set. Creates an SQL database that acts like a graph

This is created because the raw graph takes upwards of 15 GB of RAM to use, and that is simply too much.
"""
import sqlite3 as sql
import csv
import os

ID_TO_ACTOR = 'data_files/name.basics.tsv'
ID_TO_MOVIE = 'data_files/title.basics.tsv'
MOVIE_TO_ACTOR = 'data_files/title.principals.tsv'

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


def create_database(id_to_actor: str, id_to_movie: str, movie_to_actor: str, ratings: str, database_name: str) -> bool:
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

    if os.path.exists(database_name):
        return False

    db = sql.connect(database_name)

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

    with open(id_to_actor) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['nconst', 'primaryName', 'birthYear', 'deathYear', 'primaryProfession',
                                'knownForTitles']:
            raise FileFormatError

        for line in reader:
            # print(line)
            if 'actor' in line[4] or 'actress' in line[4]:
                # print(f'"{line[0]}", "{line[1]}"')
                cur.execute("""
                    INSERT OR IGNORE INTO actor VALUES
                        (?, ?)
                """, (line[0], line[1]))
        db.commit()

    with open(id_to_movie) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'isAdult', 'startYear',
                                'endYear', 'runtimeMinutes', 'genres']:
            raise FileFormatError

        for line in reader:
            if 'movie' == line[1]:
                # print(line)
                cur.execute("""
                    INSERT INTO movie VALUES
                        (?, ?)
                """, (line[0], line[2]))
        db.commit()

    with open(movie_to_actor) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['tconst', 'ordering', 'nconst', 'category', 'job', 'characters']:
            raise FileFormatError

        for line in reader:
            if line[3] == 'actor' or line[3] == 'actress':
                # print(line[0])
                cur.execute("""
                    INSERT INTO edge VALUES
                        (?, ?, NULL)
                """, (line[0], line[2]))
        db.commit()

    with open(ratings) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['tconst', 'averageRating', 'numVotes']:
            raise FileFormatError

        for line in reader:
            cur.execute("""
                INSERT INTO rating VALUES
                    (?, ?, ?)
            """, (line[0], line[1], line[2]))
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

    if not create_database(actor_id_to_name_file, movie_id_to_name_file,
                           actor_played_in_file, ratings_file, name_of_database):
        print("That database already existed, will not create a new database")
    else:
        print("Have created a new data base in " + name_of_database + ".")
