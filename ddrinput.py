# ddrinput.py
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

import pygame
import time

#Joypad left hand
JOY_EVENT = 7
JOY_EVENT_2 = 10
KEY_EVENT = 2
KEY_RELEASE = 3
X = 0
Y = 1


#Keys player 0
KEY_LEFT = 276
KEY_UP = 273
KEY_DOWN = 274
KEY_RIGHT = 275
KEY_SPACE = 32

#Keys player 1
KEY_A = 97 #a left
KEY_D = 100 #d right
KEY_W = 119 #w up
KEY_S = 115 #s down
KEY_X = 120 #x drop

#Keys player 2
KEY_F = 102 #left
KEY_H = 104 #right
KEY_T = 116 #up
KEY_G = 103 #down
KEY_B = 98 #drop

#Keys player 3
KEY_J = 106 #left
KEY_L = 108 #right
KEY_I = 105 #up
KEY_K = 107 #down
KEY_COMMA = 44 #drop

#Keys general
KEY_ESC = 27

(LEFT, RIGHT, UP, DOWN, DROP, DIE, RELEASE) = range(7) 
DIRECTIONS = {0:'LEFT', 1:'RIGHT',  2:'UP', 3:'DOWN', 5:'DROP', 6:'DIE'}
class DdrInput(object):
  """
  DdrInput is a class to get input from the particular DDR pads and adapters we have.  It is not
  general or cross platform.  It uses pygame.  For something more general, use pad.py in the pydance
  library.  The pydance library doesn't work with our adapter, so we had to write our own code.  A
  few lines of code here are borrowed from the pydance library.


  DEBUG MODE:
    Use the arrow keys.  Hold down a modifier (alt, control, etc.) to get player 2
  """
  def __init__(self, debug_mode=True):
    """
    Debug mode prints inputs from the ddr pads and also enables the keyboard as an input
    """
    pygame.init() #safe to call multiple times
    self.init_joysticks()
    #This is just so that we can get key presses in the demo.  remove when we plug it into a ui
    screen = pygame.display.set_mode((640, 480))
    self.debug_mode = debug_mode
    self.active_inputs = {}

  def init_joysticks(self):
    pygame.joystick.init()
    try: totaljoy = pygame.joystick.get_count()
    except: totaljoy = 0
    print totaljoy, 'joysticks loaded'
    for i in range(totaljoy):
      m = pygame.joystick.Joystick(i)
      m.init()

  def reset(self):
    pygame.event.clear()
    
  def poll(self):
    """
    Returns a tuple of player index (0 or 1) and move, 
    LEFT, RIGHT, UP, DOWN.  Returns None if there is no new input.  Only returns 1 input at a time.
    """
    event = pygame.event.poll()
    if event.type != 0:
        #pass 
        print event
        
    player_move = None
    if event.type == JOY_EVENT_2:
      player_index, player_move = self.handle_joy_event(event)
    elif event.type == JOY_EVENT:
      player_index, player_move = self.handle_joy_event(event)
      if self.debug_mode:
        print (player_index, player_move)
    #debug mode
    if self.debug_mode:
      if event.type == KEY_EVENT or event.type == KEY_RELEASE:
        (player_index, player_move) = self.handle_key_event(event) 
    #end debug mode
    
    if player_move != None:
      if player_move == RELEASE:
        self.active_inputs[player_index] = None
        return None
      else:
        print 'setting active input'
        self.active_inputs[player_index] = (.5, time.time(), player_move)
      return (player_index, player_move)
    else:
      #~ for player_index in self.active_inputs:  pass
        #~ if self.active_inputs[player_index] != None:
          #~ (fallback_start, start_time, move) = self.active_inputs[player_index]
          #~ if time.time() - start_time > fallback_start:
            #~ fallback_start /= 2
            #~ fallback_start = max(.1, fallback_start)
            #~ start_time = time.time()
            #~ self.active_inputs[player_index] = (fallback_start, start_time, move)
            #~ return (player_index, move)
      return None
  
  def handle_joy_event(self, event):
      player_index = event.joy
      #there may be a tricky quick way to code this, but this is more readable
      #value == 0 -> released
      player_move = None
      #if event.type == JOY_EVENT_2+1:
      #  player_move = RELEASE
      #  return (player_index, player_move)
      
      try:
        if event.button == 2:
          player_move = DROP
      except:
          print "Button"
      
      try:    
        if event.axis == X:
          if event.value < 0:
            player_move = LEFT
          elif event.value > 0:
            player_move = RIGHT
        else:
          if event.value > 0:
            player_move = DOWN
          elif event.value < 0:
            player_move = UP
        if event.value == 0:
          player_move = RELEASE
      except:
        print "Axis"
        
      return player_index, player_move

  def handle_key_event(self, event):
    if event.key == KEY_LEFT:
        player_index = 0
        player_move = LEFT
    elif event.key == KEY_A:
        player_index = 1
        player_move = LEFT
    elif event.key == KEY_F:
        player_index = 2
        player_move = LEFT
    elif event.key == KEY_J:
        player_index = 3
        player_move = LEFT
    
    
    elif event.key == KEY_RIGHT:
        player_index = 0
        player_move = RIGHT
    elif event.key == KEY_D:
        player_index = 1
        player_move = RIGHT
    elif event.key == KEY_H:
        player_index = 2
        player_move = RIGHT
    elif event.key == KEY_L:
        player_index = 3
        player_move = RIGHT
    
    
    elif event.key == KEY_UP:
        player_index = 0
        player_move = UP
    elif event.key == KEY_W:
        player_index = 1
        player_move = UP
    elif event.key == KEY_T:
        player_index = 2
        player_move = UP
    elif event.key == KEY_I:
        player_index = 3
        player_move = UP
      
    
    elif event.key == KEY_DOWN:
        player_index = 0
        player_move = DOWN
    elif event.key == KEY_S:
        player_index = 1
        player_move = DOWN
    elif event.key == KEY_G:
        player_index = 2
        player_move = DOWN
    elif event.key == KEY_K:
        player_index = 3
        player_move = DOWN

    elif event.key == KEY_SPACE:
        player_index = 0
        player_move = DROP
    elif event.key == KEY_X:
        player_index = 1
        player_move = DROP
    elif event.key == KEY_B:
        player_index = 2
        player_move = DROP
    elif event.key == KEY_COMMA:
        player_index = 3
        player_move = DROP
   
    elif event.key == KEY_ESC:
        player_index = 1000
        player_move = DIE
    else:
        player_index = None
        player_move = None
    
    
    if event.type == KEY_RELEASE:
      player_move = RELEASE
    print player_move
    return (player_index, player_move)
