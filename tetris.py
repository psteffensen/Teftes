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
import pdb


LINES_TO_ADVANCE = 10 #num lines needed to advance to next  
LEVEL_SPEEDS = range(500,50,-50)

NRPLAYERS = 3
MAXX = 10
MAXY = 20
(LEFT, RIGHT, UP, DOWN, DROP, DIE) = range(6) 

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
                        print rows_deleted
                        if rows_deleted is 1:
                            self.score += 10
                        elif rows_deleted is 2:
                            self.score += 25
                        elif rows_deleted is 3:
                            self.score += 40
                        elif rows_deleted is 4:
                            self.score += 55
                        
                        # Give packages to the other players
                        if self.gs.num_players >= 2:
                            if rows_deleted > 1:
                                for op in self.other_players:
                                    self.boards[op].receive_lines(rows_deleted-1) 
           
                        # If the shape returned is None, then this indicates that
                        # that the check before creating it failed and the
                        # game is over!
                        if self.shape is None:
                            self.gs.state = "ending" #you lost!
                            if self.gs.num_players > 2:
                                self.gs.winner = (self.id + 1) % 2 #Must be updated for more than two players.
                            else:
                                self.gs.winner = self.id
                                
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
    def __init__(self):
        self.shapes = [square_shape, t_shape,l_shape, reverse_l_shape,
                      z_shape, s_shape,i_shape ]
        self.num_players = 0
        self.level = 0 #levels go 0-9
        self.delay = LEVEL_SPEEDS[0]
        self.state = "waiting" #states: waiting (between games), playing, ending
        self.winner = None #winning player id
       
        
        
#runs the overall game. initializes both player and any displays
class TetrisGame(object):

    #one-time initialization for gui etc
    def __init__(self):
        print "initialize tetris"
        #self.DISPLAY_SIZE = (1920, 1080) #Manually set screensize
        self.gui = PygameGoodRenderer()
        self.input = DdrInput()
        
        self.gui.SetupScreen()
        self.gameState = GameState()
        while True:
            self.init_game()
            

    #initializes each game
    def init_game(self):
        print "init next game"
        self.boards = [] #reset boards
        self.players = [] #reset players
        for player in range(NRPLAYERS):
            self.boards.append(Board(MAXX,MAXY))
            self.players.append(None)
            self.board_animation(player,"up_arrow")
        self.shapes = GenerateShapes(self.gameState)
        self.input.reset()
        self.gui.load_theme(theme = "RussianTheme")
        self.update_gui()
        self.handle_input() #this calls all other functions, such as add_player, start_game


    def add_player(self,num): # num is player number
        print "adding player",num
        if self.players[num]==None:
            self.boards[num].clear()
            other_players = range(NRPLAYERS)
            other_players.pop(num) #all other players
            p = Player(num, self.gameState, self.boards, other_players, self.shapes)
            print "Player" + str(num) + "added"
            self.players[num] = p
            self.board_animation(num,"down_arrow")
            self.gameState.num_players+=1
            self.update_gui()
        
    def start_game(self):
        print "start game"
        for n in range(NRPLAYERS):
            self.boards[n].clear()
        self.gameState.state = "playing"
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
                
            ev = self.input.poll()
            if ev:
                player,direction = ev
                #print "Player",player,direction
                if direction == DIE: #Exit instruction
                    game_on = False
                    pygame.quit()
                    sys.exit()
                if self.gameState.state=="playing":
                    if self.players[player]!=None:
                        #DROP is only for debugging purposes for now, to make the game end.
                        if direction == DROP:
                            while self.players[player].handle_move(DOWN):
                                pass
                        else:
                            self.players[player].handle_move(direction)
                elif self.gameState.state == "waiting":
                    if direction==UP:
                        self.add_player(player)
                    elif direction==DOWN:
                        if self.players[player]!=None:
                            self.start_game()
                
                self.update_gui()
         
            elif t%10000==0:
                t=0
                self.update_gui()
                
                
                
    def gravity(self):
        for p in self.players:
            if p:
                p.handle_move(DOWN)
            
    def update_gui(self):
        self.gui.render_game(self.to_gui_dict())

    def end_game(self):
        if self.gameState.winner!=None:
            winner_id = self.gameState.winner
            print "GAME OVER: player",winner_id,"wins"
        else:
            if self.gameState.num_players == 2:
                if self.players[0].score > self.players[1].score:
                    winner_id = 0
                elif self.players[1].score > self.players[0].score:
                    winner_id = 1
                else:
                    winner_id = 2 #tie, show both as winners.
            elif self.players[0]!=None:
                winner_id = 0
            else:
                winner_id = 1
        del self.gameState
        self.gameState = GameState()
        self.animate_ending(winner_id)
        pygame.mixer.music.stop()

    def board_animation(self, board_id, design, color="green"):
        b = self.boards[board_id]
        d = self.create_shapes(design)
        for coord in d:
            #sleep(0.005)
            b.landed[coord]=color
            #self.update_gui()
                        
    def animate_ending(self,winner_board):
        if winner_board == 2:
            self.board_animation(0,"outline")
            self.board_animation(1,"outline")
        else:
            self.board_animation(winner_board,"outline","yellow")
        self.update_gui()
        sleep(3)

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
        sides = [(i,j) for i in [0,9] for j in range(18)]
        tb = [(i,j) for i in range(10) for j in [0,17]]
        outline = tb + sides
            
        shapes["down_arrow"] = down_arrow
        shapes["up_arrow"] = up_arrow
        shapes["outline"] = outline
        shapes["test"] = [(5,5)]
        
        return shapes[design]

    def to_gui_dict(self):
        d = {}
        d["max_y"] = MAXY
        d["max_x"] = MAXX
        d["nr_players"] = NRPLAYERS
        d["level"] = self.gameState.level
        
                
        for n in range(NRPLAYERS):
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
