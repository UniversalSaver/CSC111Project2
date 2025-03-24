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


def create_database() -> None:
    """
    Creates a new file with the path 'DATABASE_NAME' and creates the necessary tables and such to act as a graph

    If a database with that name already exists, then delete it, then recreate. This is to ensure the database has
    precisely the wanted data.
    """
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)

    db = sql.connect(DATABASE_NAME)

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
                FOREIGN KEY(movie_id) REFERENCES movie(id),
                FOREIGN KEY(actor_id) REFERENCES actor(id))""")

    with open(ID_TO_ACTOR) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['nconst', 'primaryName', 'birthYear', 'deathYear', 'primaryProfession',
                                'knownForTitles']:
            raise FileFormatError

        for line in reader:
            # print(f'"{line[0]}", "{line[1]}"')
            cur.execute("""
                INSERT INTO actor VALUES
                    (?, ?)
            """, (line[0], line[1]))
        db.commit()

    with open(ID_TO_MOVIE) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'isAdult', 'startYear',
                                'endYear', 'runtimeMinutes', 'genres']:
            raise FileFormatError

        for line in reader:
            cur.execute("""
                INSERT INTO movie VALUES
                    (?, ?)
            """, (line[0], line[2]))
        db.commit()

    with open(MOVIE_TO_ACTOR) as file:
        reader = csv.reader(file, delimiter='\t')

        if not next(reader) == ['tconst', 'ordering', 'nconst', 'category', 'job', 'characters']:
            raise FileFormatError

        for line in reader:
            if line[3] == 'actor':
                # print(line[0])
                cur.execute("""
                    INSERT INTO edge VALUES
                        (?, ?)
                """, (line[0], line[2]))
        db.commit()

    cur.close()
    db.close()


if __name__ == '__main__':
    create_database()
