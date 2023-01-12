# sudo python3 local/checkers.py om te runnen
# sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel voor neopixel install
# pip3 install adafruit-circuitpython-neopixel
# sudo pip3 install --upgrade adafruit-python-shell
# wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
# sudo python3 raspi-blinka.py

import sys
import curses
import threading
import time
import random
from LEDboardController import LEDboardController
from joystickController import trackJoystick

joystickControllerThread = threading.Thread(target=trackJoystick)
joystickControllerThread.start()

global joystick_boven_pressed
global joystick_onder_pressed
global joystick_links_pressed
global joystick_rechts_pressed
global joystick_button_pressed

LED_board_dict = {}
LED_board = []
def LED_setTile(x,y,content):
    try:
        old_content = LED_board_dict[f"({x},{y})"]
        if old_content != content:
            LED_board.append({
                "x": x,
                "y": y,
                "content": content.replace(" ","e")
            })
    except:
        LED_board.append({
            "x": x,
            "y": y,
            "content": content.replace(" ","e")
        })
                 
    LED_board_dict[f"({x},{y})"] = content
    LEDboardController(LED_board)
    LED_board.clear()

# Game Functions
def consolePrint(text):
    with open('console.txt', 'a') as console:
        console.write(f"{text}\n")

def start():
    game_board = [
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 2, 1],
        [' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' '],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
    ]

    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN) 
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.cbreak()
    stdscr.keypad(1)

    stdscr.addstr(0, 10, 'Hit \'q\' to quit')
    stdscr.addstr(1, 10, 'Press any key to start...')
    stdscr.addstr(2, 10, 'Turn:')
    stdscr.addstr(3, 10, '----- --------')
    stdscr.refresh()

    player = random.randint(1,2)
    # current cursor position
    pos_x = 0
    pos_y = 0
    # selected disc x, y, and value (to preserve if king)
    sel_disc_x = -1
    sel_disc_y = -1
    sel_disc = ''
    disc_selected = False

    key = ''
    winner = 0
    playing = True
    while key != ord('q') or playing:
        key = stdscr.getch()
        stdscr.addstr(1, 10, '                         ')
        stdscr.addstr(2, 10, 'Turn: Player-%d' % player)
        tem_board = []
        for y in range(8):
            for i, x in enumerate(game_board[y]):
                if y % 2 == 0: # if border columns
                    add = i * 2
                else: # else altering columns
                    add = i * 2 + 1
                stdscr.addstr(add, y, str(x), curses.color_pair(1))
                LED_setTile(add,y,str(x))
        stdscr.refresh()

        # consolePrint(joystick_boven_pressed)
        if key == curses.KEY_UP:
            # if 2nd row, move one up-left (diagonal)
            if pos_x == 1:
                pos_x -= 1
                pos_y -= 1
            # else move two up (vertical)
            else:
                pos_x = pos_x - 2 if pos_x - 2 > 0 else 0
        if key == curses.KEY_DOWN:
            # if 7th row, move one bottom-right (diagonal)
            if pos_x == 6:
                pos_x += 1
                pos_y += 1
            # else move two down (vertical)
            else:
                pos_x = pos_x + 2 if pos_x + 2 < 7 else 7
        if key == curses.KEY_LEFT:
            # don't do anything at 0, 0 or x, 0
            if (pos_x == 0 and pos_y == 0) or pos_y == 0:
                pass
            # if topmost row, move bottom-left (diagonal)
            elif pos_x == 0 and pos_y != 0:
                pos_x += 1
                pos_y -= 1
            # if bottommost row, move top-left (diagonal)
            elif pos_x == 7:
                pos_x -= 1
                pos_y -= 1
            # if odd rows, move bottom-left (diagonal)
            elif pos_x % 2 == 1:
                pos_x -= 1
                pos_y -= 1
            # if even rows, move top-left (diagonal)
            else:
                pos_x += 1
                pos_y -= 1
        if key == curses.KEY_RIGHT:
            # don't do anything at 1, 7 or x, 7
            if (pos_x == 1 and pos_y == 7) or pos_y == 7:
                pass
            # if topmost row, move bottom-right (diagonal)
            elif pos_x == 0 and pos_y != 7:
                pos_x += 1
                pos_y += 1
            # if odd rows, move bottom-right (diagonal)
            elif pos_x % 2 == 1:
                pos_x -= 1
                pos_y += 1
            # if even rows, move top-right (diagonal)
            else:
                pos_x += 1
                pos_y += 1

        if key == 10:
            # clear cursor's position of clutter, e.g. b'1' into 1
            # FIXME: could probably use another replace instead of split join by single quote
            current_tile = str(''.join(str(stdscr.instr(pos_x, pos_y, 1)).split('\'')).replace('b', ''))

            # check if player selected a tile
            for row in game_board:
                if 'x' in row:
                    disc_selected = True

            # deselect disc if one is selected by selecting it again
            if disc_selected and current_tile == 'x':
                disc_selected = False
                sel_disc_x = -1
                sel_disc_y = -1
                game_board[pos_y][get_res_x(pos_y, pos_x)] = int(sel_disc)
                # consolePrint(f"Deselect selected disc | x: {pos_x} | y: {pos_y} | sel_disc: {sel_disc}")
                LED_setTile(pos_x,pos_y," ")
                stdscr.addstr(pos_x, pos_y, sel_disc, curses.color_pair(1))
                sel_disc = ''

            # select another disc when one is already selected
            if disc_selected and (current_tile == str(player) or current_tile == str(player + 2)):
                game_board[sel_disc_y][get_res_x(sel_disc_y, sel_disc_x)] = int(sel_disc)
                # consolePrint(f"Deselect disc | x: {sel_disc_x} | y: {sel_disc_y} | sel_disc: {sel_disc}")
                LED_setTile(sel_disc_x,sel_disc_y,sel_disc)
                stdscr.addstr(sel_disc_x, sel_disc_y, sel_disc, curses.color_pair(1))
                game_board[pos_y][get_res_x(pos_y, pos_x)] = 'x'
                sel_disc_x = pos_x
                sel_disc_y = pos_y
                sel_disc = current_tile
                # consolePrint(f"Select disc | x: {pos_x} | y: {pos_y} | (x)")
                LED_setTile(pos_x,pos_y,"x")
                stdscr.addstr(pos_x, pos_y, 'x', curses.color_pair(1))

            # TODO: add mandatory rule of destroying opponent's piece if in position
            if disc_selected and current_tile == ' ':
                illegal_move = True
                diff_x = int((pos_x - sel_disc_x) / 2)
                diff_y = int((pos_y - sel_disc_y) / 2)
                is_in_right_direction = calculate_direction(sel_disc_y, pos_y, sel_disc, player)
                opp_x, opp_y = calculate_opponent_pos(pos_x, pos_y, diff_x, diff_y)
                opponent_tile = str(''.join(str(stdscr.instr(opp_x, opp_y, 1)).split('\'')).replace('b', ''))
                opponent = str(1 if player == 2 else 2)

                # check if required to capture
                requirements_array = [] #is_required_to_capture(player, game_board, sel_disc) TEMP
                # only allow movement one step further or behind opponent
                if diff_x == 0 and diff_y == 0:
                    illegal_move = False
                elif opponent_tile == opponent or opponent_tile == str(int(opponent) + 2):
                    illegal_move = False
                    game_board[opp_y][get_res_x(opp_y, opp_x)] = ' '
                    # consolePrint(f"Empty spot | x: {opp_x} | y: {opp_y} | (' ')")
                    LED_setTile(opp_x,opp_y," ")
                    stdscr.addstr(opp_x, opp_y, ' ', curses.color_pair(1))
                else:
                    illegal_move = True
                if not is_in_right_direction:
                    illegal_move = True
                
                stdscr.addstr(8, 10, 'cur:  %s%s   ' % (pos_x, pos_y))
                capture_required = False
                if len(requirements_array) > 0:
                    capture_required = True
                    for reqs in requirements_array:
                        # FIXME: lets go even if the wrong piece moves to the tile without capturing the opponent
                        # should probably add a check to see if the opponent is gone
                        # which requires opponent to be also returned from the function, i think
                        if pos_x == get_act_x(reqs[0], reqs[1]) and pos_y == reqs[0]:
                            capture_required = False
                    # loop above to check if player moved to one of the required tiles
                    # highlight only if didn't move to one of the tiles
                    if capture_required:
                        for reqs in requirements_array:
                            stdscr.addstr(get_act_x(reqs[0], reqs[1]), reqs[0], ' ', curses.color_pair(2))

                if capture_required:
                    stdscr.addstr(5, 10, '!! Capture required')
                elif illegal_move:
                    stdscr.addstr(5, 10, '!! Illegal move    ')
                else:
                    stdscr.addstr(5, 10, '                   ')
                    # movement after if action is legal
                    for n, row in enumerate(game_board):
                        for i, x in enumerate(row):
                            if x == 'x':
                                # reset tile in board array
                                game_board[n][i] = ' '
                                stdscr.addstr(6, 10, '                              ')
                                # set current tile to player's disc
                                res_player = int(sel_disc)
                                stdscr.addstr(6, 10, '                              ')
                                # check if end of the board and disc isn't already a king
                                if is_at_end(pos_x, pos_y, player) and res_player < 3:
                                    res_player += 2
                                    stdscr.addstr(6, 10, '!! Player-%d crowned a king' % player)
                                game_board[pos_y][get_res_x(pos_y, pos_x)] = res_player
                                stdscr.addstr(pos_x, pos_y, str(res_player), curses.color_pair(1))
                                # consolePrint(f"String in spot | x: {pos_x} | y: {pos_y} | content: {str(res_player)}")
                                LED_setTile(pos_x,pos_y,str(res_player))
                                # temporarily draw onto tile where x was before re-draw
                                # consolePrint(f"String in spot | x: {get_act_x(n, i)} | y: {n} | (' ')")
                                LED_setTile(get_act_x(n, i),n," ")
                                stdscr.addstr(get_act_x(n, i), n, ' ', curses.color_pair(1))
                                disc_selected = False
                                sel_disc_x = -1
                                sel_disc_y = -1
                                sel_disc = ''
                                # change turn
                                player = 2 if player == 1 else 1
                                stdscr.addstr(2, 10, 'Turn: Player-%d' % player)

            if get_player_discs(game_board, 1) == 0:
                playing = False
                winner = 2
                break
            if get_player_discs(game_board, 2) == 0:
                playing = False 
                winner = 1      
                break           


            # if current tile is of player's disc select it
            if (current_tile == str(player) or current_tile == str(player + 2)) and not disc_selected:
                # set current tile to an x mark in board array
                game_board[pos_y][get_res_x(pos_y, pos_x)] = 'x'
                sel_disc_x = pos_x
                sel_disc_y = pos_y
                sel_disc = current_tile
                # temporarily draw x on current tile until re-draw on cursor move
                # consolePrint(f"String in spot | x: {pos_x} | y: {pos_y} | ('x')")
                LED_setTile(pos_x,pos_y,"x")
                stdscr.addstr(pos_x, pos_y, 'x', curses.color_pair(1))

            # notify that it is the opponent's turn when wrong disc is selected
            if (current_tile == str(1 if player == 2 else 2) or current_tile == str(3 if player == 2 else 4)) and not disc_selected:
                stdscr.addstr(4, 10, '!! Player-%d\'s turn' % player)
            else:
                stdscr.addstr(4, 10, '                    ')
            

        stdscr.move(pos_x, pos_y)
        LED_setTile(pos_x,pos_y, "c") #R

    curses.endwin()
    stdscr = False
    end(winner)


def get_player_discs(game_board, player):
    amount = 0
    for row in game_board:
        if player == 1:
            amount += row.count(1)
            amount += row.count(3)
        if player == 2:
            amount += row.count(2)
            amount += row.count(4)
    consolePrint(f"{game_board} ------ player: {player} ------- aantal: {amount}")
    return amount

def get_res_x(pos_y, pos_x):
    """Return the second level array position of a given tile."""
    if pos_y % 2 == 0:
        res_x = int(pos_x / 2)
    else:
        res_x = int((pos_x - 1 if pos_x > 0 else 0) / 2)
    return res_x

def get_act_x(pos_y, pos_x):
    """Do the reverse of above function. Array position into a tile position."""
    if pos_y % 2 == 0: # if border columns
        act_x = pos_x * 2
    else: # else altering columns
        act_x = pos_x * 2 + 1
    return act_x

def calculate_opponent_pos(new_x, new_y, diff_x, diff_y):
    """Calculate opponent's position by movement difference.
    
    args:
    new_x, new_y -- moved position of player
    diff_x, diff_y -- difference between starting and ending position
    """
    opp_x = new_x - diff_x
    opp_y = new_y - diff_y
    return opp_x, opp_y

def is_at_end(pos_x, pos_y, player):
    """Determine if player has reached end of the board and earned a promotion."""
    if player == 1:
        if pos_y == 0 and pos_x % 2 == 0:
            return True
        return False
    else:
        if pos_y == 7 and pos_x % 2 == 1:
            return True
        return False

def calculate_direction(old_y, new_y, disc, player):
    """Check if disc is moved in the correct direction.
    By checking difference between its old and new y val.
    Always true for kings.
    """
    if int(disc) > 2:
        return True
    if player == 1:
        if new_y < old_y:
            return True
    else:
        if new_y > old_y:
            return True
    return False

def is_required_to_capture(player, game_board, sel_disc):
    """Calculate if a player needs to make a capture based on the position of discs,
    and possible movement patterns.
    """
    required_moves = []
    if player == 2:
        opp = [1, 3]
        for y, row in enumerate(game_board):
            for x, disc in enumerate(row):
                if y % 2 == 0: # if even (not indented row)
                    # forward only move checks
                    if disc == player or disc == 'x':
                        if y + 2 < 8 and x - 1 >= 0: # valid top-right move
                            opp_space = game_board[y + 1][x - 1]
                            if opp_space in opp and game_board[y + 2][x - 1] == ' ':
                                required_moves.append([y + 2, x - 1])
                        if y + 2 < 8 and x + 1 < 4: # valid bottom-right move
                            opp_space = game_board[y + 1][x]
                            if opp_space in opp and game_board[y + 2][x + 1] == ' ':
                                required_moves.append([y + 2, x + 1])
                    # additional backward move checks for kings
                    if disc == player + 2 or (disc == 'x' and sel_disc == str(player + 2)):
                        if y - 2 >= 0 and x - 1 >= 0: # valid top-left move
                            opp_space = game_board[y - 1][x - 1]
                            if opp_space in opp and game_board[y - 2][x - 1] == ' ':
                                required_moves.append([y - 2, x - 1])
                        if y - 2 >= 0 and x + 1 < 4: # valid bottom-left move
                            opp_space = game_board[y - 1][x]
                            if opp_space in opp and game_board[y - 2][x + 1] == ' ':
                                required_moves.append([y - 2, x + 1])
                else: # if odd (indented row)
                    if disc == player or disc == 'x':
                        if y + 2 < 8 and x - 1 >= 0: # valid top-right move
                            opp_space = game_board[y + 1][x]
                            if opp_space in opp and game_board[y + 2][x - 1] == ' ':
                                required_moves.append([y + 2, x - 1])
                        if y + 2 < 8 and x + 1 < 4: # valid bottom-right move
                            opp_space = game_board[y + 1][x + 1]
                            if opp_space in opp and game_board[y + 2][x + 1] == ' ':
                                required_moves.append([y + 2, x + 1])
                    if disc == player + 2 or (disc == 'x' and sel_disc == str(player + 2)):
                        if y - 2 >= 0 and x - 1 >= 0: # valid top-left move
                            opp_space = game_board[y - 1][x]
                            if opp_space in opp and game_board[y - 2][x - 1] == ' ':
                                required_moves.append([y - 2, x - 1])
                        if y - 2 >= 0 and x + 1 < 4: # valid bottom-left move
                            opp_space = game_board[y - 1][x + 1]
                            if opp_space in opp and game_board[y - 2][x + 1] == ' ':
                                required_moves.append([y - 2, x + 1])
    else:
        opp = [2, 4]
        for y, row in enumerate(game_board):
            for x, disc in enumerate(row):
                if y % 2 == 0: # if even (not indented row)
                    # forward only move checks
                    if disc == player or disc == 'x':
                        if y - 2 >= 0 and x - 1 >= 0: # valid top-left move
                            opp_space = game_board[y - 1][x - 1]
                            if opp_space in opp and game_board[y - 2][x - 1] == ' ':
                                required_moves.append([y - 2, x - 1])
                        if y - 2 >= 0 and x + 1 < 4: # valid bottom-left move
                            opp_space = game_board[y - 1][x]
                            if opp_space in opp and game_board[y - 2][x + 1] == ' ':
                                required_moves.append([y - 2, x + 1])
                    # additional backward move checks for kings
                    if disc == player + 2 or (disc == 'x' and sel_disc == str(player + 2)):
                        if y + 2 < 8 and x - 1 >= 0: # valid top-right move
                            opp_space = game_board[y + 1][x - 1]
                            if opp_space in opp and game_board[y + 2][x - 1] == ' ':
                                required_moves.append([y + 2, x - 1])
                        if y + 2 < 8 and x + 1 < 4: # valid bottom-right move
                            opp_space = game_board[y + 1][x]
                            if opp_space in opp and game_board[y + 2][x + 1] == ' ':
                                required_moves.append([y + 2, x + 1])
                else: # if odd (indented row)
                    if disc == player or disc == 'x':
                        if y - 2 >= 0 and x - 1 >= 0: # valid top-left move
                            opp_space = game_board[y - 1][x]
                            if opp_space in opp and game_board[y - 2][x - 1] == ' ':
                                required_moves.append([y - 2, x - 1])
                        if y - 2 >= 0 and x + 1 < 4: # valid bottom-left move
                            opp_space = game_board[y - 1][x + 1]
                            if opp_space in opp and game_board[y - 2][x + 1] == ' ':
                                required_moves.append([y - 2, x + 1])
                    if disc == player + 2 or (disc == 'x' and sel_disc == str(player + 2)):
                        if y + 2 < 8 and x - 1 >= 0: # valid top-right move
                            opp_space = game_board[y + 1][x]
                            if opp_space in opp and game_board[y + 2][x - 1] == ' ':
                                required_moves.append([y + 2, x - 1])
                        if y + 2 < 8 and x + 1 < 4: # valid bottom-right move
                            opp_space = game_board[y + 1][x + 1]
                            if opp_space in opp and game_board[y + 2][x + 1] == ' ':
                                required_moves.append([y + 2, x + 1])

    return required_moves

def end(winner):
    consolePrint("GAME ENDED")
    consolePrint(f"{winner} won")
    time.sleep(5)
    start()

if __name__ == '__main__':
    start()