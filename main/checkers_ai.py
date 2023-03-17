from checkers.game import Game # https://pypi.org/project/imparaai-checkers/
from controller import readController
import json
from queue import Queue
from webInterface import startWebInterface
import threading
import requests
import time
import board
import neopixel 

pixels = neopixel.NeoPixel(board.D18, 128)
URL = "http://flyyrin.pythonanywhere.com/game"

with open(r'/home/rpi/Documents/GIP-2022-2023/main/json/config.json') as configFile:
    config = json.load(configFile)

with open(r'/home/rpi/Documents/GIP-2022-2023/main/json/layout.json') as layoutFile:
    layout = json.load(layoutFile)

show_moves = True

playerData = {
    "player1": {
        "name": "",
        "color": ""
    },
    "player2": {
        "name": "",
        "color": ""
    }
}

gameData = {
    "current-player": 0,
    "pieces": {
        "player1": {
            "pieces": 12,
            "kings": 0,
            "captured": 0
        },
        "player2": {
            "pieces": 12,
            "kings": 0,
            "captured": 0
        }
    }
}

def postNoWait(URL, params, json):
    requests.post(url = URL, params = params, json = json)

board = {}
old_board = {}
def color(tile, color):
    global board
    board[tile] = color

def refresh():
    global board
    global old_board
    for tile, color in board.items():
        if color == 1:
            tile_color = eval(config["colors"][playerData["player1"]["color"]])
        elif color == 2:
            tile_color = eval(config["colors"][playerData["player2"]["color"]])
        elif color == 3:
            tile_color = eval(config["colors"]["king-"+playerData["player1"]["color"]])
        elif color == 4:
            tile_color = eval(config["colors"]["king-"+playerData["player2"]["color"]])
        else:
            tile_color = eval(config["colors"][str(color)])
        try:
            if old_board[tile] != color:
                led1 = tile*2
                led2 = tile*2+1
                pixels[led1] = tile_color
                pixels[led2] = tile_color
        except:
            led1 = tile*2
            led2 = tile*2+1
            pixels[led1] = tile_color
            pixels[led2] = tile_color
    old_board = dict(board)

def startGame(queue):
    global layout
    game = Game()
    moves = []   
    selected = 0
    highlighted = {"x": 0, "y": 0}
    selected_tile = False
    playing = True
    startup = True
    while playing:
        winner = game.get_winner()
        if winner:
            requests.post(url = URL, params = {"type": "winner"}, json = {"winner": winner})
            winData = dict(playerData)
            winData["winner"] = winner  
            winData["date"] = int(time.time() * 1000)
            requests.post(url = URL+"s" , json = winData)
            playing = False
            for i in range(64):
                color(i, winner)
            refresh()
            exit()
        player = game.whose_turn()
        controller = readController(player)

        if startup:
            gameData["current-player"] = game.whose_turn()
            requests.post(url = URL, params = {"type": "gameData"}, json = {"gameData": gameData})
            controller = "-"
            startup = False
        try:
            data = queue.get_nowait()
            if data == "stop":
                for i in range(32):
                    color(i, "red")
                for i in range(32,64):
                    color(i, "purple")
                refresh()
                playing = False
                exit()
            if data == "exit":
                print("puss")
                for i in range(64):
                    color(i, "e")
                refresh()
                playing = False
                exit()
        except:
            pass

        pieces = []
        player1pieces = []
        player2pieces = []
        for piece in game.board.pieces:
            if piece.position != None:
                pieces.append(piece.position)
                if piece.player == 1:
                    player1pieces.append(piece.position)
                if piece.player == 2:
                    player2pieces.append(piece.position)

        empty = [x for x in [*range(1,33)] if x not in set(pieces)]    
        for position in empty:
            color(layout['game'][str(position)], "e")

        if controller == "up":
            if highlighted["y"] < 7:
                highlighted["y"] += 1

        if controller == "down":
            if 0 < highlighted["y"]:
                highlighted["y"] -= 1

        if controller == "left":
            if 0 < highlighted["x"]:
                highlighted["x"] -= 1

        if controller == "right":
            if highlighted["x"] < 7:
                highlighted["x"] += 1

        highlighted_tile = layout["board"][f"({highlighted['x']},{highlighted['y']})"]

        if controller == "press":
            if highlighted_tile in layout["game"].values():
                allowed = False
                new_selected = int([k for k, v in layout["game"].items() if v == highlighted_tile][0])
                if player == 1 and new_selected in player1pieces:
                    allowed = True
                if player == 2 and new_selected in player2pieces:
                    allowed = True
                if selected:
                    move = [selected, new_selected]
                    if move in game.get_possible_moves():
                        selected = 0
                        selected_tile = False
                        moves.clear()
                        game.move(move)
                if allowed:
                    if selected == new_selected:
                        selected = 0
                        selected_tile = False
                        moves.clear()
                    else:
                        moves.clear()
                        selected = new_selected
                        selected_tile = highlighted_tile
                        if show_moves:
                            for move in game.get_possible_moves():
                                if selected == move[0]:
                                    moves.append(move)

            player1piecesAmount = 0
            player2piecesAmount = 0
            player1kingsAmount = 0
            player2kingsAmount = 0
            for piece in game.board.pieces:
                if piece.position != None:
                    if piece.player == 1:
                        if piece.king:
                            player1kingsAmount += 1
                        else:
                            player1piecesAmount += 1
                    if piece.player == 2:
                        if piece.king:
                            player2kingsAmount += 1
                        else:
                            player2piecesAmount += 1
        
            gameData["pieces"]["player1"]["pieces"] = player1piecesAmount
            gameData["pieces"]["player2"]["pieces"] = player2piecesAmount
            gameData["pieces"]["player1"]["kings"] = player1kingsAmount
            gameData["pieces"]["player2"]["kings"] = player2kingsAmount
            gameData["pieces"]["player1"]["captured"] = 12 - (player2piecesAmount + player2kingsAmount)
            gameData["pieces"]["player2"]["captured"] = 12 - (player1piecesAmount + player1kingsAmount)
            gameData["current-player"] = game.whose_turn()
            threading.Thread(target=postNoWait, args=(URL, {"type": "gameData"}, {"gameData": gameData})).start()

        if controller:
            for i in range(64):
                color(i, "e")
            for piece in game.board.pieces:
                if piece.position != None:
                    player_piece = piece.player
                    if piece.king:
                        player_piece += 2
                    color(layout['game'][str(piece.position)], player_piece)
            
            for move in moves:
                color(layout['game'][str(move[1])], "p")
            if selected_tile:
                color(selected_tile, "c")
            color(highlighted_tile, "h")
            refresh()

def setupGame(queue):
    for i in range(32):
        color(i, "red")
    for i in range(32,64):
        color(i, "purple")
    refresh()
    while True:
        try:
            data = queue.get()
            if "start" in data:
                global playerData
                global show_moves
                np1,np2,cp1,cp2,assist = data.split("|")[1].split("&")
                playerData["player1"]["name"] = np1
                playerData["player2"]["name"] = np2
                playerData["player1"]["color"] = cp1
                playerData["player2"]["color"] = cp2
                print("assist:", assist, type(assist))
                if assist == "true":
                    show_moves = True
                if assist == "false":
                    show_moves = False
                startGame(queue)

            if "color" in data:
                cp1,cp2 = data.split("|")[1].split("&")
                color1 = eval(config["colors"][str(cp1)])
                color2 = eval(config["colors"][str(cp2)])
                for i in range(32):
                    color(i, cp1)
                for i in range(32,64):
                    color(i, cp2)
                refresh()
            if data == "exit":
                for i in range(64):
                    color(i, "e")
                refresh()
                exit()
        except:
            pass

queue = Queue()
gameThread = threading.Thread(target=setupGame, args=(queue,))
gameThread.start()
startWebInterface(queue)