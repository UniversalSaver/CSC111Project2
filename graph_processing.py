"""
The file where functions for processing the data will be.

# TODO - add copyright
"""
import networkx as nx
import sqlite3 as sql

ID_TO_ACTOR = 'data_files/name.basics.tsv'
ID_TO_MOVIE = 'data_files/title.basics.tsv'
MOVIE_TO_ACTOR = 'data_files/title.principals.tsv'


class FileFormatError(Exception):
    """
    An error raised during file reading if the format of the file is incorrect
    """
    def __str__(self):
        """
        Return a string representation of this exception
        """
        return "The file attempted to be read is not in the correct format"


class ActorGraph:
    """
    An abstract class that defines how the methods for the actual actor graphs should work
    """

    # Private Instance Attributes:
    #   - _actor_graph: A graph representing the actors in some way
    #   - _actors: A graph mapping actor IDs to the name
    #   - _movies: A graph mapping movie IDs to the title
    # TODO: Figure out what from this is necessary now that it's database based

    _actor_graph: nx.Graph
    _actors: dict[str, str]
    _movies: dict[str, str]
    _db_path: str

    def __init__(self, database_path: str) -> None:
        """
        Initializes the _actors and _movies attributes using the files

        Preconditions:
            - database_path refers to a valid sqlite3 database that has at least the tables "actor", "movie", and "edge"
        """
        # self._actors = {}
        # self._movies = {}
        # self._actor_graph = nx.Graph()
        self._db_path = database_path

        # with open(ID_TO_ACTOR) as file:
        #     reader = csv.reader(file, delimiter='\t')
        #
            # if not next(reader) == ['nconst', 'primaryName', 'birthYear', 'deathYear', 'primaryProfession',
            #                         'knownForTitles']:
        #         raise FileFormatError
        #
        #     for line in reader:
        #         self._actors[line[0]] = line[1]
        #
        # with open(ID_TO_MOVIE) as file:
        #     reader = csv.reader(file, delimiter='\t')
        #
            # if not next(reader) == ['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'isAdult', 'startYear',
            #                         'endYear', 'runtimeMinutes', 'genres']:
        #         raise FileFormatError
        #
        #     for line in reader:
        #         self._movies[line[0]] = line[2]

        # with open(MOVIE_TO_ACTOR) as file:
        #     reader = csv.reader(file, delimiter='\t')
        #
        #     if not next(reader) == ['tconst', 'ordering', 'nconst', 'category', 'job', 'characters']:
        #         raise FileFormatError
        #
        #     for line in reader:
        #         if line[3] == 'actor':
        #             self._actor_graph.add_edge(line[0], line[2])

    def shortest_path(self, actor1: str, actor2: str) -> list[str]:
        """
        Given two actors, return the shortest path between the actors
        """
        raise NotImplementedError

    def output_graph(self, actors: list[str], movies: list[str]):
        """
        Creates a new window with a graph induced by the given actors and movies.
        """
        raise NotImplementedError

    def get_actor_id(self, actor_name: str, played_in: str = '') -> str:
        """
        Given an actor's name, return their id.

        If there are multiple of the same actor, then can be given an optional parameter 'played_in' to specify a movie
        the actor has played in.

        Returns an empty string if the actor doesn't exist, or there are more than one actor that fit the description

        >>> a = ActorGraph('data_files/actors_and_movies.db')
        >>> a.get_actor_id('Kevin Bacon')
        ''
        >>> a.get_actor_id('Kevin Bacon', 'Space Oddity')
        'nm0000102'
        """
        with sql.connect(self._db_path) as connection:
            cursor = connection.cursor()
            if played_in == '':
                response = cursor.execute("""
                SELECT id FROM actor WHERE name = ?
                """, (actor_name,)).fetchall()

                if len(response) != 1:
                    return ''
                else:
                    return response[0][0]
            else:
                actors_response = cursor.execute("""
                SELECT id FROM actor WHERE name = ?
                """, (actor_name,)).fetchall()

                for actor in actors_response:
                    movies = cursor.execute("""
                    SELECT movie_id FROM edge WHERE actor_id = ?
                    """, (actor[0],)).fetchall()

                    for movie in movies:
                        if played_in == cursor.execute("""
                        SELECT title FROM movie WHERE id = ?
                        """, (movie[0],)).fetchone()[0]:
                            return actor[0]

            cursor.close()

    def get_adjacent_nodes(self, id: str) -> list[str]:
        """
        Given an actor or movie id, this function will return the adjacent nodes to that id using the database in
        _db_path

        Preconditions:
            - id is a valid actor or movie id
        """
        # TODO


class ShortestActorGraph(ActorGraph):
    """
    A class with the graph which will process the functions such as shortest_path or new_bacon
    """
    # Private Instance Attributes:
    #   - _actor_graph: A graph with actors as vertices, and movies two people have played in as edges. The actors are
    #                   represented as their IDs, and the edges have attributes as movie IDs

    _actor_graph: nx.MultiGraph

    def __init__(self) -> None:
        """
        Process the data from the constants and create a multigraph with nodes of actors, and edges as movies

        Preconditions:
            - The constants above refer to valid files
        """
        super().__init__()

    def shortest_path(self, actor1: str, actor2: str) -> list[str]:
        """
        Given two actor IDs, return the shortest path between two actors as a sequences of actors

        Preconditions:
            - The actors are in the graph
        """
        # TODO

    def movie_path(self, actor_path: list[str]) -> list[str]:
        """
        Given a path between two actors, find return a list of movies such that for every two consecutive actors in the
        the path, the returned list has a movie between them. This is due to two actors possibly playing in more than
        one movie together.

        This means the length of the returned list is one less than the length of the given path.

        Preconditions:
            - actor_path is a valid path
        """
        # TODO

    def output_graph(self, actors: list[str], movies: list[str]) -> None:
        """
        Creates a new window with an induced subgraph depending on the given actors and edges.

        TODO - Decide what this should take in and what Preconditions those things should have
        """
        # TODO


class WeightedActorGraph(ActorGraph):
    """
    A class very similar to ActorGraph, except the edges are weighted to funnel towards the most popular movie that is
    found. This allows for faster path-finding between two actors, but it is not guaranteed to find the shortest path.
    """

    # Private Instance Attributes:
    #   - _actor_graph: a graph with actors and movies as vertices. A movie and an actor will have an edge if the actor
    #                   has played in the movie. There are no edges between actors and no edges between movies. The
    #                   actors and movies are represented as their IDs. The edges will also have weights, which are how
    #                   far it is from _popular_movie
    #   - _popular_movie: A string containing the ID of a popular movie

    _actor_graph: nx.MultiGraph
    _popular_movie: str

    def __init__(self) -> None:
        """
        Process the data from the constants and create a
        """
        # TODO

    def shortest_path(self, actor1: str, actor2: str) -> list[str]:
        """
        Will find the shortest path between actor1 and actor2 by finding a path between the actors and popular_movie.
        The combined path can then be found and that will be a path between the two actors.
        """
        # TODO

    def output_graph(self, actors: list[str], movies: list[str]):
        """
        Will create a new window with a graph induced by the given actors and movies, color-coding them to show which is
        which.
        """
        # TODO
