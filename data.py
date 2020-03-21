'''© fergascod & asleix'''

from staticmap import StaticMap, CircleMarker, Line
import networkx as nx
import pandas as pd
from haversine import haversine
from geopy.geocoders import Nominatim
from math import ceil, floor


class BotException(Exception):
    ''' Custom class to distinguish handled exceptions. '''
    pass


class Node:
    ''' Main class for the nodes in the geometric graph. '''
    def __init__(self, lat_, lon_, station_id=None):
        ''' Defines latitude and longitude for the node. '''
        self.lat = lat_
        self.lon = lon_
        self.id = station_id

    def coords(self):
        ''' Returns a tuple of the coordinates. Reversed order than init. '''
        return (self.lon, self.lat)

    def distance_to(self, next):
        ''' Calculates distance (km) in the sphere using haversine.
            Returns a float, the distance between self and next in km. '''
        c1 = (self.lat, self.lon)
        c2 = (next.lat, next.lon)
        return haversine(c1, c2)


def create_grid(G, P, d):
    '''
    Create a grid that divides the plane in cells of distance d + EPS.
    We use an error parameter EPS because the points are in a sphere. Returns a
    matrix where each cells contains the stations in that position of the grid.
    '''
    EPS = 0.01
    d_ = d + EPS
    # Find boundary points
    minlat, minlon, maxlat, maxlon = P[0].lat, P[0].lon, P[0].lat, P[0].lon
    for node in P:
        minlat = min(minlat, node.lat)
        minlon = min(minlon, node.lon)
        maxlat = max(maxlat, node.lat)
        maxlon = max(maxlon, node.lon)

    # Find vertices of the bounding box
    ll, lr = Node(minlat-EPS, minlon-EPS), Node(minlat-EPS, maxlon+EPS)
    ul, ur = Node(maxlat+EPS, minlon-EPS), Node(maxlat+EPS, maxlon+EPS)
    n, m = ceil(ll.distance_to(lr)/d_), ceil(ll.distance_to(ul)/d_)
    grid = [[[] for i in range(m)] for j in range(n)]

    # Insert points to the grid
    for node in P:
        aux_x, aux_y = Node(ll.lat, node.lon), Node(node.lat, ll.lon)
        x, y = floor(ll.distance_to(aux_x)/d_), floor(ll.distance_to(aux_y)/d_)
        grid[x][y].append(node)

    return grid


def geometric_graph(G, P, d):
    '''
    Function that creates the geometric graph.
    A grid is generated so all nodes in a cell can only be connected to nodes
    in its neighbouring cells.
    Linear with respect to edges when assuming the points are
    uniformly distributed over the plane.
    '''
    grid = create_grid(G, P, d)

    def create_edges(G, cur, next):
        ''' Create edges between cells 'cur' and 'next'. '''
        for n1 in cur:
            for n2 in next:
                dist = n1.distance_to(n2)
                if dist <= d and n1 is not n2:
                    G.add_edge(n1, n2, weight=dist/10)

    n, m = len(grid), len(grid[0])
    for i in range(n-1):
        for j in range(m-1):
            create_edges(G, grid[i][j], grid[i][j])
            create_edges(G, grid[i][j], grid[i+1][j])
            create_edges(G, grid[i][j], grid[i][j+1])
            create_edges(G, grid[i][j], grid[i+1][j+1])
            if j >= 1:
                create_edges(G, grid[i][j], grid[i+1][j-1])


def start_graph():
    '''
    Retrieve data from the web.
    Returns a geometric graph with distance 1000m.
    '''
    try:
        url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
        print('Retrieving data...')

        bicing = pd.DataFrame.from_records(
            pd.read_json(url)['data']['stations'], index='station_id')

        G = nx.Graph()
        for station in bicing.itertuples():
            n = Node(station.lat, station.lon, station.Index)
            G.add_node(n)

    except Exception as err:
        raise BotException('Could not retrieve Bicing data. ' +
                           'Data might be inaccessible.')

    return create_graph(G, 1000)


def create_graph(G_, distance):
    '''
    Returns a geometric graph given a distance d,
    using Bicing stations in Barcelona as vertices.
    '''
    if distance < 0 or distance > 1000:
        raise BotException('Invalid distance. Input must be in range ' +
                           '0 - 1000 (meters).')

    distance /= 1000

    G = nx.create_empty_copy(G_, with_data=True)
    geometric_graph(G, list(G.nodes()), distance)

    return G


def number_of_nodes(G):
    ''' Returns the number of nodes of the graph '''
    return G.number_of_nodes()


def number_of_edges(G):
    ''' Returns the number of edges of the graph '''
    return G.number_of_edges()

def graph_summary(G):
    ''' Returns a summary of the graph '''
    return nx.info(G)

def addressesTOcoordinates(addresses):
    '''
    Returns the two coordinates of two addresses of Barcelona
    Given their addresses in a single string separated by a comma.
    In case of failure, returns None.
    '''
    try:
        geolocator = Nominatim(user_agent="PyBicing_bot")
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return ((location1.latitude, location1.longitude),
                (location2.latitude, location2.longitude))

    except ValueError:
        raise BotException('A comma between addresses is required!')

    except AttributeError:
        msg = ['Address/es could not be found.']
        if location1 is None: msg.append('\n  -> ' + address1)
        if location2 is None: msg.append('\n  -> ' + address2)
        raise BotException(''.join(msg))


def plot_route(path, filename):
    ''' Creates a file with the map of Barcelona
        showing the route indicated in path.'''
    mapa = StaticMap(800, 800)
    last = path[0]
    for node in path:
        if node.coords() != last.coords():
            mapa.add_marker(CircleMarker(last.coords(), 'blue', 6))
            coord = [list(node.coords()), list(last.coords())]
            if(node == path[1] or node == path[-1]):
                line = Line(coord, 'red', 3)
            else:
                line = Line(coord, 'blue', 3)
            mapa.add_line(line)
            last = node
    mapa.add_marker(CircleMarker(path[0].coords(), 'red', 8))
    mapa.add_marker(CircleMarker(path[-1].coords(), 'red', 8))
    imatge = mapa.render()
    imatge.save(filename)


def create_route(G_, args, filename):
    '''
    Creates a file (map.png) with the map of Barcelona showing all Bicing
    stations and edges of the shortest route that connect two given adresses.
    '''
    # Getting coordinates from input string
    G = G_.copy()
    if len(args) == 0:
        raise BotException('No addresses were given.')
    adresses = ''.join([s + ' ' for s in args])
    cood1, cood2 = addressesTOcoordinates(adresses)

    add1, add2 = Node(cood1[0], cood1[1]), Node(cood2[0], cood2[1])
    G.add_node(add1)
    G.add_node(add2)
    for node in G.nodes():
        if node is not add1:
            G.add_edge(add1, node, weight=node.distance_to(add1)/4)
        if node is not add2:
            G.add_edge(add2, node, weight=node.distance_to(add2)/4)
    path = nx.dijkstra_path(G, add1, add2)
    plot_route(path, filename)


def get_connected_components(G):
    '''
    Returns the number of connected components of the Graph. If the number
    is 1, every node is accessible from any starting point.
    '''
    return len(list(nx.connected_components(G)))


def plot_graph(G, filename):
    '''
    Creates a file (filename) with the map of Barcelona showing all
    Bicing stations and the edges of the graph that connect them.
    '''
    mapa = StaticMap(800, 800)
    for node in list(G.nodes):
        mapa.add_marker(CircleMarker(node.coords(), 'red', 5))
    for node1, node2 in list(G.edges):
        coord = [list(node1.coords()), list(node2.coords())]
        line = Line(coord, 'blue', 1)
        mapa.add_line(line)
    imatge = mapa.render()
    imatge.save(filename)


def create_flow_network(G_, stations, bikes, requiredBikes, requiredDocks):
    ''' Create flow graph according to our model. The geometric graph is copied.
        Returns a directed flow network Graph. '''
    G = nx.DiGraph()
    G.add_node('TOP')  # The green node
    demand = 0

    for st in bikes.itertuples():
        idx = st.Index
        if idx not in stations.index: continue
        stridx = str(idx)

        b_idx, k_idx, r_idx = 'b'+stridx, 'k'+stridx, 'r'+stridx
        G.add_nodes_from([b_idx, k_idx, r_idx])

        b, d = st.num_bikes_available, st.num_docks_available
        req_bikes = max(0, requiredBikes - b)
        req_docks = max(0, requiredDocks - d)

        # Connect nodes and set boundary capacities
        G.add_edge('TOP', b_idx)
        G.add_edge(r_idx, 'TOP')
        G.add_edge(b_idx, k_idx, capacity=max(0, b-requiredBikes))
        G.add_edge(k_idx, r_idx, capacity=max(0, d-requiredDocks))

        # Set demand to source and sink nodes
        if req_bikes > 0:
            demand += req_bikes
            G.nodes[r_idx]['demand'] = +req_bikes
        elif req_docks > 0:
            demand -= req_docks
            G.nodes[b_idx]['demand'] = -req_docks

    G.nodes['TOP']['demand'] = -demand    # Compensate demand from nodes

    # Copy edges from geometric graph
    for u, v in G_.edges:
        idx1, idx2 = u.id, v.id
        dist = int(G_[u][v]['weight'] * 1e4)
        # The edges must be bidirectional: k_idx1 <--> k_idx2
        G.add_edge('k'+str(idx1), 'k'+str(idx2), weight=dist)
        G.add_edge('k'+str(idx2), 'k'+str(idx1), weight=dist)

    return G

def update_stations(G, flowDict, bikes, requiredBikes, requiredDocks):
    ''' Update stations according to the transportation of bicycles.
        Returns a list with all the moves, with bike num. and distance. '''
    nbikes = 'num_bikes_available'
    ndocks = 'num_docks_available'
    moves = []
    for src in flowDict:
        if src[0] != 'k': continue
        idx_src = int(src[1:])
        for dst, b in flowDict[src].items():
            if dst[0] == 'k' and b > 0:
                idx_dst = int(dst[1:])
                print(idx_src, "->", idx_dst, " ", b, "bikes, distance",
                      G.edges[src, dst]['weight'])
                moves.append((idx_src, idx_dst, b, G.edges[src, dst]['weight']))
                bikes.at[idx_src, nbikes] -= b
                bikes.at[idx_dst, nbikes] += b
                bikes.at[idx_src, ndocks] += b
                bikes.at[idx_dst, ndocks] -= b

    return moves


def distribute_bikes(G_, requiredBikes, requiredDocks):
    '''
    Use a flow network approach to compute the redistribution of bikes.
    returns: Minimum distribution cost.
             List of moves: (source, destination, num_of_bikes)
    '''

    # retrieve bike data
    url_info = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
    stations = pd.DataFrame.from_records(
        pd.read_json(url_info)['data']['stations'], index='station_id')
    bikes = pd.DataFrame.from_records(
        pd.read_json(url_status)['data']['stations'], index='station_id')

    nbikes = 'num_bikes_available'
    ndocks = 'num_docks_available'
    bikes = bikes[[nbikes, ndocks]]  # We only select the interesting columns

    try:
        G = create_flow_network(G_, stations, bikes, requiredBikes, requiredDocks)
        print('Graph with', G.number_of_nodes(),
              "nodes and", G.number_of_edges(), "edges.")
    except Exception as err:
        raise BotException('Could not create graph: \n' + str(err))

    try:
        flowCost, flowDict = nx.network_simplex(G)

    except nx.NetworkXUnfeasible:
        raise BotException('No solution was found.')

    except Exception as err:
        raise Exception('Internal error. Error with the model.\n' + str(err))

    print("The total cost of transferring bikes is", flowCost/1000, "km.")

    moves = update_stations(G, flowDict, bikes, requiredBikes, requiredDocks)
    if len(moves) == 0:
        raise BotException('No transportation of bikes is needed.')

    cost = lambda x: x[2]*x[3]  # Cost function

    return flowCost/1000, max(moves, key=cost)
