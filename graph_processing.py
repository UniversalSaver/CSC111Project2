"""
The file where functions for processing the data will be.

# TODO - add copyright
"""
import networkx as nx
import sqlite3 as sql
from collections import deque
import matplotlib.pyplot as plt

ID_TO_ACTOR = 'data_files/name.basics.tsv'
ID_TO_MOVIE = 'data_files/title.basics.tsv'
MOVIE_TO_ACTOR = 'data_files/title.principals.tsv'

# The number of nodes to add to each node in a path for context
RANDOM_NODE_COUNT = 3


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
        self._db_path = database_path

    def get_path(self, actor1: str, actor2: str) -> list[str]:
        """
        Given two actors, return the shortest path between the actors
        """
        raise NotImplementedError

    def _make_networkx_graph(self, path: list[str]) -> nx.Graph:
        """
        Given a path, creates a NetworkX graph using the nodes in the path. Also includes nodes branching from the path
        for visual comparison

        Preconditions:
            - path is a valid path in the database
        """
        nx_graph = nx.Graph()

        for node_index in range(len(path) - 1):
            current_node_name = self.get_name(path[node_index])
            adjacent_nodes = self.get_adjacent_nodes(path[node_index])

            adjacent_nodes.remove(path[node_index + 1])

            if path[node_index][0:2] == 'tt':
                nx_graph.add_node(current_node_name, color='salmon')
            else:
                nx_graph.add_node(current_node_name, color='bisque')
            nx_graph.add_edge(current_node_name, self.get_name(path[node_index + 1]))

            nodes_to_add = RANDOM_NODE_COUNT

            while nodes_to_add > 0 and len(adjacent_nodes) > 0:
                connected_node_id = adjacent_nodes.pop()
                connected_node_name = self.get_name(connected_node_id)
                if connected_node_id[0:2] == 'tt':
                    nx_graph.add_node(connected_node_name, color='salmon')
                else:
                    nx_graph.add_node(connected_node_name, color='bisque')
                nx_graph.add_edge(current_node_name, connected_node_name)
                nodes_to_add -= 1

        nx_graph.nodes[self.get_name(path[0])]['color'] = 'green'
        nx_graph.add_node(self.get_name(path[-1]), color='green')
        return nx_graph

    def output_graph(self, path: list[str]):
        """
        Creates a new window with a graph induced by the given actors and movies.

        Preconditions:
            - path is a valid path, and any two adjacent elements in the list are connected
            - path is a list of ids of actors and movies

        >>> s = ShortestActorGraph('small_data_files/small_db.db')
        >>> p = s.get_path(s.get_actor_id('Keanu Reeves'), s.get_actor_id('Cillian Murphy'))
        >>> s.output_graph(p)
        """
        nx_graph = self._make_networkx_graph(path)

        colours = [nx_graph.nodes[k]['color'] for k in nx_graph.nodes]

        nx.draw_networkx(nx_graph, node_color=colours)
        # plt.savefig('img.png')

    def get_name(self, id: str) -> str:
        """
        Given an id (Whether movie or actor) return a title or actor.

        Preconditions:
            - id is a valid actor or movie id
        """
        connection = sql.connect(self._db_path)
        cursor = connection.cursor()

        if id[0:2] == 'tt':
            name = cursor.execute("""SELECT title FROM movie WHERE id = ?""", (id,)).fetchone()[0]
        else:
            name = cursor.execute("""SELECT name FROM actor WHERE id = ?""", (id,)).fetchone()[0]
        cursor.close()
        connection.close()

        return name

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
        >>> s = ActorGraph('small_data_files/small_db.db')
        >>> s.get_actor_id('Leonardo DiCaprio')
        'nm0000138'
        """
        with sql.connect(self._db_path) as connection:
            cursor = connection.cursor()
            if played_in == '':
                response = cursor.execute("""
                SELECT id FROM actor WHERE name = ?
                """, (actor_name,)).fetchall()

                cursor.close()
                if len(response) != 1:
                    return ''
                else:
                    return response[0][0]
            else:
                list_of_actors = cursor.execute("""
                SELECT id FROM actor WHERE name = ?
                """, (actor_name,)).fetchall()

                for actor in list_of_actors:
                    movies_played_in = cursor.execute("""
                    SELECT movie_id FROM edge WHERE actor_id = ?
                    """, (actor[0],)).fetchall()

                    for movie in movies_played_in:
                        if played_in == cursor.execute("""
                        SELECT title FROM movie WHERE id = ?
                        """, (movie[0],)).fetchone()[0]:
                            cursor.close()
                            return actor[0]

            cursor.close()
            return ''

    def get_adjacent_nodes(self, given_id: str) -> set[str]:
        """
        Given an actor or movie id, this function will return the adjacent nodes to that id using the database in
        _db_path

        Preconditions:
            - id is a valid actor or movie id

        >>> a = ActorGraph('small_data_files/small_db.db')
        >>> a.get_adjacent_nodes('nm0000138') == {'tt1375666', 'tt0120338'}
        True
        >>> a.get_adjacent_nodes('tt1375666') == {'nm0000138', 'nm0330687', 'nm0680983', 'nm0913822', 'nm0362766', 'nm2438307', 'nm0614165', 'nm0000297', 'nm0182839', 'nm0000592'}
        True
        """
        with sql.connect(self._db_path) as connection:
            cursor = connection.cursor()
            if given_id[0:2] == 'tt':
                actors = cursor.execute("""
                SELECT actor_id FROM edge WHERE
                movie_id = ?
                """, (given_id,)).fetchall()

                # Unpacks the list of tuples
                cursor.close()
                return {actor[0] for actor in actors}
            else:
                movies = cursor.execute("""
                SELECT movie_id FROM edge WHERE
                actor_id = ?
                """, (given_id,)).fetchall()

                # Unpacks the list of tuples
                cursor.close()
                return {movie[0] for movie in movies}


class ShortestActorGraph(ActorGraph):
    """
    A class with the graph which will process the functions such as shortest_path or new_bacon
    """
    # Private Instance Attributes:
    #   - _actor_graph: A graph with actors as vertices, and movies two people have played in as edges. The actors are
    #                   represented as their IDs, and the edges have attributes as movie IDs

    _actor_graph: nx.MultiGraph

    def __init__(self, database_path) -> None:
        """
        Process the data from the constants and create a multigraph with nodes of actors, and edges as movies

        Preconditions:
            - The constants above refer to valid files
        """
        super().__init__(database_path)

    def get_path(self, actor1: str, actor2: str) -> list[str]:
        """
        Given two actor IDs, return the shortest path between two actors as a sequences of actors

        Returns an empty list if such a path does not exist

        Preconditions:
            - The actors are in the graph

        >>> s = ShortestActorGraph('small_data_files/small_db.db')
        >>> s.get_path('nm0000206', 'nm0000138') != []
        True
        # >>> a = ShortestActorGraph('data_files/actors_and_movies.db')
        # >>> a.shortest_path('nm0000206', 'nm0000138')
        """
        if actor1 == actor2:
            return [actor1]

        queue = deque()
        queue.append([actor1])
        visited = set()
        visited.add(actor1)

        while queue:
            curr_path = queue.popleft()
            curr_node = curr_path[-1]
            # print("Currently checking " + curr_node)

            # if curr_node == actor2:
                # return curr_path

            for adjacent in self.get_adjacent_nodes(curr_node):
                # print(adjacent)

                # Check for end-point
                if adjacent == actor2:
                    return curr_path + [adjacent]

                if adjacent not in visited:
                    visited.add(adjacent)
                    queue.append(curr_path + [adjacent])

        return []

    # def movie_path(self, actor_path: list[str]) -> list[str]:
    #     """
    #     Given a path between two actors, return a list of movies such that for every two consecutive actors in the
    #     the path, the returned list has a movie between them. This is due to two actors possibly playing in more than
    #     one movie together.
    #
    #     This means the length of the returned list is one less than the length of the given path.
    #
    #     Preconditions:
    #         - actor_path is a valid path
    #     """
    #     final_movie_path = []
    #
    #     for i in range(len(actor_path) - 1):
    #         actor1 = actor_path[i]
    #         actor2 = actor_path[i+1]
    #
    #         actor1_movies = self.get_adjacent_nodes(actor1)
    #         actor2_movies = self.get_adjacent_nodes(actor2)
    #
    #         for movie in actor1_movies:
    #             if movie in actor2_movies:
    #                 final_movie_path.append(movie)
    #                 break
    #
    #     return final_movie_path


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

    def __init__(self, db_path: str) -> None:
        """
        Creates a relation to the database with a path
        """
        super().__init__(db_path)

    def shortest_path(self, actor1: str, actor2: str) -> list[str]:
        """
        Will find the shortest path between actor1 and actor2 by finding a path between the actors and popular_movie.
        The combined path can then be found and that will be a path between the two actors.
        """
        # TODO


if __name__ == '__main__':
    s = ShortestActorGraph('small_data_files/small_db.db')
    p = s.get_path(s.get_actor_id('Keanu Reeves'), s.get_actor_id('Cillian Murphy'))
    s.output_graph(p)
