'''© fergascod & asleix'''

from telegram.ext import *
import data
from data import BotException
import os
import random
import string
import logging
from datetime import datetime


def ErrorHandler(func):
    '''
    Decorator that handles the possible exceptions during a request.
    It distinguishes between user mistakes, using the class
    BotException, and internal mistakes.
    '''
    red, blue, end = '\033[91m', '\033[94m', '\033[0m' # Unix Terminal colors

    def Request(self, bot, update, **kwargs):
        user_ = str(update.message.from_user.id)
        user = blue +  update.message.chat.username + end
        print(user, 'is putting a request')
        print('    time:', datetime.now())

        try:
            func(self, bot, update, **kwargs)
            print(user, 'request is fulfilled')

        except KeyError as err:  # Case graph has not been created
            if str(err) != user_:
                print(red + 'EXCEPTION' + end)
                bot.send_message(chat_id=update.message.chat_id,
                                 text="I can't fulfill your desires!")
                bot.send_message(chat_id=update.message.chat_id, text=str(err))
                raise err

            self.start(bot, update)
            func(self, bot, update, **kwargs)
            print(user, 'request is fulfilled')

        except BotException as err:  # General handled case
            print(red + 'EXCEPTION' + end)
            print(user, 'request is not fulfilled\n', err)
            bot.send_message(chat_id=update.message.chat_id,
                             text="I can't fulfill your desires!")
            bot.send_message(chat_id=update.message.chat_id, text=str(err))

        except Exception as err:  # Unexpected error
            print(red + 'EXCEPTION' + end)
            print(user, 'request is not fulfilled')
            bot.send_message(chat_id=update.message.chat_id,
                             text="I can't fulfill your desires!")
            bot.send_message(chat_id=update.message.chat_id,
                             text="Some weird error happened:\n" + str(err))
            raise err

    return Request


class BicingBot(object):
    ''' Main driver class for the BicingBot. Contains all bot functions. '''
    def __init__(self):
        self.G = {}
        self.rand_gen = lambda: ''.join([random.choice(string.ascii_letters)
                                         for i in range(10)]) + '.png'

    @ErrorHandler
    def start(self, bot, update):
        ''' Starts a conversation with the bot.
            A welcome message is sent to the chat.'''
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Welcome! This bot will help you get information on " +
                 "Bicing stations in Barcelona, for more information " +
                 "on the bot, use the command /help")

        user = update.message.from_user.id
        username = update.message.chat.username
        self.G[user] = data.start_graph()
        self.G[user].name = username

    @ErrorHandler
    def get_help(self, bot, update):
        '''
        Show documentation.
        Display all possible commands and usage guide.
        '''
        user = update.message.from_user.id
        bot.send_message(chat_id=update.message.chat_id, text=HELP)

    @ErrorHandler
    def get_authors(self, bot, update):
        ''' Sends a message with the names and emails of the authors. '''
        user = update.message.from_user.id
        if user not in self.G.keys():
            self.start(bot, update)

        bot.send_message(
            chat_id=update.message.chat_id,
            text="Fernando Gastón Codony: fernando.gaston@est.fib.upc.edu")
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Aleix Seguí Ugalde: aleix.segui@est.fib.upc.edu")

    @ErrorHandler
    def get_graph(self, bot, update, args):
        '''
        Create a new geometric graph from the Bicing stations data.
        Given a set of vertices and a distance d, a geometric graph
        contains the edges between the vertices at a distance less than d.
        '''
        user = update.message.from_user.id
        try:
            if len(args) != 1:
                raise Exception
            distance = int(args[0])

        except Exception as err:
            raise BotException('Invalid argument. Not a distance!')

        self.G[user] = data.create_graph(self.G[user], distance)
        bot.send_message(chat_id=update.message.chat_id, text='OK')

    @ErrorHandler
    def get_nodes(self, bot, update):
        '''Sends a message with the number of nodes of the graph.'''
        user = update.message.from_user.id
        nodes = data.number_of_nodes(self.G[user])
        bot.send_message(chat_id=update.message.chat_id, text=nodes)

    @ErrorHandler
    def get_edges(self, bot, update):
        ''' Sends a message with the number of edges of the graph. '''
        user = update.message.from_user.id
        edges = data.number_of_edges(self.G[user])
        bot.send_message(chat_id=update.message.chat_id, text=edges)

    @ErrorHandler
    def get_components(self, bot, update):
        ''' Sends a message with the number of connected components. '''
        user = update.message.from_user.id
        CC = data.get_connected_components(self.G[user])
        bot.send_message(chat_id=update.message.chat_id, text=CC)

    @ErrorHandler
    def get_route(self, bot, update, args):
        '''
        Displays the map of the city with
        the route between two given addresses.
        '''
        user = update.message.from_user.id
        filename = self.rand_gen()
        data.create_route(self.G[user], args, filename)
        bot.send_photo(chat_id=update.message.chat_id,
                       photo=open(filename, 'rb'))
        os.remove(filename)

    @ErrorHandler
    def get_map(self, bot, update):
        '''
        Displays the map of the city with the all
        the Bicing stations (vertices of the graph)
        and the edges that connect them
        '''
        user = update.message.from_user.id
        filename = self.rand_gen()
        data.plot_graph(self.G[user], filename)
        bot.send_photo(chat_id=update.message.chat_id,
                       photo=open(filename, 'rb'))
        os.remove(filename)

    @ErrorHandler
    def get_summary(self, bot, update):
        '''
        Distribute the unbalanced bikes in the Bicing network.
        The total cost of transportation is displayed, as well
        as the edge with highest cost.
        '''
        user = update.message.from_user.id
        summary = data.graph_summary(self.G[user])
        bot.send_message(
            chat_id=update.message.chat_id,
            text=summary)


    @ErrorHandler
    def get_distribute(self, bot, update, args):
        '''
        Distribute the unbalanced bikes in the Bicing network.
        The total cost of transportation is displayed, as well
        as the edge with highest cost.
        '''
        user = update.message.from_user.id

        try:
            if len(args) != 2:
                raise Exception('2 arguments are needed!')
            requiredBikes, requiredDocks = int(args[0]), int(args[1])
            if requiredBikes < 0 or requiredDocks < 0:
                raise Exception('Values must be non-negative!')

        except Exception as err:
            raise BotException('Invalid input. ' + str(err))

        cost, move = data.distribute_bikes(self.G[user],
                                     requiredBikes, requiredDocks)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Total cost of transferring bicycles: " + str(cost) + " km.\n" +
                 "Highest cost edge:\n" + str(move[0]) + ' -> ' + str(move[1]) +
                 ', ' + str(move[2]) + ' bikes, distance ' + str(move[3]) + ' m.')

    @ErrorHandler
    def unknown(self, bot, update):
        ''' Unknown command handler. '''
        raise BotException('Unrecognized command. ' +
                           'Try /help for other commands.')

    @ErrorHandler
    def NoCommand(self, bot, update):
        ''' Text with no command handler. '''
        bot.send_message(
            chat_id=update.message.chat_id,
            text='I didn\'t catch that! Try /help for more info.')


def main():
    # Using the logger to display uncatched exceptions in stdout.
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    # Declaration of objects used to work with Telegram bots
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    PyBot = BicingBot()
    # When the bot receives the command (first parameter)
    # the function (second parameter) is executed
    dispatcher.add_handler(CommandHandler('start', PyBot.start))
    dispatcher.add_handler(CommandHandler('help', PyBot.get_help))
    dispatcher.add_handler(CommandHandler('authors', PyBot.get_authors))
    dispatcher.add_handler(CommandHandler('graph', PyBot.get_graph, pass_args=True))
    dispatcher.add_handler(CommandHandler('nodes', PyBot.get_nodes))
    dispatcher.add_handler(CommandHandler('edges', PyBot.get_edges))
    dispatcher.add_handler(CommandHandler('components', PyBot.get_components))
    dispatcher.add_handler(CommandHandler('plotgraph', PyBot.get_map))
    dispatcher.add_handler(CommandHandler('route', PyBot.get_route, pass_args=True))
    dispatcher.add_handler(CommandHandler('distribute', PyBot.get_distribute, pass_args=True))
    dispatcher.add_handler(CommandHandler('summary', PyBot.get_summary))

    dispatcher.add_handler(MessageHandler(Filters.command, PyBot.unknown))
    dispatcher.add_handler(MessageHandler(Filters.text, PyBot.NoCommand))

    print('Bot is ON')
    updater.start_polling()


# Declaration of some constants used throughout the code

# Bot's token
TOKEN = "Here you should copy your token"

# Help message displayed when /help command is executed
HELP = "@PyBicingBot supports the following commands:\n\n\
- /start: Start a conversation with the bot. Your graph is created.\n\
- /help: Display all commands and usage guide.\n\
- /authors: Who are we?\n\
- /graph (distance): Create a new geometric graph from the Bicing stations \
data using the Bicing stations as vertices and the parameter as the maximum\
distance between stations. It must be in range (0, 1000).\n\
- /nodes: Get the number of nodes of the graph \
(number of active Bicing stations).\n\
- /edges: Get a message with the number of edges.\n\
- /components: Get the number of connected components.\n\
- /plotgraph: Get a drawing of the graph over the map of Barcelona.\n\
- /route (address, address): Get a drawing of the route between two given addresses. \n\
- /summary: Get assorted info from the graph. \n\
- /distribute (int, int): Calculate the cost of transporting bikes \
in order to guarantee a minimum number of bikes (first parameter) and docks \
(second parameter) per station. \n\n\
For additional information on the bot check out the following link: \n\
https://github.com/jordi-petit/ap2-bicingbot-2019/blob/master/README.md"


if __name__ == '__main__':
    main()
