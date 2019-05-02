# importa l'API de Telegram
import telegram

from telegram.ext import *

from staticmap import *

import datetime

import 'data.py' as data
'''
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Preparat per fer cosetes ☺")
    bot.send_message(chat_id=update.message.chat_id, text="Fes servir la comanda /help per obtenir més informació sobre mi.")


def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text=HELP)

def hora(bot, update):
	HORA = str(datetime.datetime.now()) #Returns date and time
	bot.send_message(chat_id=update.message.chat_id, text="Avui som a "+HORA)

def creation_time(bot, update):
	message = "This bot was created on 4/11/2019 at 10:30 in the morning"
	bot.send_message(chat_id=update.message.chat_id, text=message)

def myface(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Ara veuràs la meva cara")
	bot.send_photo(chat_id=update.message.chat_id, photo=open('myface.jpg', 'rb'))
	bot.send_message(chat_id=update.message.chat_id, text="Disgusting, ja ho sé")

def info(bot, update):
	botname = bot.username
	username = update.message.chat.username
	fullname = update.message.chat.first_name
	if username!="Fergascod":
		missatge = "Tu ets en %s (%s) i jo soc el %s." % (fullname, username, botname)
	else:
		missatge = "Tu ets el meu creador!"
		bot.send_message(chat_id=update.message.chat_id, text=missatge)

def where (bot, update, user_data):
	try:
		bot.send_message(chat_id=update.message.chat_id, text="Aquesta és la teva posició")
		fitxer = "location.png"
		lat, lon = update.message.location.latitude, update.message.location.longitude
		print (lon , lat)
		coord=[[2.112577, 41.387725], [lon , lat]]
		line = Line(coord, 'white', 5)
		mapa = StaticMap(1100, 1100)
		mapa.add_line(line)

		mapa.add_marker(CircleMarker((lon, lat), 'blue', 10))
		mapa.add_marker(CircleMarker((2.112577, 41.387725), 'red', 10))

		imatge = mapa.render()
		imatge.save(fitxer)
		bot.send_photo(chat_id=update.message.chat_id, photo=open('location.png', 'rb'))
	except Exception as e:
		print(e)

def kk (bot, update):
	try:
		lon = randint(-180, 180)
		lat = randint(-90, 90)
		bot.send_message(chat_id=update.message.chat_id, text="Random position")
		fitxer = "location.png"
		mapa = StaticMap(1100, 1100)

		mapa.add_marker(CircleMarker((lon,lat), 'blue', 10))

		imatge = mapa.render(zoom=10)
		imatge.save(fitxer)

		bot.send_photo(chat_id=update.message.chat_id, photo=open('location.png', 'rb'))
		mapa2 = StaticMap(1100, 1100)

		mapa2.add_marker(CircleMarker((lon,lat), 'blue', 10))
		mapa2.add_marker(CircleMarker((2.112577, 41.387725), 'blue', 10))

		imatge2 = mapa2.render()
		imatge2.save(fitxer)

		bot.send_photo(chat_id=update.message.chat_id, photo=open('location.png', 'rb'))
	except Exception as e:
		print(e)

'''


def start(bot, update):
    '''
    Starts a conversation with the bot.
    '''
    data.create_graph(1000)
    bot.send_message(chat_id=update.message.chat_id, text="Benvingut...")
    # print welcome message

def get_help(bot, update):
    '''
    Show documentation.
    Display all possible commands
    and usage guide.
    '''
    bot.send_message(chat_id=update.message.chat_id, text=HELP)

def get_authors(bot, update):
    '''
    Sends a message to the chat with the names and emails of the authors
    '''
    bot.send_message(chat_id=update.message.chat_id, text="Fernando Gastón Codony: fernando.gaston@est.fib.upc.edu")

def get_graph(bot, update, distance):
    '''
    Create a new geometric graph from the Bicing stations data.
    Given a set of vertices and a distance d, a geometric graph
    contains the edges between the vertices at a distance less than d.
    '''
    distance = input #ditancia erronia (ex: negativa)
    data.create_graph(distance)
    bot.send_message(chat_id=update.message.chat_id, text="OK")


def get_nodes(bot, update):
    '''
    Sends a message to the chat with the number of nodes of the graph.
    '''
    nodes = data.number_of_nodes()
    bot.send_message(chat_id=update.message.chat_id, text=nodes)

def get_edges(bot, update):
    '''
    Sends a message to the chat with the number of edges of the graph.
    '''
    edges = data.number_of_edges()
    bot.send_message(chat_id=update.message.chat_id, text=edges)

def get_components(bot, update):
    '''
    Sends a message to the chat with the number of connected components.
    '''
    CC = data.get_connected_components()
    bot.send_message(chat_id=update.message.chat_id, text=CC)

def get_route(bot, update, input):
    '''
    Displays the map of the city with the route
    between two given addresses.
    '''
    origin = input
    destination = input
    data.create_route(origin, destination)
    bot.send_photo(chat_id=update.message.chat_id, photo=open('map.png', 'rb'))
    delete map.png

def get_map(bot, update):
    '''
    Displays the map of the city with the all
    the Bicing stations (vertices of the graph)
    and the edges that connect them
    '''
    data.plot_graph()
    bot.send_photo(chat_id=update.message.chat_id, photo=open('map.png', 'rb'))
    delete map.png


# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()
#Llegeix el fitxer help.txt
HELP = open('help.txt').read().strip()
# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda '/comanda' s'executi la funció comanda (1r i 2n paràmtre)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', get_help))
dispatcher.add_handler(CommandHandler('authors', get_authors))
dispatcher.add_handler(CommandHandler('graph', get_graph, pass_args=True)) #parameters
dispatcher.add_handler(CommandHandler('nodes', get_nodes))
dispatcher.add_handler(CommandHandler('edges', get_edges))
dispatcher.add_handler(CommandHandler('components', get_components))
dispatcher.add_handler(CommandHandler('plotgraph', get_map))
dispatcher.add_handler(CommandHandler('route', get_route, pass_args=True))


# engega el bot
updater.start_polling()
