# Bicing Bot

This project features the implementation of a telegram bot (@PyBicingbot) that can be used to  get information on the current state of all Bicing stations in Barcelona. Bicing is a bike-based transportation service in Barcelona with more than 300 stations and 900 bikes spread around the city, which you can use to get around by paying a small fee. This bot will allow you to create routes between Bicing stations and get information on the current state of all stations in Barcelona using graph theory and the data provided by Bicing.

More info on the project: https://github.com/jordi-petit/ap2-bicingbot-2019/blob/master/README.md

(Note: For optimal viewing of this file use Typora.)

[TOC]

## Starting a conversation with the bot

In order to run the bot, you have to create a Telegram account, you can use the following link in order to create an account:    https://web.telegram.org/#/login

You can also download the app and the registration process will start as soon as you open it. If you already have an account, skip this step.

Once your account has been created, you can directly search for our bot's ID (@PyBicingbot) in the Telegram search bar. Once the chat  between you and the bot has been established, use the /start command to start the conversation.



## Prerequisites

If you want to run bot.py from terminal, you should install certain libraries. To do so just, run the following command in your terminal and all necessary libraries will be downloaded:

> ```
> pip install -r requirements.txt
> ```

In order for the bot.py file to run in the FIB server we had to add an extra requirement  (python-telegram-bot==10)  in the requirements.txt so an older version of the telegram module would be used (newer versions were not compatible with the server).



## Libraries

This projects benefits from the use of some libraries in order to handle graphs, maps, coordinates, data and the bot itself. The main ones are the following:

- **telegram**: this library is the one used to implement the bot.

  ​						https://github.com/python-telegram-bot/python-telegram-bot

- **staticmap**: the maps displayed by the bot were created using this library which allows you to create static maps.

  ​						https://github.com/komoot/staticmap

- **haversine: **this library was used to calculate distances between two points, given their longitude and latitude.

  ​						https://pypi.org/project/haversine/

- **pandas**: was used to collect the Bicing stations data which  was given in JSON format.

  ​						https://pandas.pydata.org/

- **geopy**: was used to translate addresses in Barcelona to their coordinates.

  ​						https://geopy.readthedocs.io/en/stable/



## Commands

@PyBicingBot supports the following commands:

- **/start**: Starts a conversation with the bot. A welcome message is sent to the chat. A graph with distance d and the Bicing stations is created for your user. It is supposed to be the first command to be executed, so if you execute another command first, the bot will automatically execute it before the given command.
- **/help**:  Shows documentation. Displays all possible commands and usage guide (this section of the README).
- **/authors**: Sends a message to the chat with the names and emails of the authors.
- **/graph** (distance) : Creates a new geometric graph [[ 1 ]]( ) from the Bicing stations data using the Bicing stations as vertices and the parameter as the distance for the constructor. The parameter must be in range (0, 1000).
- **/nodes**: Sends a message to the chat with the number of nodes of the graph (number of Bicing stations).
- **/edges**: Sends a message to the chat with the number of edges of the graph.
- **/components**: Sends a message to the chat with the number of connected components of the graph.
- **/plotgraph**: Sends a drawing of the graph over a map of Barcelona.
- **/route** (origin, destination): Sends a drawing of the route between two given addresses over a map of Barcelona.
- **/distribute** (int, int): This command calculates the cost of transporting bikes in order to guarantee a minimum number of bikes (first parameter) and docks (second parameter) per station.



## Implementation details

- The graph for each user is stored in a map that relates a graph to the user ID of each person that has used the bot.
- When an instruction is received, the program will send details of the execution to the stdout, alongside with the possible errors that may have taken place during the execution.
- The first command to be executed when starting a conversation with the bot for the first time should be /start, because that's when the graph attached to your user name will be created. However, if another command is executed before, /start will be executed before your petition so no error will be visible.
- A decorator  (ErrorHandler)   is used to handle all possible errors, including both user input errors and internal errors, such as unavailable data.

Implementation details for some commands:

- /graph: When a graph is created all edges are assigned a weight which is the time that it takes to get from one vertex to the other. The distance is calculated with the haversine function and the speed is considered to be 10 km/h for a bike. 
  - Description of the algorithm. We create a grid with cells, each covering an area of d x d, where d is the maximum neighbor distance. Thus, we only have to check the cells around a given cell to create the edges. Notice that we are assuming we are in a plane. Hence, we have to use a distance d' = d + epsilon to avoid issues with the model.  
- /route: When adding both the origin and the destination to the graph, we will connect them to all other nodes in the graph (including each other). In this case, the weight will also be the time that it takes to get from one vertex to the other, but we'll consider the speed to be 4 km/h (walking speed). This way we don't have any problems in case the generated graph is not connected, we'll be able to walk to the destination from a bicing station.
- /distribute: We create a flow network from the geometric graph and run a simplex to find a solution to transfer the bikes with the minimum cost. An excerpt from the bike-flow statement explaining the model used is copied: 

  - Every station is represented by three nodes (blue, black, red).
  - The geometric graph, with bidirectional edges, is represented with the black nodes and edges.
  - The blue->black edges represent the `donation` of bikes to the network.
  - The black->red edges represent the `reception` of bikes from the network.
  - Some stations may have a deficit of bikes (double circle in red nodes). These stations must have a positive demand of bicycles.
  - Some stations may have a deficit of free docks (double circle in blue nodes). These stations must have a negative demand of bicycles.
  - For those nodes that meet the constraints (no deficit of bikes or docks), the flow must be zero. All bikes donated by the node (blue->black edge) are compensated by the free docks received by the same node (green->blue edges). Similarly, all bikes received by the node (black->red edges) are compensated by the docks donated by the node (red->green edges). Notice the duality between bikes and slots: the absence of a bicycle implies a free docks, in such a way that `bikes + free docks` is an invariant at each station.
  - The __TOP__ node is used to compensate the demand of bikes/docks (the sum of demands must be zero). Notice that the __TOP__ node has been duplicated to simplify the drawing of the graph: the two green nodes are the same.



## Test case examples

We show some inputs and the expected output. Commands that send pictures can't be shown here.

```
> /start
Welcome! This bot will help you get information on Bicing stations in Barcelona, for more information, use the command /help.

> /distribute 4 3
Total cost of transferring bicycles: 304.749 km.
Highest cost edge:
121 -> 278, 10 bikes, distance 702 m.

> /route
I can't fulfill your desires!
No addresses were given.

> /distance 900
OK

> /distance 1500
I can't fulfill your desires!
Invalid distance. Input must be in range 0 - 1000 (meters).
```



## Authors

Fernando Gastón Codony: fernando.gaston@est.fib.upc.edu.

Aleix Seguí Ugalde: aleix.segui@est.fib.upc.edu.

