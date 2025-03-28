"""
Module Description
==================
A file with all manners of graph processing given an SQL database graph created by sql_processing.
These processings include finding the shortest path between two nodes, finding the shortest path
given various restrictions on the nodes, and processing a found path into a colour coded graph
for printing purposes.

Copyright and Usage Information
===============================
This file is solely provided for the use in grading and review of the named student's
work by the TAs and Professors of CSC111. All further distribution of this code whether
as is or modified is firmly prohibited.

This file is Copyright (c) Nabhan Rashid, Danny Tran, and Tai Poole
"""
import os
import sqlite3 as sql
from collections import deque
import networkx as nx

ID_TO_ACTOR = 'data_files/name.basics.tsv'
ID_TO_MOVIE = 'data_files/title.basics.tsv'
MOVIE_TO_ACTOR = 'data_files/title.principals.tsv'

# The number of nodes to add to each node in a path for context
RANDOM_NODE_COUNT = 3


class FileFormatError(Exception):
    """
    An error raised during file reading if the format of the file is incorrect
    """
    def __str__(self) -> str:
        """
        Return a string representation of this exception
        """
        return "The file attempted to be read is not in the correct format"


class ShortestActorGraph:
    """
    A class with the graph which will process the functions such as shortest_path or new_bacon
    """

    # Private Instance Attributes:
    #   - _db_path: The file path leading to the formatted

    _db_path: str

    def __init__(self, database_path: str) -> None:
        """
        Initializes the _actors and _movies attributes using the files

        Preconditions:
            - database_path refers to a valid sqlite3 database that has at least the tables "actor", "movie", and "edge"
                - It will throw an error if this is not true
        """
        if not os.path.exists(database_path):
            raise FileNotFoundError
        self._db_path = database_path

    def make_networkx_graph(self, path: list[str]) -> nx.Graph:
        """
        Given a path, creates a NetworkX graph using the nodes in the path. Also includes nodes branching from the path
        for visual comparison.

        These nodes have attributes for the colours of the nodes. Check now deprecated output_graph for how that is
        expected to work

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

        last_node_name = self.get_name(path[-1])
        nodes_to_add = RANDOM_NODE_COUNT
        adjacent_nodes = self.get_adjacent_nodes(path[-1])

        if len(path) <= 1:
            nx_graph.add_node(self.get_name(path[0]), color='green')
        else:
            nx_graph.nodes[self.get_name(path[0])]['color'] = 'green'

            adjacent_nodes.remove(path[-2])

        while nodes_to_add > 0 and len(adjacent_nodes) > 0:
            connected_node_id = adjacent_nodes.pop()
            connected_node_name = self.get_name(connected_node_id)
            if connected_node_id[0:2] == 'tt':
                nx_graph.add_node(connected_node_name, color='salmon')
            else:
                nx_graph.add_node(connected_node_name, color='bisque')
            nx_graph.add_edge(last_node_name, connected_node_name)
            nodes_to_add -= 1

        nx_graph.add_node(self.get_name(path[-1]), color='green')
        return nx_graph

    def get_name(self, object_id: str) -> str:
        """
        Given an id (Whether movie or actor) return a title or actor.

        Preconditions:
            - id is a valid actor or movie id
        """
        connection = sql.connect(self._db_path)
        cursor = connection.cursor()

        if object_id[0:2] == 'tt':
            name = cursor.execute("""SELECT title FROM movie WHERE id = ?""", (object_id,)).fetchone()[0]
        else:
            name = cursor.execute("""SELECT name FROM actor WHERE id = ?""", (object_id,)).fetchone()[0]
        cursor.close()
        connection.close()

        return name

    def get_actor_id(self, actor_name: str, played_in: str = '') -> str:
        """
        Given an actor's name, return their id.

        If there are multiple of the same actor, then can be given an optional parameter 'played_in' to specify a movie
        the actor has played in.

        Returns an empty string if the actor doesn't exist, or there are more than one actor that fit the description

        >>> a = ShortestActorGraph('data_files/actors_and_movies.db')
        >>> a.get_actor_id('Kevin Bacon')
        ''
        >>> a.get_actor_id('Kevin Bacon', 'Space Oddity')
        'nm0000102'
        >>> s = ShortestActorGraph('data_files/actors_and_movies.db')
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
                played_in = cursor.execute("""
                            SELECT id FROM movie WHERE title = ?
                    """, (played_in,)).fetchall()

                if len(played_in) == 0:
                    cursor.close()
                    return ''

                list_of_actors = cursor.execute("""
                    SELECT id FROM actor WHERE name = ?
                    """, (actor_name,)).fetchall()

                for actor in list_of_actors:
                    movies_played_in = cursor.execute("""
                        SELECT connections FROM edge WHERE object_id = ?
                        """, (actor[0],)).fetchone()

                    if movies_played_in is None:
                        continue

                    movies_played_in = movies_played_in[0].split(',')

                    if any(possible_played_in[0] in movies_played_in for possible_played_in in played_in):
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

        >>> a = ShortestActorGraph('small_data_files/small_db.db')
        >>> a.get_adjacent_nodes('nm0000138') == {'tt1375666', 'tt0120338'}
        True
        >>> a.get_adjacent_nodes('tt1375666') == {'nm0000138', 'nm0330687', 'nm0680983', 'nm0913822', 'nm0362766', 'nm2438307', 'nm0614165', 'nm0000297', 'nm0182839', 'nm0000592'}
        True
        """
        with sql.connect(self._db_path) as connection:
            cursor = connection.cursor()
            connected_nodes = cursor.execute("""
                                    SELECT connections FROM edge WHERE object_id = ?
                            """, (given_id,)).fetchone()

            cursor.close()

            if connected_nodes is None:
                return set()

            return set(connected_nodes[0].split(','))

    def get_valid_actors(self, is_alive: str = "") -> list[str]:
        """
        Returns a list of valid actors based on the restrictions given

        Preconditions:
            - is_alive.lower() in ["alive", "deceased", ""]
        """
        with sql.connect(self._db_path) as connection:
            cursor = connection.cursor()

            if is_alive == 'alive':
                return cursor.execute("""
                            SELECT name FROM actor WHERE deathYear = '\\N'
                    """).fetchall()
            elif is_alive == 'deceased':
                return cursor.execute("""
                            SELECT name FROM actor WHERE deathYear != '\\N'
                    """).fetchall()
            else:
                return cursor.execute("""
                            SELECT name FROM actor
                    """).fetchall()

    def get_path(self, actor1: str, actor2: str) -> list[str]:
        """
        Given two actor IDs, return the shortest path between two actors as a sequences of actors

        Returns an empty list if such a path does not exist

        Preconditions:
            - The actors are in the graph

        >>> s = ShortestActorGraph('small_data_files/small_db.db')
        >>> s.get_path('nm0000206', 'nm0000138') != []
        True
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

            for adjacent in self.get_adjacent_nodes(curr_node):
                if adjacent == actor2:
                    return curr_path + [adjacent]

                if adjacent not in visited:
                    visited.add(adjacent)
                    queue.append(curr_path + [adjacent])

        return []


    def check_alive_helper(self, check_is_alive_helper, alive_status_helper) -> bool:
        # If actor is dead and we want alive nodes:
        if alive_status_helper == "\\N":
            if check_is_alive_helper.lower() == "alive":
                return False
        # If actor is alive and we want dead nodes:
        else:
            if check_is_alive_helper.lower() == "deceased":
                return False
        return True

    def match_requirements(self, node_id: str, want_alive: str, want_before: int, want_after: int) -> bool:
        """
        Given a node ID, returns True if that node matches all the necessary requirements.

        If the node is a movie, then it was released before want_before and after want_after.
        If the node is an actor, then their alive or dead state matches the want_alive.

        Preconditions:
            - node_id is a valid node in the database of self._db_path

        >>> p = ShortestActorGraph('data_files/actors_and_movies.db')
        >>> dead_person = p.get_actor_id('William Courtenay')
        >>> p.match_requirements(dead_person, 'dead', 9999, 0)
        True
        >>> p.match_requirements(dead_person, 'alive', 9999, 0)
        False
        >>> old_movie = 'tt0000675'
        >>> p.match_requirements(old_movie, '', 1990, 0)
        True
        >>> p.match_requirements(old_movie, '', 9999, 1990)
        False
        """
        connection = sql.connect(self._db_path)
        cursor = connection.cursor()

        if node_id[0:2] == 'nm':
            death_state = cursor.execute("""SELECT deathYear FROM actor WHERE id = ?""", (node_id,)).fetchone()[0]

            satisfied_requirements = (death_state == "\\N") == (want_alive.lower() == "alive")
        else:
            release_year = cursor.execute("""SELECT startYear FROM movie WHERE id = ?""", (node_id,)).fetchone()[0]

            if not release_year.isnumeric():
                satisfied_requirements = True
            else:
                satisfied_requirements = want_after < int(release_year) < want_before
        # If actor is dead and we want alive nodes:

        cursor.close()
        connection.close()
        return satisfied_requirements

    def get_restricted_path(self, actor1: str, actor2: str, check_is_alive: str = "Any", released_before: int = 9999, released_after: int = 0) -> list[str]:
        """
        Given two actor IDs, return the shortest path between the two as a list of actors/movies with the following restrictions:

        If specified, only use nodes between alive actors exclusively or dead actors exclusively

        If specified, only use nodes of movies released before or during a specified year

        If specified, only use nodes of movies released after or during specified year

        Return an empty list if no such path exists.

        Preconditions:
            - is_alive.lower() in ["alive", "deceased", ""]
        """
        if actor1 == actor2:
            return [actor1]

        queue = deque()
        queue.append([actor1])
        visited = set()
        visited.add(actor1)

        # Initialize SQL connection:

        while queue:
            curr_path = queue.popleft()
            curr_node = curr_path[-1]

            for adjacent in self.get_adjacent_nodes(curr_node):
                # Return found path!
                if adjacent == actor2:
                    return curr_path + [adjacent]

                # Check Neighbours that are not
                if adjacent not in visited:
                    visited.add(adjacent)
                    if self.match_requirements(adjacent, check_is_alive, released_before, released_after):
                        queue.append(curr_path + [adjacent])

        return []

# if __name__ == '__main__':
#     import python_ta
#
#     python_ta.check_all(config={
#         'max-line-length': 120,
#         'disable': ['E1136'],
#         'extra-imports': ['csv', 'networkx', 'sqlite3', 'collections', 'matplotlib.pyplot'],
#         'allowed-io': ['load_review_graph'],
#         'max-nested-blocks': 4
#     })

    # s = ShortestActorGraph('small_data_files/small_db.db')
    # p = s.get_path(s.get_actor_id('Keanu Reeves'), s.get_actor_id('Cillian Murphy'))
    # s.output_graph(p)
