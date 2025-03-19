"""
The file where functions for processing the data will be.

# TODO - add copyright
"""
import networkx as nx

ID_TO_ACTOR = 'data_files/name.basics.tsv'
ID_TO_MOVIE = 'data_files/title.basics.tsv'
MOVIE_TO_ACTOR = 'data_files/title.basics.tsv'


class ActorGraph:
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
        # TODO

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

    def output_graph(self) -> None:
        """
        Creates a new window with an induced subgraph depending on the given actors and edges.

        TODO - Decide what this should take in and what Preconditions those things should have
        """
        # TODO
