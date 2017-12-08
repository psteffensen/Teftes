# renderer.py
# Copyright (C) 2011  Russell Cohen <rcoh@mit.edu>,
#                     Leah Alpert <lalpert@mit.edu>
#
# This file is part of Burton-Conner Tetris Battle.
#
# Burton-Conner Tetris Battle is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Burton-Conner Tetris Battle is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Burton-Conner Tetris Battle.  If not, see
# <http://www.gnu.org/licenses/>.

from numpy import zeros

import pygame, random, glob
from pygame.locals import Color

import util

class Renderer(object):
  def render_game(self, game_board):
    """
    renderBoard
    @param game_board -- dictionary of tuples of location (x,y), 0 indexed from
    the top left of the board.
    """
    raise NotImplementedError

  def color_deref(self, color_str):
    return Color(color_str)

class PygameGoodRenderer(Renderer):
 
  """
  Based heavily off of PygameRenderer in SmootLight.  Renders Tetris to a 
  pygame Window.
  """
  #MAXX = 10
  #MAXY = 20
  #NRPLAYERS = 2 #Number of players
  #DISPLAY_SIZE = (800,480)
  

  def __init__(self):
    pygame.init()
    
    infoObject = pygame.display.Info()
    self.DISPLAY_SIZE = (infoObject.current_w,infoObject.current_h)
    #self.DISPLAY_SIZE = (800,480)
    print self.DISPLAY_SIZE
    
    self.background = pygame.Surface(self.DISPLAY_SIZE)
    #self.screen = pygame.display.set_mode(self.DISPLAY_SIZE)
    self.screen = pygame.display.set_mode(self.DISPLAY_SIZE, pygame.FULLSCREEN | pygame.HWSURFACE)
    #pygame.display.toggle_fullscreen()
    
    pygame.display.set_mode(self.DISPLAY_SIZE)
    
                
    self.background = self.background.convert()
    self.background.fill(Color(0,0,0))
    self.extra_top_bottom = 3

    pygame.mouse.set_visible(0)
    
  def SetupScreen(self):
    pygame.display.set_mode(self.DISPLAY_SIZE)

  def load_theme(self, MAXY, theme = 'RussianTheme'):
    # Choose random background in theme folder
    types = ['jpg','jpeg','png']
    backgrounds = []
    flat_list = []
    for t in types:
        backgrounds.append(glob.glob('./Themes/' + str(theme) + '/*.' + str(t))) #get name of pictures in theme folder
    for sublist in backgrounds: # Change from list of lists to flat list.
        for item in sublist:
            flat_list.append(item)
    background = random.choice(flat_list) 
    self.bg = pygame.image.load(background)
    self.bg = pygame.transform.scale(self.bg, self.DISPLAY_SIZE)
    self.count = 0
    #Load font
    self.SCALE = int(self.DISPLAY_SIZE[1]/(MAXY+self.extra_top_bottom*2)) # squares in board area plus extra on top and buttom
    self.font = pygame.font.Font('./Themes/' + str(theme) + '/' + 'troika.otf', int(self.SCALE*1.0))
  
  def update(self):
    self.screen.blit(self.background, (0,0))
    pygame.display.flip()

   
  def render_game_init(self, game_board):
    self.MAXX = game_board["max_x"]
    self.MAXY = game_board["max_y"]
    self.NRPLAYERS = game_board["nr_players"]
    
    # Calculations depending on screen dimensions
    self.SCALE = int(self.DISPLAY_SIZE[1]/(self.MAXY+self.extra_top_bottom*2)) # squares in board area plus extra on top and buttom
    self.GAP = ((self.DISPLAY_SIZE[0]/self.SCALE)-self.MAXX*self.NRPLAYERS)/(self.NRPLAYERS)
    self.OFFSET = ((self.DISPLAY_SIZE[0]-(self.MAXX*self.SCALE*self.NRPLAYERS+self.GAP*self.SCALE*(self.NRPLAYERS-1)))/2, self.extra_top_bottom*self.SCALE)
      
    # Draw background
    self.background.fill(Color(0,0,0))
    self.background.blit(self.bg, (0, 0))  

  def render_instruction(self):
    ## Draw instruction
    
    button_color = (180,50,50)
    text_color = (150,150,150)
    x = self.DISPLAY_SIZE[0]/2
    y = self.OFFSET[1]+int(1.5*self.SCALE)
    line_width = 8
    
    # Draw transparent rectangle
    width = 20*self.SCALE
    height = 17*self.SCALE
    s = pygame.Surface((width, height))  # the size of your rect
    s.set_alpha(230)                # alpha level
    s.fill((50,50,50))           # this fills the entire surface
    self.background.blit(s, ( (self.DISPLAY_SIZE[0]-width)/2, y))    # (0,0) are the top-left coordinates
    
    ## Draw buttons
    # Left Up button
    pygame.draw.circle(self.background, button_color, (x+int(5.5*self.SCALE), y+int(7*self.SCALE)), int(self.SCALE*0.7), 0)
    # Left Down button
    pygame.draw.circle(self.background, button_color, (x+int(5.5*self.SCALE), y+int(10*self.SCALE)), int(self.SCALE*0.7), 0)
    # Left Left button
    pygame.draw.circle(self.background, button_color, (x+int(4*self.SCALE), y+int(8.5*self.SCALE)), int(self.SCALE*0.7), 0)
    # Left Left button
    pygame.draw.circle(self.background, button_color, (x+int(7*self.SCALE), y+int(8.5*self.SCALE)), int(self.SCALE*0.7), 0)
    
    # Right Up/Down Button
    pygame.draw.rect(self.background, button_color, [x-int(7*self.SCALE), 
                                                    y+int(8*self.SCALE), 
                                                    int(self.SCALE*3), 
                                                    int(self.SCALE*1)], 0)
    # Right Left/Right Button
    pygame.draw.rect(self.background, button_color, [x-int(6*self.SCALE), 
                                                    y+int(7*self.SCALE), 
                                                    int(self.SCALE*1), 
                                                    int(self.SCALE*3)], 0)
    
    # Menu and pause button
    pygame.draw.line(self.background, button_color, (x-int(0.5*self.SCALE), y+int(7.75*self.SCALE)), 
                                                    (x-int(1.5*self.SCALE), y+int(9.25*self.SCALE)), 
                                                    self.SCALE/2)
                                                    
    pygame.draw.line(self.background, button_color, (x+int(1.5*self.SCALE), y+int(7.75*self.SCALE)), 
                                                    (x+int(0.5*self.SCALE), y+int(9.25*self.SCALE)), 
                                                    self.SCALE/2)
                                                    
    # Draw Outline
    pygame.draw.arc(self.background, button_color, (x+int(1.5*self.SCALE),y+int(4.5*self.SCALE),int(self.SCALE*8),int(self.SCALE*8)), -0.75*3.14, 0.5*3.14, line_width)
    pygame.draw.arc(self.background, button_color, (x-int(9.5*self.SCALE),y+int(4.5*self.SCALE),int(self.SCALE*8),int(self.SCALE*8)), 0.5*3.14, -0.25*3.14, line_width)
    pygame.draw.line(self.background, button_color, (x+int(5.5*self.SCALE)+line_width/2, y+int(4.5*self.SCALE)+line_width/2), 
                                                    (x-int(5.5*self.SCALE)-line_width/2, y+int(4.5*self.SCALE)+line_width/2), 
                                                    line_width)
    pygame.draw.line(self.background, button_color, (x+int(2.5*self.SCALE)+self.SCALE/3, y+int(11.5*self.SCALE)-line_width), 
                                                    (x-int(2.5*self.SCALE)-self.SCALE/3, y+int(11.5*self.SCALE)-line_width), 
                                                    line_width)
                                                    
    ## Add text
    text = "Press up for right or left hand control"
    text = self.font.render(text, True, text_color)
    textpos = (x-int(9.2*self.SCALE), y+2*self.SCALE)
    self.background.blit(text, textpos)
    
    
    text = "Press down to start game"
    text = self.font.render(text, True, text_color)
    textpos = (x-int(6*self.SCALE), y+14*self.SCALE)
    self.background.blit(text, textpos)
    '''
    text = "Menu Pause"
    text = self.font.render(text, True, text_color)
    textpos = (x+int(-3*self.SCALE), y+int(9.5*self.SCALE))
    self.background.blit(text, textpos)
    '''
    
    # Circle around buttons
    pygame.draw.circle(self.background, text_color, [x+int(5.5*self.SCALE), y+int(7*self.SCALE)], self.SCALE, line_width)
    pygame.draw.circle(self.background, text_color, [x-int(5.5*self.SCALE), y+int(7*self.SCALE)], self.SCALE, line_width)
    pygame.draw.circle(self.background, text_color, [x+int(5.5*self.SCALE), y+int(10*self.SCALE)], self.SCALE, line_width)
    pygame.draw.circle(self.background, text_color, [x-int(5.5*self.SCALE), y+int(10*self.SCALE)], self.SCALE, line_width)
    
    ## Draw line to circles
    # Left Up
    pygame.draw.line(self.background, text_color, (x+int(4.85*self.SCALE), y+int(6.35*self.SCALE)), 
                                                    (x+int(2*self.SCALE), y+int(4*self.SCALE)), 
                                                    line_width)
    pygame.draw.line(self.background, text_color, (x+int(2*self.SCALE), y+int(3.2*self.SCALE)), 
                                                    (x+int(2*self.SCALE), y+int(4*self.SCALE)), 
                                                    line_width)
    # Right Up
    pygame.draw.line(self.background, text_color, (x-int(4.85*self.SCALE), y+int(6.35*self.SCALE)), 
                                                    (x-int(2*self.SCALE), y+int(4*self.SCALE)), 
                                                    line_width)
    pygame.draw.line(self.background, text_color, (x-int(2*self.SCALE), y+int(3.2*self.SCALE)), 
                                                    (x-int(2*self.SCALE), y+int(4*self.SCALE)), 
                                                    line_width)
    
    # Left Down
    pygame.draw.line(self.background, text_color, (x+int(4.55*self.SCALE), y+int(10.05*self.SCALE)), 
                                                    (x+int(2*self.SCALE), y+int(13*self.SCALE)), 
                                                    line_width)
    pygame.draw.line(self.background, text_color, (x+int(2*self.SCALE), y+int(14*self.SCALE)), 
                                                    (x+int(2*self.SCALE), y+int(13*self.SCALE)), 
                                                    line_width)
    
    # Right Down
    pygame.draw.line(self.background, text_color, (x-int(4.55*self.SCALE), y+int(10.05*self.SCALE)), 
                                                    (x-int(2*self.SCALE), y+int(13*self.SCALE)), 
                                                    line_width)
    pygame.draw.line(self.background, text_color, (x-int(2*self.SCALE), y+int(14*self.SCALE)), 
                                                    (x-int(2*self.SCALE), y+int(13*self.SCALE)), 
                                                    line_width)
    
  def render_game(self, game_board):
    ##Draw game_board
    board_dist = self.SCALE * (self.MAXX + self.GAP) #x offset for second board
    x = []
    y = []
    for player in range(self.NRPLAYERS):
        x.append(self.OFFSET[0]+player*self.MAXX*self.SCALE+player*self.GAP*self.SCALE)
        y.append(self.OFFSET[1])
    
    
    #Draw player background
    padding_topbottom = 2.5*self.SCALE
    padding_sides = 0.3*self.SCALE
    for n in range(self.NRPLAYERS):
        pygame.draw.rect(self.background, (50,50,50), [x[n]+1-padding_sides,y[n]-padding_topbottom,self.MAXX*self.SCALE+2*padding_sides,self.MAXY*self.SCALE+2*padding_topbottom])
    '''
    
    #Draw transparent player background
    padding_topbottom = 2.5*self.SCALE
    padding_sides = 0.3*self.SCALE
    for n in range(self.NRPLAYERS):
        s = pygame.Surface((self.MAXX*self.SCALE+2*padding_sides,self.MAXY*self.SCALE+2*padding_topbottom))  # the size of your rect
        s.set_alpha(200)                # alpha level
        s.fill((50,50,50))           # this fills the entire surface
        self.background.blit(s, ( (x[n]+1-padding_sides,y[n]-padding_topbottom)))    # (0,0) are the top-left coordinates
    '''
    
        
    #Draw board background
    for n in range(self.NRPLAYERS):
        pygame.draw.rect(self.background, (0,0,0), [x[n],y[n],self.MAXX*self.SCALE,self.MAXY*self.SCALE])
    
    #Draw Score text
    for n in range(self.NRPLAYERS):
        score_player = "score_player" + str(n)
        if score_player in game_board:
            score = game_board[score_player]
            score_string = "Score %d" % score
            text = self.font.render(score_string, True, (120,120,120))
            textpos = (x[0] + self.SCALE*0 + board_dist*n,y[0]+(self.MAXY+0.0)*self.SCALE)
            self.background.blit(text, textpos)
    '''
    #Draw Lines text
    for n in range(self.NRPLAYERS):
        lines_player = "lines_player" + str(n)
        if lines_player in game_board:
            lines = game_board[lines_player]
            lines_string = "Lines %d" % lines
            text = self.font.render(lines_string, True, (120,120,120))
            #textpos = (x[0] + self.SCALE*0 + board_dist*n,y[0]+self.SCALE*1+(self.MAXY+0.0)*self.SCALE)
            textpos = (x[0] + self.SCALE*0 + board_dist*n,y[0]+self.SCALE*1+(self.MAXY+0.0)*self.SCALE)
            self.background.blit(text, textpos)
    '''
    
    #Draw grid
    
    grid_color = (20,20,20)
    for player in range(self.NRPLAYERS):
        for line in range(self.MAXX):
            pygame.draw.line(self.background, grid_color, (x[0]+player*board_dist+line*self.SCALE,y[0]), (x[0]+player*board_dist+line*self.SCALE,y[0]+self.MAXY*self.SCALE-1),1)
        for line in range(self.MAXY):
            pygame.draw.line(self.background, grid_color, (x[0]+player*board_dist,y[0]+line*self.SCALE), (x[0]+self.MAXX*self.SCALE+player*board_dist-1,y[0]+line*self.SCALE),1)

    #Draw landed blocks
    for n in range(self.NRPLAYERS):
        board_landed_player = "board_landed_player" + str(n)
        for (xx,yy) in game_board[board_landed_player]:
            pygame.draw.rect(self.background, self.color_deref(game_board[board_landed_player][(xx,yy)]), (self.OFFSET[0] + xx*self.SCALE+n*self.MAXX*self.SCALE+n*self.GAP*self.SCALE, self.OFFSET[1] + yy*self.SCALE, self.SCALE-1, self.SCALE-1))
    
    #Draw faling blocks
    for n in range(self.NRPLAYERS):
        board_block_player = "blocks_player" + str(n)
        if board_block_player in game_board:
            for block in game_board[board_block_player]:
                if block.y >= 0: #This sees to not draw above the top border
                    pygame.draw.rect(self.background, self.color_deref(block.color), (self.OFFSET[0] + block.x*self.SCALE+n*self.MAXX*self.SCALE+n*self.GAP*self.SCALE, self.OFFSET[1] + block.y*self.SCALE, self.SCALE-1, self.SCALE-1))
    
    #Draw next block and text
    for n in range(self.NRPLAYERS):
        text = self.font.render("Next:", 1, (120,120,120))
        textpos = (x[0] + self.SCALE*0 + board_dist*n,y[0]-self.SCALE*2.5)
        self.background.blit(text, textpos)
        #Draw Next text
        board_nextshape_player = "nextshape_player" + str(n)
        if board_nextshape_player in game_board:
            for block in game_board[board_nextshape_player]:
                pygame.draw.rect(self.background, self.color_deref(block.color), (self.OFFSET[0] + block.x*self.SCALE+n*self.MAXX*self.SCALE+n*self.GAP*self.SCALE, self.OFFSET[1] + (block.y-2.25)*self.SCALE, self.SCALE-1, self.SCALE-1))
                    #nextshape = p.nextshape.blocks
                    #for ns in nextshape:
                    #    d[(ns.x+(offset*n),ns.y-2.3)] = ns.color
         
                
    #self.screen.blit(self.background, (0,0))
    #pygame.display.flip()
    
