#!/usr/bin/env python
# Burton-Conner Tetris Battle -- Tetris installation controlled by DDR pads
# Copyright (C) 2010, 2011  Simon Peverett <http://code.google.com/u/@WRVXSlVXBxNGWwl1/>
# Copyright (C) 2011  Russell Cohen <rcoh@mit.edu>,
#                     Leah Alpert <lalpert@mit.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Tetris Tk - A tetris clone written in Python using the Tkinter GUI library.

Controls:
    Left/a      Move left
    Right/d     Move right
    Up/w        Rotate / add player
    Down/s      Move down / start game
"""

from time import sleep, time
import random
import sys
from renderer import PygameGoodRenderer
from tetris_shape import *
from ddrinput import DdrInput
from ddrinput import DIRECTIONS
import pygame


LINES_TO_ADVANCE = 10 #num lines needed to advance to next  
LEVEL_SPEEDS = range(500,50,-50)

#NRPLAYERS = 2
MAXX = 10
MAXY = 20
(LEFT, RIGHT, UP, DOWN, DROP, DIE, RELEASE) = range(7) 

COLORS = ["orange", "red", "green", "blue", "purple", "yellow", "magenta"]
LEVEL_COLORS = ["red", "orange", "yellow", "green", "blue", "purple","orange","magenta", "white"]

#pygame.init()
#BASICFONT = pygame.font.Font('freesansbold.ttf', 18)



class Board():
    """
    The board represents the tetris playing area. A grid of x by y blocks.
    Stores blocks that have landed.
    """
    def __init__(self, max_x=10, max_y=20): 
        # blocks are stored in dict of (x,y)->"color"
        self.landed = {}
        self.max_x = max_x
        self.max_y = max_y

    def clear(self):
        self.landed = {}
      
    def receive_lines(self, num_lines): #Lines received when opposite player gets more than one line.
        #shift lines up
        for y in range(self.max_y-num_lines):
            for x in xrange(self.max_x):
                block_color = self.landed.pop((x,y+num_lines),None)
                if block_color:
                    self.landed[(x,y)] = block_color
        #put in new lines
        for j in range(num_lines):
            for i in random.sample(xrange(self.max_x), random.choice([6,7])):
                self.landed[(i,self.max_y-1-j)] = random.choice(COLORS)
                
    def check_for_complete_row( self, blocks ):
        """
        Look for a complete row of blocks, from the bottom up until the top row
        or until an empty rowf is reached.
        """
        rows_deleted = 0
        
        # Add the blocks to those in the grid that have already 'landed'
        for block in blocks:
            self.landed[ block.coord() ] = block.color
        
        empty_row = 0
        # find the first empty row
        for y in xrange(self.max_y -1, -1, -1):
            row_is_empty = True
            for x in xrange(self.max_x):
                if self.landed.get((x,y), None):
                    row_is_empty = False
                    break;
            if row_is_empty:
                empty_row = y
                break

        # Now scan up and until a complete row is found. 
        y = self.max_y - 1
        while y > empty_row:
 
            complete_row = True
            for x in xrange(self.max_x):
                if self.landed.get((x,y), None) is None:
                    complete_row = False
                    break;

            if complete_row:
                rows_deleted += 1
                
                #delete the completed row
                for x in xrange(self.max_x):
                    self.landed.pop((x,y))
                    
                # move all the rows above it down
                for ay in xrange(y-1, empty_row, -1):
                    for x in xrange(self.max_x):
                        block_color = self.landed.pop((x,ay), None)
                        if block_color:
                            dx,dy = (0,1)
                            self.landed[(x+dx, ay+dy)] = block_color

                # move the empty row index down too
                empty_row +=1
                # y stays same as row above has moved down.       
            else:
                y -= 1
            
        # return the number of rows deleted.        
        return rows_deleted

    def check_block(self, (x, y) ):
        """
        Check if the x, y coordinate can have a block placed there.
        That is; if there is a 'landed' block there or it is outside the
        board boundary, then return False, otherwise return true.
        """
        if x < 0 or x >= self.max_x or y < -3 or y >= self.max_y:
            return False
        elif self.landed.has_key( (x, y) ):
            return False
        else:
            return True


#represents a player. each player has a board, other player's board,
#current shape, score, etc
class Player():
    def __init__(self, player_id, gs, boards, other_players, shapes):
        self.other_players = other_players
        self.shapes = shapes
        self.id = player_id
        self.boards = boards
        self.score = 0
        self.lines = 0
        self.gs = gs
        self.shape_nr = 0
        self.the_shape = self.shapes.get_shape(self.shape_nr)
        self.shape = self.the_shape.check_and_create(self.boards[self.id])
        self.the_nextshape = self.shapes.get_shape(self.shape_nr+1)
        self.nextshape = self.the_nextshape.check_and_create(self.boards[self.id])
        
    def handle_move(self, direction):
        #if you can't move then you've hit something
        if self.shape:
            if direction==UP:
                self.shape.rotate(clockwise=False)
                print "handle_move up"
            elif direction == RELEASE:
                pass #Do nothing
            else:
                if not self.shape.move(direction):
                    # if you're heading down then the shape has 'landed'
                    if direction == DOWN:
                        rows_deleted = self.boards[self.id].check_for_complete_row(self.shape.blocks)
                        self.shape_nr += 1
                        self.the_shape = self.shapes.get_shape(self.shape_nr)
                        self.shape = self.the_shape.check_and_create(self.boards[self.id])
                        self.the_nextshape = self.shapes.get_shape(self.shape_nr+1)
                        self.nextshape = self.the_nextshape.check_and_create(self.boards[self.id])
                        
                        self.lines += rows_deleted
                        # Score calculation
                        if rows_deleted is 1:
                            self.score += 10
                        elif rows_deleted is 2:
                            self.score += 25
                        elif rows_deleted is 3:
                            self.score += 40
                        elif rows_deleted is 4:
                            self.score += 55
                        
                        # Give packages to the other players
			num = len(self.gs.active_players)
                        if num >= 2:
                            if rows_deleted > (num-1):
                                for op in self.gs.active_players: 
                                    if op == self.id:
					pass
				    else:
					self.boards[op].receive_lines(rows_deleted-(num-1))
			    elif num > 4 and rows_deleted == 4:
                                for op in self.gs.active_players: 
                                    if op == self.id:
					pass
				    else:
				        self.boards[op].receive_lines(1) # if more that four players: 1 package.
				
			del num
				 
           
                        # If the shape returned is None, then this indicates that
                        # that the check before creating it failed and the
                        # game is over!
                        if self.shape is None:
                            if self.gs.num_players >= 2 and len(self.gs.active_players)-1 >= 2:
                                print "List after pop " + str(self.gs.active_players)
                                #return None
                            elif self.gs.num_players >= 2 and len(self.gs.active_players)-1 < 2:
                                self.gs.winner = self.gs.active_players[0] # winner is last active player
                                print "List after last pop " + str(self.gs.active_players)
                                print "winner is " + str(self.gs.winner)
                                self.gs.state = "ending" #you lost!
                            else:                                
                                return ValueError("Did not end correctly!")
                                #game ends
                            self.gs.active_players.remove(self.id)
                            #del self

                        # do we go up a level?
                        if (self.gs.level < len(LEVEL_SPEEDS)-1 and self.lines / LINES_TO_ADVANCE >= self.gs.level+1 ):
                            self.gs.level+=1
                            print "level",self.gs.level
                            print LEVEL_SPEEDS
                            print "Level right now:", LEVEL_SPEEDS[self.gs.level]
                            self.gs.delay = LEVEL_SPEEDS[self.gs.level]
                        
                        # Signal that the shape has 'landed'
                        return False
        return True

                
#Generates a lot of shapes that are queued for the         
#players. So the players will get the same shapes.
class GenerateShapes(object):
    def __init__(self, gs):
        #generate shapes
        self.gs = gs
        self.the_shape = []
        for i in range(10000): # Choose a really high number so we dont run out of shapes.
            self.the_shape.append(self.gs.shapes[ random.randint(0,len(self.gs.shapes)-1) ])
        #get shape by nr.
        
    def get_shape(self, shape_nr):
        return self.the_shape[shape_nr]

        
#contains variables that are shared between the players:
#levels, delay time, etc
class GameState():
    def __init__(self, num_players):
        self.shapes = [square_shape, t_shape,l_shape, reverse_l_shape,
                      z_shape, s_shape,i_shape ]
        self.level = 0 #levels go 0-9
        self.delay = LEVEL_SPEEDS[0]
        self.state = "waiting" #states: waiting (between games), playing, ending
        self.winner = None #winning player id
        self.active_players = []
        self.instruction = False
        self.num_players = num_players
        
#runs the overall game. initializes both player and any displays
class TetrisGame(object):

    #one-time initialization for gui etc
    def __init__(self):
        print "initialize tetris"
        #self.DISPLAY_SIZE = (1920, 1080) #Manually set screensize
        self.gui = PygameGoodRenderer()
        self.input = DdrInput()
        self.num_players = self.input.totaljoy
        self.gui.SetupScreen()
        self.gameState = GameState(self.num_players)
        if self.num_players is 0: # If no joypad connected then 4 players on keyboard.
            self.num_players = 4
            
        while True:
            self.init_game()
            

    #initializes each game
    def init_game(self):
        print "init next game"
        self.boards = [] #reset boards
        self.players = [] #reset players
        for player in range(self.num_players):
            self.boards.append(Board(MAXX,MAXY))
            self.players.append(None)
            self.board_animation(player,"up_arrow")
        self.shapes = GenerateShapes(self.gameState)
        self.input.reset()
        self.gui.load_theme(MAXY, theme = "RussianTheme")
        self.gui.render_game_init(self.to_gui_dict_init())
        self.instruction = True
        self.update_gui()
        self.handle_input() #this calls all other functions, such as add_player, start_game
        

    def add_player(self,num, controller): # num is player number
        print "adding player",num
        if self.players[num]==None:
            self.boards[num].clear()
            other_players = range(self.num_players)
            other_players.pop(num) #all other players
            p = Player(num, self.gameState, self.boards, other_players, self.shapes)
            print "Player" + str(num) + "added"
            self.players[num] = p
            self.players[num].controller = controller
            self.board_animation(num,"down_arrow")
            self.gameState.num_players+=1
            self.gameState.active_players.append(num)
            self.update_gui()
        
    def start_game(self):
        print "start game"
        for n in range(self.num_players):
            self.boards[n].clear()
        self.gameState.state = "playing"
        self.instruction = False
        self.gui.render_game_init(self.to_gui_dict_init())
        self.update_gui()
        self.drop_time = time()
        self.gravity()
        pygame.mixer.music.load('./Themes/RussianTheme/session.mp3')
        pygame.mixer.music.play(-1)
        
        

    def handle_input(self):
        game_on = True
        t = 0
        while game_on:
            t+=1    
            if (self.gameState.state=="ending"):
                self.end_game()
                game_on = False
            
            if self.gameState.state=="playing" and time()-self.drop_time > self.gameState.delay/1000.0:
                self.gravity()
                self.drop_time = time()
                if self.gameState.state != "ending":
                    self.update_gui()
            
            
            player, button = self.input.poll() #If keyboard event UP, DOWN... directions will work, with joypad we get: button.
            if player is None or button is None:
                pass #Do not do anything if None
            elif self.gameState.state=="playing":
                #print "Player " + str(player) + ", Controller " + self.players[player].controller + "Button " + button
                if self.players[player]!=None:
                    if self.players[player].controller == 'Lefthanded':
                        if button is 'arrowLeft':
                            player_move = LEFT
                        elif button is 'arrowRight':
                            player_move = RIGHT
                        elif button is 'arrowUp':
                            player_move = UP
                        elif button is 'arrowDown':
                            player_move = DOWN
                        elif button is 'roundDown':
                            player_move = DROP
                        elif button is 'release':
                            player_move = RELEASE
                        
                    elif self.players[player].controller == 'Righthanded':
                        if button is 'roundLeft':
                            player_move = LEFT
                        elif button is 'roundRight':
                            player_move = RIGHT
                        elif button is 'roundUp':
                            player_move = UP
                        elif button is 'roundDown':
                            player_move = DOWN
                        elif button is 'arrowDown':
                            player_move = DROP
                        elif button is 'release':
                            player_move = RELEASE
                        
                        
                    elif self.players[player].controller == 'Keyboard':
                        player_move = button

                    if player_move == DROP:
                            while self.players[player].handle_move(DOWN):
                                pass
                    else:
                        self.players[player].handle_move(player_move)

                self.update_gui()
                
            elif self.gameState.state == "waiting":
                if button is 'roundUp':
                    self.add_player(player,'Righthanded')
                elif button is 'arrowUp':
                    self.add_player(player,'Lefthanded')
                elif button is UP:
                    self.add_player(player,'Keyboard')
                    
                elif button is 'roundDown' or button is 'arrowDown' or button is DOWN:
                    if self.players[player]!=None:
                        self.start_game()
                self.update_gui()
            
            #sleep(0.01)
            if t%10000==0:
                t=0
                self.update_gui()
                
                
                
    def gravity(self):
        for p in self.players:
            if p:
                p.handle_move(DOWN)
            
    def update_gui(self):
        if self.instruction:
            self.gui.render_game_init(self.to_gui_dict_init())
            self.gui.render_game(self.to_gui_dict())
            self.gui.render_instruction()
        else:
            self.gui.render_game_init(self.to_gui_dict_init())
            self.gui.render_game(self.to_gui_dict())
        self.gui.update()
        
    def end_game(self):
        print "end-game"
        if self.gameState.winner!=None:
            winner_id = self.gameState.winner
            print "GAME OVER: player",winner_id,"wins"
        del self.gameState
        self.gameState = GameState(self.num_players)
        self.animate_ending(winner_id)
        pygame.mixer.music.stop()
        
        # Up date number of players (loypads)
        self.num_players = self.input.totaljoy
        if self.num_players is 0: # If no joypad connected then 4 players on keyboard.
            self.num_players = 4
        

    def board_animation(self, board_id, design, color="green"):
        b = self.boards[board_id]
        d = self.create_shapes(design)
        for coord in d:
            #sleep(0.005)
            b.landed[coord]=color
            #self.update_gui()
                        
    def animate_ending(self,winner_board):
        self.board_animation(winner_board,"outline","yellow")
        self.update_gui()
        sleep(2)
        
        #escape = True
        #while escape:
        #    ev = self.input.poll()
        #    if ev:
        #        player,direction = ev
        #        #print "Player",player,direction            
        #        if direction == UP:
        #            escape = False
        #        else:
        #            escape = True
        #    else:
        #        sleep(0.2)
	sleep(2)
	
    def create_shapes(self,design): #in progress.....
        shapes = {}
        y = 4
        up_diags = [(1,y+4),(1,y+3),(2,y+3),(2,y+2),(3,y+2),(3,y+1),
                 (8,y+4),(8,y+3),(7,y+3),(7,y+2),(6,y+2),(6,y+1)]
        down_diags = [(x0,10-y0+2*y) for (x0,y0) in up_diags]
        line = [(i,j) for i in [4,5] for j in range(y,y+11)]
        up_arrow = line[:]
        for xy in up_diags:
            up_arrow.append(xy)
        down_arrow = line[:]
        for xy in down_diags:
            down_arrow.append(xy)
        sides = [(i,j) for i in [0,9] for j in range(MAXY)]
        tb = [(i,j) for i in range(10) for j in [0,MAXY-1]]
        outline = tb + sides
            
        shapes["down_arrow"] = down_arrow
        shapes["up_arrow"] = up_arrow
        shapes["outline"] = outline
        shapes["test"] = [(5,5)]
        
        return shapes[design]

    def to_gui_dict_init(self):
        d = {}
        d["max_y"] = MAXY
        d["max_x"] = MAXX
        d["nr_players"] = self.num_players
        d["level"] = self.gameState.level
        
        return d
        


    def to_gui_dict(self):
        d = {}                
        for n in range(self.num_players):
            #blocks
            d["board_landed_player" + str(n)] = self.boards[n].landed

            if self.players[n]!=None:
                p = self.players[n]
                #score
                d["score_player" + str(n)] = p.score
                d["lines_player" + str(n)] = p.lines
                
                #shapes
                if p.shape:
                    d["blocks_player" + str(n)] = p.shape.blocks
                            
                #next shape
                if p.nextshape:
                    d["nextshape_player" + str(n)] = p.nextshape.blocks
                   
        return d

            
if __name__ == "__main__":
    print """Burton-Conner Tetris Battle  Copyright (C) 2010, 2011  Simon Peverett
                             Copyright (C) 2011 Russell Cohen, Leah Alpert
This program comes with ABSOLUTELY NO WARRANTY; for details see
<http://gnu.org/licenses/gpl#section15>.
This is free software, and you are welcome to redistribute it under certain
conditions; see <http://gnu.org/licenses/gpl#content> for details."""

    tetrisGame = TetrisGame()
