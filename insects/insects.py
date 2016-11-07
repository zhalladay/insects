##  \file insects.py
#   \author Zach Halladay
#
#   This program provides a quick way to run either ants.py or bees.py and is
#   meant to be run as is.
#
#       This program is free software.

import ants, bees, sys, argparse
from menu import *

def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='Simulate an ant or bee.')
    parser.add_argument('-s','--scale', dest='scale', default=2, type=int,
                                        help='scale (default: 2)')
    args = parser.parse_args()
    
    #initialize pygame
    pygame.init()
   
    #set the display screen
    scale = args.scale
    screen_width=1280*scale
    screen_height=800*scale
    screen=pygame.display.set_mode((screen_width,screen_height), pygame.RESIZABLE)

    # for screen prompts
    screen_prompt_xpos = scale * 500
    screen_prompt_ypos = scale * 200
        
    #set the font
    fontsize = 48*scale
    font = pygame.font.Font(None, fontsize)
    
    #block mouse motion to save resources
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    
    screen.fill((0,0,0))
    menu = cMenu(100, 100, 20, 5, 'vertical', 100, screen,
       [('Ants', 1, None),
        ('Bees',  2, None)])

    menu.set_font(pygame.font.Font(None, fontsize))

    # Center the menu on the draw_surface (the entire screen here)
    menu.set_center(True, True)

    # Center the menu on the draw_surface (the entire screen here)
    menu.set_alignment('center', 'center')

    # Create the state variables
    state = 0
    prev_state = 1

    # rect_list is the list of pygame.Rect's that will tell pygame where to
    # update the screen (there is no point in updating the entire screen if only
    # a small portion of it changed!)
    rect_list = []

    while 1:
      # Check if the state has changed, if it has, then post a user event to
      # the queue to force the menu to be shown at least once
      if prev_state != state:
         pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key = 0))
         prev_state = state

      # Get the next event
      e = pygame.event.wait()

      # Update the menu, based on which "state" we are in
      if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
         if state == 0:
            rect_list, state = menu.update(e, state)
         elif state == 1:
            ant = ants.Ants(screen, scale)
            state = 0
            break
         elif state == 2:
            bee = bees.Bees(screen, scale)
            state = 0
            break
         else:
            print ('Exit!')
            pygame.quit()
            sys.exit()

      # Quit if the user presses the exit button
      if e.type == pygame.QUIT:
         pygame.quit()
         sys.exit()

      # Update the screen
      pygame.display.update(rect_list)


##Run
if __name__ == "__main__":
   main()
