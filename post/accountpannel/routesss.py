import psycopg2
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from django.conf import settings
#create graph that passes to dijkstra



def create_graph_from_db(db_config, target, threshold=0.95):
    """
    Create a graph from the database by fetching NSH routes and applying a threshold.
    :param db_config: Dictionary with database credentials.
    :param threshold: Traffic-to-capacity ratio threshold for including edges.
    :return: Graph as an adjacency list.
    """
    graph = {}
    
    try:

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=db_config["NAME"],
            user=db_config["USER"],
            password=db_config["PASSWORD"],
            host=db_config["HOST"],
            port=db_config["PORT"]
        )
        cursor = conn.cursor()

        # Query the NSH routes
        cursor.execute("""
            SELECT nsh1_id, nsh2_id, time, traffic, capacity
            FROM accountpannel_adjacent_nsh_data;
        """)
        rows = cursor.fetchall()

        for source, adjacent, time, traffic, capacity in rows:
            if capacity == 0:
                continue  # Skip edges with zero capacity to avoid division by zero

            traffic_to_capacity_ratio = traffic / capacity

            # Include edge only if it satisfies the threshold condition
            if traffic_to_capacity_ratio <= threshold or adjacent == target:
                effective_weight = time  # Adjust weight calculation as needed
                if source not in graph:
                    graph[source] = []
                graph[source].append((adjacent, effective_weight))

        # Close the connection
        conn.close()
    except psycopg2.Error as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

    return graph


#dijkstra algorithm

def dijkstra(graph, source, target):
    
    try:
        pq = [(0, source, [])]  # Priority queue: (distance, current_node, path)
        visited = set()
        
        while pq:
            current_distance, current_node, path = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            # Update the path
            path = path + [current_node]
            

            pathDic = {}
            # If we reached the target, return the result
            

            if current_node == target:
                i = 1
                for p in path:
                    pathDic[f"nsh{i}"] = p
                    i+=1
                return current_distance, path, pathDic
            if len(path) == 0 :
                    return float('inf'), [], {"error": "Empty path encountered"}  
            
            # Explore neighbors
            for neighbor, weight in graph.get(current_node, []):
                if neighbor not in visited:
                    heapq.heappush(pq, (current_distance + weight, neighbor, path))
        
        return float('inf'), []  # No path found
    
    except KeyError as e:
        return float('inf'), [], {"error": f"Node not found in graph: {str(e)}"}
    except ValueError as e:
        return float('inf'), [], {"error": f"Invalid data encountered: {str(e)}"}
    except Exception as e:
        return float('inf'), [], {"error": f"Unexpected error: {str(e)}"}
    

