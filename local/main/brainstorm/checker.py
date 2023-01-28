from checkers.game import Game
from controller import readController
import json
# https://pypi.org/project/imparaai-checkers/

with open(r'local\main\brainstorm\layout.json') as layoutFile:
    layout = json.load(layoutFile)

board = {}
old_board = {}
def color(tile, color):
    global board
    board[tile] = color

def refresh():
    global board
    global old_board
    for tile, color in board.items():
        try:
            if old_board[tile] != color:
                led1 = tile*2
                led2 = tile*2+1
                print(f"{tile}: {color}")

        except:
            led1 = tile*2
            led2 = tile*2+1
            print(f"{tile}: {color}")
    
    old_board = dict(board)

    b = board
    print(f"""     
        {b[56]} {b[57]} {b[58]} {b[59]} {b[60]} {b[61]} {b[62]} {b[63]} 
        {b[55]} {b[54]} {b[53]} {b[52]} {b[51]} {b[50]} {b[49]} {b[48]} 
        {b[40]} {b[41]} {b[42]} {b[43]} {b[44]} {b[45]} {b[46]} {b[47]} 
        {b[39]} {b[38]} {b[37]} {b[36]} {b[35]} {b[34]} {b[33]} {b[32]} 
        {b[24]} {b[25]} {b[26]} {b[27]} {b[28]} {b[29]} {b[30]} {b[31]} 
        {b[23]} {b[22]} {b[21]} {b[20]} {b[19]} {b[18]} {b[17]} {b[16]} 
        {b[8]} {b[9]} {b[10]} {b[11]} {b[12]} {b[13]} {b[14]} {b[15]} 
        {b[7]} {b[6]} {b[5]} {b[4]} {b[3]} {b[2]} {b[1]} {b[0]}    
    """)

def startGame():
    game = Game()
    player = game.whose_turn()
    global layout
    
    selected = 0
    highlighted = {"x": 0, "y": 0}
    selected_tile = False
    while not game.is_over():
        controller = readController(player)

        for i in range(64):
            color(i, "e")
        pieces = []
        player1pieces = []
        player2pieces = []
        for piece in game.board.pieces:
            color(layout['game'][str(piece.position)], piece.player)
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
                print(allowed)
                if allowed:
                    if selected == new_selected:
                        selected = 0
                        selected_tile = False
                    else:
                        selected = new_selected
                        selected_tile = highlighted_tile
        if selected_tile:
            color(selected_tile, "c")
        color(highlighted_tile, "h")

        refresh()

    print(game.get_winner())

startGame()