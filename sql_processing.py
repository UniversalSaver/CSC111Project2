"""
A file that does all the necessary SQL processing for the data set. Creates an SQL database that acts like a graph

This is created because the raw graph takes upwards of 15 GB of RAM to use, and that is simply too much.
"""
import sqlite3 as sql
import csv
import os

MAIN_DATABASE = 'data_files/all_data.db'

ID_TO_ACTOR = 'data_files/name.basics.tsv'
ID_TO_MOVIE = 'data_files/title.basics.tsv'
MOVIE_TO_ACTOR = 'data_files/title.principals.tsv'
RATINGS = 'data_files/title.ratings.tsv'

DATABASE_NAME = 'data_files/actors_and_movies.db'


class FileFormatError(Exception):
    """
    An error raised during file reading if the format of the file is incorrect
    """

    def __str__(self) -> str:
        """
        Return a string representation of this exception
        """
        return "The file attempted to be read is not in the correct format"


def compile_full_data(main_database: str) -> str:
    """
    Will create a database of ALL the data in necessary files

    However this is FAR too big, so we will be working with a smaller database

    Returns the name of the database if it successfully created it

    If the database already exists, returns an empty string
    """
    if main_database == '':
        main_database = MAIN_DATABASE

    if os.path.exists(main_database):
        return ''

    with sql.connect(main_database) as connection:
        cursor = connection.cursor()

        with open(ID_TO_ACTOR) as file:
            reader = csv.reader(file, delimiter='\t')

            header = next(reader)

            cursor.execute(f"""
            CREATE TABLE actor(
            {header[0]} PRIMARY_KEY, {header[1]}, {header[2]}, {header[3]}, {header[4]}, {header[5]}
            )
            """)
            cursor.execute("""CREATE UNIQUE INDEX idx_actor_id ON actor(nconst)""")

            for line in reader:

                cursor.execute("""
                INSERT INTO actor VALUES
                (?, ?, ?, ?, ?, ?)
                """, tuple(line))
            connection.commit()

        with open(ID_TO_MOVIE) as file:
            reader = csv.reader(file, delimiter='\t')

            header = next(reader)

            cursor.execute(f"""
                CREATE TABLE movie(
                {header[0]} PRIMARY_KEY, {header[1]}, {header[2]}, {header[3]}, {header[4]}, {header[5]},
                {header[6]}, {header[7]}, {header[8]}
                )
                """)
            cursor.execute("""CREATE UNIQUE INDEX idx_movie_id ON movie(tconst)""")

            for line in reader:
                if len(line) == 9:
                    cursor.execute("""
                    INSERT INTO movie VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(line))
            connection.commit()

        with open(MOVIE_TO_ACTOR) as file:
            reader = csv.reader(file, delimiter='\t')

            header = next(reader)

            cursor.execute(f"""
                CREATE TABLE connections(
                {header[0]}, {header[1]}, {header[2]}, {header[3]}, {header[4]}, {header[5]}
                )
                """)
            cursor.execute("""CREATE INDEX idx_connections ON connections(tconst, nconst)""")

            for line in reader:
                if len(line) == 6:
                    # print(line)
                    cursor.execute("""
                    INSERT INTO connections VALUES
                    (?, ?, ?, ?, ?, ?)
                    """, tuple(line))
            connection.commit()

        with open(RATINGS) as file:
            reader = csv.reader(file, delimiter='\t')

            header = next(reader)

            cursor.execute(f"""
                CREATE TABLE ratings(
                {header[0]} PRIMARY_KEY, {header[1]}, {header[2]}
                )
                """)

            for line in reader:
                cursor.execute("""
                INSERT INTO ratings VALUES
                (?, ?, ?)
                """, tuple(line))
            connection.commit()

        cursor.close()
    return main_database


def create_database(database_name: str) -> str:
    """
    Creates a database, and returns the file path if it was able to, but an empty if there was already a database
    """
    if database_name == '':
        database_name = DATABASE_NAME

    if os.path.exists(database_name):
        return ''
    else:
        connection = sql.connect(database_name)
        connection.close()
        return database_name


def create_movie_table(creation_database_name: str, main_database: str, number_of_movies: int) -> str:
    """
    Loads a number of random movies from the database. These movies will not be guaranteed to be connected. But that's
    fine, the point of this is to say that they probably are for a relatively small count. This assumes there is no
    such table in the database already

    Returns the name of the main database if the function ran without issue, but if the function could not find one of
    the files, returns an empty string.

    Preconditions:
        - number_of_movies is a valid positive integer
    """
    if main_database == '':
        main_database = MAIN_DATABASE

    if not os.path.exists(main_database) or not os.path.exists(creation_database_name):
        return ''

    insertion_connection = sql.connect(creation_database_name)
    insertion_cursor = insertion_connection.cursor()

    main_connection = sql.connect(main_database)
    main_cursor = main_connection.cursor()

    insertion_cursor.execute("""CREATE TABLE movie(
                    id PRIMARY KEY, title, isAdult, startYear, endYear,
                    runtimeMinutes, genre, averageRating, numVotes)""")
    insertion_cursor.execute("""CREATE UNIQUE INDEX idx_movie_id ON movie(id)""")
    insertion_connection.commit()

    movies = main_cursor.execute("""SELECT movie.tconst, primaryTitle, isAdult, startYear, endYear, runtimeMinutes,
            genres, averageRating, numVotes FROM movie JOIN ratings ON movie.tconst = ratings.tconst
            WHERE titleType = 'movie' ORDER BY RANDOM() LIMIT ?""", (number_of_movies,)).fetchall()

    insertion_cursor.executemany("""INSERT INTO movie VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", movies)
    insertion_connection.commit()

    insertion_cursor.close()
    insertion_connection.close()

    main_cursor.close()
    main_connection.close()

    return main_database


def create_actor_table(creation_database_name: str, main_database: str) -> None:
    """
    Creates the actor table and edge table from the main_database in creation_database_name. Only adds actors that act
    in the movies already in the database. This will also add the necessary connections between actors and movies.

    Preconditions:
        - creation_database_name is a valid database that has its movies
        - main_database is a valid main database
    """
    insertion_connection = sql.connect(creation_database_name)
    insertion_cursor = insertion_connection.cursor()

    main_connection = sql.connect(main_database)
    main_cursor = main_connection.cursor()

    insertion_cursor.execute("""CREATE TABLE actor(id PRIMARY_KEY, name, birthYear, deathYear, actorOrActress)""")
    insertion_cursor.execute("""CREATE UNIQUE INDEX idx_actor_id ON actor(id)""")

    insertion_cursor.execute("""CREATE TABLE edge(
                movie_id,
                actor_id,
                FOREIGN KEY(movie_id) REFERENCES movie(id),
                FOREIGN KEY(actor_id) REFERENCES actor(id))""")
    insertion_cursor.execute("""CREATE INDEX idx_edge ON edge(movie_id, actor_id)""")
    insertion_connection.commit()

    movies = insertion_cursor.execute("""SELECT id FROM movie""").fetchall()

    inserted_actors = []
    inserted_edges = []
    for movie in movies:
        actors = main_cursor.execute("""SELECT actor.nconst, primaryName, birthYear, deathYear, primaryProfession
                FROM actor
                JOIN connections ON actor.nconst = connections.nconst
                WHERE tconst = ?""", movie).fetchall()

        inserted_edges += main_cursor.execute("""SELECT tconst, nconst
                FROM connections WHERE tconst = ? AND (category = 'actor' OR category = 'actress')""", movie).fetchall()

        for actor in actors:
            if 'actor' in actor[4]:
                inserted_actors.append(actor[0:4] + ('M',))
            elif 'actress' in actor[4]:
                inserted_actors.append(actor[0:4] + ('F',))

    insertion_cursor.executemany("""INSERT OR IGNORE INTO actor VALUES(?, ?, ?, ?, ?)""", inserted_actors)
    insertion_cursor.executemany("""INSERT INTO edge VALUES(?, ?)""", inserted_edges)
    insertion_connection.commit()

    insertion_cursor.close()
    insertion_connection.close()

    main_cursor.close()
    main_connection.close()


if __name__ == '__main__':
    import python_ta

    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['E1136'],
    #     'extra-imports': ['csv', 'networkx', 'sqlite3', 'collections', 'matplotlib.pyplot', 'os'],
    #     'allowed-io': ['compile_full_data', 'create_movie_table', 'create_actor_table', 'create_database'],
    #     'max-nested-blocks': 4
    # })

    if input("Would you like to make a Main Database which has all the information from the downloaded files? (Y/N) "
             "(Note this takes a while)").strip().lower() == 'y':
        if not (os.path.exists(ID_TO_ACTOR) and os.path.exists(ID_TO_MOVIE) and os.path.exists(MOVIE_TO_ACTOR)
                and os.path.exists(RATINGS)):
            print("Please make sure you have name.basics.tsv, title.basics.tsv, title.principals.tsv, title.ratings.tsv"
                  " in the data_files folder...")
        else:
            main_database_location = input("Where would you like to store the Main Database? ")
            main_database_location = compile_full_data(main_database_location)
            if main_database_location == '':
                print("It seems you already have a database there. We won't make you wait through making another one!")
            else:
                print(f"Made a Main Database at {main_database_location}")

    inputted_main_database = input("What would you like to get the data from? ")
    inputted_created_database = input("Where would you like your new database? ")

    inputted_created_database = create_database(inputted_created_database)

    if inputted_created_database == '':
        print("A database with that name already exists, please run the program again and input a new name.")
    else:
        inputted_number_of_actors = input("How many movies would you like data from? ").strip()

        inputted_main_database = create_movie_table(inputted_created_database,
                                                    inputted_main_database, int(inputted_number_of_actors))
        if inputted_main_database == '':
            print("Couldn't find the main database, please run the program again and try again")
        else:
            create_actor_table(inputted_created_database, inputted_main_database)
            print(f"Created a new database for graph traversing at {inputted_created_database}")

    # actor_id_to_name_file = input("What will your source of actor IDs to names be? ")
    # movie_id_to_name_file = input("What will your source of movie IDs to titles be? ")
    # actor_played_in_file = input("What will your source of actor to movie relations be? ")
    # ratings_file = input("What will your source of movie ratings be? ")
    # name_of_database = input("What would you like the database to be stored into? ")
    # create_weights = input("Would you like to create edge weights? (Y/N) ").lower().strip()
    #
    # if create_weights == 'y':
    #     create_weights = True
    # elif create_weights == 'n':
    #     create_weights = False
    # else:
    #     raise IOError
    #
    # if not create_database(actor_id_to_name_file, movie_id_to_name_file,
    #                        actor_played_in_file, ratings_file, name_of_database, create_weights):
    #     print("That database already existed, will not create a new database")
    # else:
    #     print("Have created a new data base in " + name_of_database + ".")
