##  \file bees.py
#   \author Zach Halladay
#
#   This is a variance of the problem described in chapter 18 of
#   Tracking the Automatic Ant, by David Gale, replacing the square tiles
#   with triangular tiles. This class is written in Pygame/Python,
#   and is written in a so that to run it you just need
#   to create an object of the Bees class.
#
#       This program is free software.


import pygame, math, sys, eztext, sets
from menu import *


class Bees:
    def __init__(self, screen, scale):
        self.screen = screen
        #initialize pygame
        pygame.init()

        #time starts at 0
        self.time = 0

        self.scale = scale # kludge, so that SetAppearance knows this is the initial call
        self.SetAppearance(screen, scale)
        
        #block mouse motion to save resources
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        #set up black and white
        self.Set_Colors(1)

        #create a surface to represent our board
        self.board = pygame.Surface((1400 * self.scale, 800 * self.scale))

        #create reference coordinates for the starting tile
        self.center = ((int((self.width_ref/2))), (int((self.height_ref/2)-1)))

        #create a variable to keep up with where the bee is
        self.bee = None

        #create a variable to tell you if the bee is reversed or not
        self.reverse = False

        #a dictionary to hold information about all the tiles
        self.tiles = {}
        #and a second one to use for gathering information about the board without manipulating the board
        self.false_tiles = {}
        self.false_bee = None

        #show the control screen
        self.Control_Screen()

        #let the user set the rules
        self.Set_Rule_Input()
        
        #create Truchet Tiles and record if each tile is a right facing or left facing triangle
        self.width_adj = max(0, 2-self.scale) # width_ref one too small when scale = 1
        for x in range(self.width_ref + self.width_adj):
            self.height_adj = max(0, 2-self.scale) # height_ref one too small when scale = 1
            for y in range(self.height_ref + self.height_adj):
                coord = (x, y)
                if x%2 == y%2:
                    self.tiles[coord] = ["Right"]                       
                if x%2 != y%2:
                    self.tiles[coord] = ["Left"]

        #add other information about each tile
        for key in self.tiles:
            #each tile starts out as a Left tile
            self.tiles[key].append("L")
            #each tile has been stepped on 0 times
            self.tiles[key].append(0)
            #color starts out white
            self.tiles[key].append(self.white)
            #each tile is cold
            self.tiles[key].append(False)
            #no tile has an bee in it
            self.tiles[key].append((False, None))
            #"reverse steps" or "antisteps"
            self.tiles[key].append(0)
            #arc_colors
            self.tiles[key].append((self.black,self.black,self.black))
            #fill out the board
            self.Make_Triangle_Tile(key)

            #self.tiles[][0] holds either 'Left' or 'Right' representing left or right facing triangles
            #self.tiles[][1] holds either 'L' or 'R' representing Left and Right turns
            #self.tiles[][2] holds an integer representing the number of times a tile has been stepped on
            #self.tiles[][3] holds an RGB value representing the color of the tile
            #self.tiles[][4] holds a boolean value representing if the tile is hot
            #self.tiles[][5] holds a tuple with a boolean and an integer between 1 and 4
            #the boolean represents if there's an bee in that tile and the integer represents the location of the bee

        self.symmetry = True
        
        #create with a new bee in the center
        self.Make_Bee_Center()

        #update the board to the screen
        self.Update()

        #run the program
        self.Run()

    # Set member attributes that control appearance
    def SetAppearance(self, screen, scale):

        ##!! doesn't work!! rescale the display passed in from insects
        if self.scale != scale:
            width = screen.get_width()
            height = screen.get_height()
            pygame.display.quit()
            pygame.display.init()
            self.screen=pygame.display.set_mode((width*scale/self.scale,
                                            height*scale/self.scale),
                                           pygame.RESIZABLE)

            #update the board to the screen
            self.Update()

            self.scale = scale
            
        #set the display screen
        self.screen_width=self.screen.get_width()
        self.width_ref = int(self.screen_width / 35) + 1
        self.screen_height=self.screen.get_height()
        self.height_ref = int(self.screen_height / 20) + min(2, scale)

        self.font = pygame.font.Font(None, 20)
        self.L = self.font.render('L', 1, (0,0,0))
        self.R = self.font.render('R', 1, (0,0,0))

        # for screen prompts
        self.screen_prompt_xpos = self.scale * 500
        self.screen_prompt_ypos = self.scale * 200
        
        #set the font
        self.fontsize = 48*self.scale
        self.font = pygame.font.Font(None, self.fontsize)

    #Clear puts the board back into its starting state
    def Clear(self):
        #time starts at 0
        self.time = 0

        #create a surface to represent our board
        self.board = pygame.Surface((1400 * self.scale, 800 * self.scale))

        #create a variable to keep up with where the bee is
        self.bee = None

        #create a variable to tell you if the bee is reversed or not
        self.reverse = False

        #a dictionary to hold information about all the tiles
        self.tiles = {}
        #and a second one to use for gathering information about the board without manipulating the board
        self.false_tiles = {}
        self.false_bee = None
        
        #create Truchet Tiles and record if each tile is a right facing or left facing triangle
        self.width_adj = max(0, 2-self.scale) # width_ref one too small when scale = 1
        for x in range(self.width_ref + self.width_adj):
            self.height_adj = max(0, 2-self.scale) # height_ref one too small when scale = 1
            for y in range(self.height_ref + self.height_adj):
                coord = (x, y)
                if x%2 == y%2:
                    self.tiles[coord] = ["Right"]                       
                if x%2 != y%2:
                    self.tiles[coord] = ["Left"]

        #add other information about each tile
        for key in self.tiles:
            #each tile starts out as a Left tile
            self.tiles[key].append("L")
            #each tile has been stepped on 0 times
            self.tiles[key].append(0)
            #color starts out white
            self.tiles[key].append(self.white)
            #each tile is cold
            self.tiles[key].append(False)
            #no tile has an bee in it
            self.tiles[key].append((False, None))
            #"reverse steps" or "antisteps"
            self.tiles[key].append(0)
            #arc_colors
            self.tiles[key].append((self.black,self.black,self.black))
            #fill out the board
            self.Make_Triangle_Tile(key)

            #self.tiles[][0] holds either 'Left' or 'Right' representing left or right facing triangles
            #self.tiles[][1] holds either 'L' or 'R' representing Left and Right turns
            #self.tiles[][2] holds an integer representing the number of times a tile has been stepped on
            #self.tiles[][3] holds an RGB value representing the color of the tile
            #self.tiles[][4] holds a boolean value representing if the tile is hot
            #self.tiles[][5] holds a tuple with a boolean and an integer between 1 and 4
            #the boolean represents if there's an bee in that tile and the integer represents the location of the bee

        self.symmetry = True
        
        #create with a new bee in the center
        self.Make_Bee_Center()

        #update the board to the screen
        self.Update()

    #Update updates self.board then blits it to the screen
    def Update(self):
        self.Arc_Color_Origin()
        for key in self.tiles:
            if (key[0] >= 0 and key[0] <= self.width_ref - 1) and (key[1] >= 0 and key[1] <= self.height_ref - 1):
                self.Make_Triangle_Tile(key)
            else:
                self.Color(key)
                self.Is_Hot(key)
                self.Rule(key)
        if (self.bee[0][0] >= 0 and self.bee[0][0] <= self.width_ref - 1) and (self.bee[0][1] >= 0 and self.bee[0][1] <= self.height_ref - 1):
            self.Draw_Bee()
        #self.Bee_Path()
        self.screen.blit(self.board, (0,0))
        pygame.display.flip()

    #For my Menu function I used the Simple_Example file that came with the menu.py as a template for my menu and modified it as needed
    def Main_Menu(self):
        self.screen.fill(self.black)
        menu = cMenu(50, 50, 20, 5, 'vertical', 100, self.screen,
           [('New Bee', 1, None),
            ('Set Rule',  2, None),
            ('Set Time',    3, None),
            ('Reverse',       4, None),
            ('Scale', 8, None), ##!! doesn't work!!
            ('Controls', 5, None),
            ('Back', 6, None),
            ('Exit', 7, None)])

        menu.set_font(pygame.font.Font(None, self.fontsize))

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
                print('New Bee')
                self.Clear()
                state = 0
                break
             elif state == 2:
                print('Rule =')
                self.Set_Rule_Input()
                state = 0
                break
             elif state == 3:
                print('Time =')
                self.Set_Time_Input()
                state = 0
                break
             elif state == 4:
                print('Reverse')
                self.Reverse_Bee()
                break
             elif state == 8: ##!! doesn't work!!
                print('Scale =')
                self.SetAppearance_Input()
                break
             elif state == 5:
                self.Control_Screen()
                break
             elif state == 6:
                break
             else:
                print('Exit!')
                pygame.quit()
                sys.exit()

          # Quit if the user presses the exit button
          if e.type == pygame.QUIT:
             pygame.quit()
             sys.exit()

          # Update the screen
          pygame.display.update(rect_list)
          
    #Control_Screen shows the user what commands do what
    def Control_Screen(self):
        self.screen.fill(self.black)
        self.font = pygame.font.Font(None, self.fontsize)
        line1 = self.font.render('Space - Step', 1, self.white)
        line2 = self.font.render('t - Set Time', 1, self.white)
        line3 = self.font.render('r - Reverse', 1, self.white)
        line4 = self.font.render('Shift - Toggle automatic step', 1, self.white)
        line5 = self.font.render('n - Steps till returning to origin', 1, self.white)
        line6 = self.font.render('m - Skips till returning to origin', 1, self.white)
        line7 = self.font.render('c - Controls', 1, self.white)
        line8 = self.font.render('esc - Menu', 1, self.white)
        line9 = self.font.render('enter - Next', 1, self.white)
        xpos = self.screen_prompt_xpos
        ypos = self.screen_prompt_ypos
        self.screen.blit(line1, (xpos,ypos))
        self.screen.blit(line2, (xpos,ypos+self.fontsize))
        self.screen.blit(line3, (xpos,ypos+2*self.fontsize))
        self.screen.blit(line4, (xpos,ypos+3*self.fontsize))
        self.screen.blit(line5, (xpos,ypos+4*self.fontsize))
        self.screen.blit(line6, (xpos,ypos+5*self.fontsize))
        self.screen.blit(line7, (xpos,ypos+6*self.fontsize))
        self.screen.blit(line8, (xpos,ypos+7*self.fontsize))
        self.screen.blit(line9, (xpos,ypos+8*self.fontsize))
        pygame.display.flip()
        while 1:
            e = pygame.event.wait()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    break
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    ##!! doesn't work!! SetAppearance_Input lets the user rescale the lattice surface
    def SetAppearance_Input(self):
        self.screen.fill(self.black)
        textbox = eztext.Input(maxlength=45, color=(self.white), prompt='Scale: ')
        textbox.font = pygame.font.Font(None, self.fontsize)
        textbox.set_pos(self.screen_prompt_xpos, self.screen_prompt_ypos*1.5)
        # create the pygame clock
        clock = pygame.time.Clock()

        while 1:
            # make sure the program is running at 30 fps
            clock.tick(30)

            # events for textbox
            events = pygame.event.get()
            # process other events
            for event in events:
                # close if x button is pressed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print(int(textbox.value))
                        self.SetAppearance(self.screen, int(textbox.value))
                        if len(self.tiles) > 0:
                            self.Update()
                        return
            # clear the screen
            self.screen.fill(self.black)
            # update textbox
            textbox.update(events)
            # blit textbox on the sceen
            textbox.draw(self.screen)
            # refresh the display
            pygame.display.flip()

            
    #Set_Rule_Input lets the user set the rule string
    def Set_Rule_Input(self):
        self.screen.fill(self.black)
        textbox = eztext.Input(maxlength=45, color=(self.white), prompt='Bee Number: ')
        textbox.font = pygame.font.Font(None, self.fontsize)
        textbox.set_pos(self.screen_prompt_xpos, self.screen_prompt_ypos*1.5)
        # create the pygame clock
        clock = pygame.time.Clock()

        while 1:
            # make sure the program is running at 30 fps
            clock.tick(30)

            # events for textbox
            events = pygame.event.get()
            # process other events
            for event in events:
                # close if x button is pressed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print(int(textbox.value))
                        self.Rule_String(int(textbox.value))
                        if len(self.tiles) > 0:
                            self.Update()
                        return
            # clear the screen
            self.screen.fill(self.black)
            # update textbox
            textbox.update(events)
            # blit textbox on the sceen
            textbox.draw(self.screen)
            # refresh the display
            pygame.display.flip()
            

    #Set_Time_Input lets the user set the time
    def Set_Time_Input(self):
        self.screen.fill(self.black)
        textbox = eztext.Input(maxlength=45, color=(self.white), prompt='Time: ')
        textbox.font = pygame.font.Font(None, self.fontsize)
        textbox.set_pos(self.screen_prompt_xpos, self.screen_prompt_ypos*1.5)
        # create the pygame clock
        clock = pygame.time.Clock()

        while 1:
            # make sure the program is running at 30 fps
            clock.tick(30)

            # events for textbox
            events = pygame.event.get()
            # process other events
            for event in events:
                # close if x button is pressed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print(int(textbox.value))
                        self.Set_Time(int(textbox.value))
                        if len(self.tiles) > 0:
                            self.Update()
                        return
            # clear the screen
            self.screen.fill(self.black)
            # update textbox
            textbox.update(events)
            # blit textbox on the sceen
            textbox.draw(self.screen)
            # refresh the display
            pygame.display.flip()

    #starting at the upper right corner assigns colors to all the arcs
    def Arc_Color_Origin(self):
        self.Arc_Color((0,0), (self.width_ref + self.width_adj, self.height_ref + self.height_adj))
    
    def Arc_Color(self, (x,y), (a,b)):
        for i in range(x,a):
            if self.tiles[(i,y)][0] == "Left":
                self.tiles[(i,y)][7] = (self.blue, self.red, self.green)
            else:
                self.tiles[(i,y)][7] = (self.red, self.blue, self.green)
            for j in range(y+1,b):
                if self.tiles[(i,j)][0] == "Left":
                    if self.tiles[(i,j)][1] == "L":
                        if self.tiles[(i,j-1)][1] == "L":
                            self.tiles[(i,j)][7] = (self.tiles[(i,j-1)][7][2],self.tiles[(i,j-1)][7][1],self.tiles[(i,j-1)][7][0])
                        else:
                            self.tiles[(i,j)][7] = (self.tiles[(i,j-1)][7][2],self.tiles[(i,j-1)][7][0],self.tiles[(i,j-1)][7][1])
                    else:
                        if self.tiles[(i,j-1)][1] == "L":
                            self.tiles[(i,j)][7] = (self.tiles[(i,j-1)][7][2],self.tiles[(i,j-1)][7][0],self.tiles[(i,j-1)][7][1])
                        else:
                            self.tiles[(i,j)][7] = (self.tiles[(i,j-1)][7][2],self.tiles[(i,j-1)][7][1],self.tiles[(i,j-1)][7][0])
                if self.tiles[(i,j)][0] == "Right":
                    if self.tiles[(i,j)][1] == 'L':
                        if self.tiles[(i,j-1)][1] == "L":
                            self.tiles[(i,j)][7] = (self.tiles[(i,j-1)][7][0], self.tiles[(i,j-1)][7][2], self.tiles[(i,j-1)][7][1])
                        else:
                            self.tiles[(i,j)][7] = (self.tiles[(i,j-1)][7][1], self.tiles[(i,j-1)][7][2], self.tiles[(i,j-1)][7][0])
                    else:
                        if self.tiles[(i,j-1)][1] == "L":
                            self.tiles[(i,j)][7] = (self.tiles[(i,j-1)][7][1], self.tiles[(i,j-1)][7][2], self.tiles[(i,j-1)][7][0])
                        else:
                            self.tiles[(i,j)][7] = (self.tiles[(i,j-1)][7][0], self.tiles[(i,j-1)][7][2], self.tiles[(i,j-1)][7][1])

    #Left_Triangle_Tile creates a left facing triangle tile
    def Left_Triangle_Tile(self, color, coord, turn, key):
        #find the points list of the triangle
        points = [(coord[0] + 35, coord[1]), (coord[0], coord[1] +20), (coord[0] + 35, coord[1] + 40)]
        #fill the background the color of the tile
        pygame.draw.polygon(self.board, color, points, 0)
        #give the tile a black outline
        pygame.draw.polygon(self.board, self.black, points, 1)
        #mark if the tile is a left turning or right turning tile
        if turn == 'L':
            pygame.draw.arc(self.board, self.tiles[key][7][0], pygame.Rect((points[2][0]-11, points[2][1]-11), (22,22)), math.pi/2, 5*math.pi/6, 2)
            pygame.draw.arc(self.board, self.tiles[key][7][1], pygame.Rect((points[1][0]-11, points[1][1]-11), (22,22)), -math.pi/6, math.pi/6, 2)
            pygame.draw.arc(self.board, self.tiles[key][7][2], pygame.Rect((points[0][0]-11, points[0][1]-11), (22,22)), 7*math.pi/6, 3*math.pi/2, 2)
        elif turn == 'R':
            pygame.draw.arc(self.board, self.tiles[key][7][0], pygame.Rect((points[2][0]-30, points[2][1]-30), (60,60)), math.pi/2, 5*math.pi/6, 2)
            pygame.draw.arc(self.board, self.tiles[key][7][1], pygame.Rect((points[1][0]-30, points[1][1]-30), (60,60)), -math.pi/6, math.pi/6, 2)
            pygame.draw.arc(self.board, self.tiles[key][7][2], pygame.Rect((points[0][0]-30, points[0][1]-30), (60,60)), 7*math.pi/6, 3*math.pi/2, 2)

    #Right_Triangle_Tile creates a right facing triangle tile
    def Right_Triangle_Tile(self, color, coord, turn, key):
        #find the points list of the triangle
        points = [(coord), (coord[0], coord[1] + 40), (coord[0]+35, coord[1]+20)]
        #fille the background the color of the tile
        pygame.draw.polygon(self.board, color, points, 0)
        #give the tile a black outline
        pygame.draw.polygon(self.board, self.black, points, 1)
        #mark if the tile is a left turning or right turning tile
        if turn == 'L':
            pygame.draw.arc(self.board, self.tiles[key][7][0], pygame.Rect((points[2][0]-11, points[2][1]-11), (22,22)), 5*math.pi/6, 7*math.pi/6, 2)
            pygame.draw.arc(self.board, self.tiles[key][7][1], pygame.Rect((points[1][0]-11, points[1][1]-11), (22,22)), math.pi/6, math.pi/2, 2)
            pygame.draw.arc(self.board, self.tiles[key][7][2], pygame.Rect((points[0][0]-11, points[0][1]-11), (22,22)), 3*math.pi/2, 11*math.pi/6, 2)
        elif turn == 'R':
            pygame.draw.arc(self.board, self.tiles[key][7][0], pygame.Rect((points[2][0]-30, points[2][1]-30), (60,60)), 5*math.pi/6, 7*math.pi/6, 2)
            pygame.draw.arc(self.board, self.tiles[key][7][1], pygame.Rect((points[1][0]-30, points[1][1]-30), (60,60)), math.pi/6, math.pi/2, 2)
            pygame.draw.arc(self.board, self.tiles[key][7][2], pygame.Rect((points[0][0]-30, points[0][1]-30), (60,60)), 3*math.pi/2, 11*math.pi/6, 2)
            
    #Make_Triangle_Tile makes a triangle tile at the given coordinates
    def Make_Triangle_Tile(self,(x,y)):
        #loc is the coordinates of the tile on the board given the dictionary coordinates of the tile
        loc = (- 35 + 35*x, -40 + 20*y)
        #sets the color of the tile
        self.Color((x,y))
        color = self.tiles[(x,y)][3]
        #checks if the tiles is hot
        self.Is_Hot((x,y))
        #updates the rule for the tile
        self.Rule((x,y))
        #checks if the tile is a right facing tile
        if self.tiles[(x,y)][0] == 'Right':
                self.Right_Triangle_Tile(color, loc, str(self.tiles[(x,y)][1]), (x,y))
        #if it's not then it's a left facing tile tile
        if self.tiles[(x,y)][0] == 'Left':
                self.Left_Triangle_Tile(color, loc, str(self.tiles[(x,y)][1]), (x,y))
        
    #Draw_Bee_1 draws a bee at position 1 on the tile given
    def Draw_Bee_1(self, (col, row)):
        #get the coordinates on the screen for where the bee should be
        x = +35 -35 + 35 * col
        y = +30 -40 + 20 * row
        #draw the bee
        pygame.draw.polygon(self.board, (255,0,0), ((x,y+5), (x-10,y), (x,y-5)),)
        #store the bee's location
        self.bee = ((col, row), 1)

    #Draw_Bee_2 draws a bee at position 2 on the tile given        
    def Draw_Bee_2(self, (col,row)):
        #get the coordinates on the screen for where the bee should be
        x = 24 -35 + 35 * col
        y =  17 -40 + 20 * row
        #draw the bee
        pygame.draw.polygon(self.board, (255,0,0), ((x-2,y+5), (x+5,y+2), (x-4,y-4)),)
        #store the bee's location
        self.bee = ((col, row), 2)

    #Draw_Bee_3 draws a bee at position 3 on the tile given
    def Draw_Bee_3(self, (col,row)):
        #get the coordinates on the screen for where the bee should be
        x = 22 + -35 + 35 * col
        y = 7 + -40 + 20 * row
        #draw the bee
        pygame.draw.polygon(self.board, (255,0,0), ((x-2,y+5), (x+10,y+7), (x + 5,y-4)),)
        #store the bee's location
        self.bee = ((col, row), 3)

    #Draw_Bee_4 draws a bee at position 4 on the tile given
    def Draw_Bee_4(self, (col,row)):
        #get the coordinates on the screen for where the bee should be
        x = 2-35 + 35 * col
        y = -2+ 12 -40 + 20 * row
        #draw the bee
        pygame.draw.polygon(self.board, (255,0,0), ((x+10,y), (x, y+5), (x, y-5)),)
        #store the bee's location
        self.bee = ((col, row), 4)

    #Draw_Bee_5 draws a bee at position 5 on the tile given
    def Draw_Bee_5(self, (col,row)):
        #get the coordinates on the screen for where the bee should be
        x = 8 + -35 + 35 * col
        y = 22 + -40 + 20 * row
        #draw the bee
        pygame.draw.polygon(self.board, (255,0,0), ((x+5,y-5), (x+10,y+5), (x-3,y)),)
        #store the bee's location
        self.bee = ((col, row), 5)

    #Draw_Bee_6 draws a bee at position 6 on the tile given
    def Draw_Bee_6(self, (col,row)):
        #get the coordinate on the screen for where the bee should be
        x = 10 + -35 + 35 * col
        y = 34 + -40 + 20 * row
        #draw the bee
        pygame.draw.polygon(self.board, (255,0,0), ((x-3,y-8), (x-9,y+3), (x+3,y)),)
        #store the bee's location
        self.bee = ((col, row), 6)

    #Draw_Bee draws a bee at the tile stored self.bee and the direction stored in self.bee
    def Draw_Bee(self):
        if self.bee[1] == 1:
            self.Draw_Bee_1(self.bee[0])
        elif self.bee[1] == 2:
            self.Draw_Bee_2(self.bee[0])
        elif self.bee[1] == 3:
            self.Draw_Bee_3(self.bee[0])
        elif self.bee[1] == 4:
            self.Draw_Bee_4(self.bee[0])
        elif self.bee[1] == 5:
            self.Draw_Bee_5(self.bee[0])
        elif self.bee[1] == 6:
            self.Draw_Bee_6(self.bee[0])
            

    #Make_Bee takes in a tile and a direction and creates a bee there
    def Make_Bee(self, (x,y), direct):
        self.bee = ((x,y), direct)
        self.Draw_Bee()
        self.tiles[(x,y)][5] = (True, direct)
        #set the origin to the tile
        self.origin = ((x,y), direct)
        pygame.display.flip()

    #Make_Bee_Center makes a left facing bee at the center
    def Make_Bee_Center(self):
        self.Make_Bee(self.center,1)

    #Make_New_Bee takes away any existing ants and makes a new bee at the given tile
    def Make_New_Bee(self, (x,y), direct):
        #checks to see if there is an existing bee
        if self.bee != None:
            #clears the information holding the bee
            self.tiles[self.bee[0]][5] = (False, None)
            #checks if the bee was inside the screen parameters
            if (self.bee[0][0] >= 0 and self.bee[0][0] <= self.width_ref - 1) and (self.bee[0][1] >= 0 and self.bee[0][1] <= self.height_ref - 1):
                #if the bee is inside the screen it clears the tile it was on
                self.Make_Triangle_Tile(self.bee[0])
        #once the old bee is gone, it makes a new bee
        self.Make_Bee((x,y), direct)

    #Make_New_Center_Bee makes a new bee at the center
    def Make_New_Center_Bee(self):
        self.Make_New_Bee(self.center, 1)

    #Reverse_Bee reverses the bee's direction
    def Reverse_Bee(self,):
        #Check to see if the bee is already reversed
        if self.reverse:
            #if it is reversed it reverses it again
            self.reverse = False
        else:
            self.reverse = True
        if self.bee[1] == 1:
            self.tiles[self.bee[0]][5] = (False, None)
            self.Draw_Bee_4((self.bee[0][0] + 1, self.bee[0][1]))
            self.tiles[self.bee[0]][5] = (True, 4)
        elif self.bee[1] == 2:
            self.tiles[self.bee[0]][5] = (False, None)
            self.Draw_Bee_5((self.bee[0][0], self.bee[0][1] - 1))
            self.tiles[self.bee[0]][5] = (True, 5)
        elif self.bee[1] == 3:
            self.tiles[self.bee[0]][5] = (False, None)
            self.Draw_Bee_6((self.bee[0][0] , self.bee[0][1] - 1))
            self.tiles[self.bee[0]][5] = (True, 6)
        elif self.bee[1] == 4:
            self.tiles[self.bee[0]][5] = (False, None)
            self.Draw_Bee_1((self.bee[0][0] - 1, self.bee[0][1]))
            self.tiles[self.bee[0]][5] = (True, 1)
        elif self.bee[1] == 5:
            self.tiles[self.bee[0]][5] = (False, None)
            self.Draw_Bee_2((self.bee[0][0], self.bee[0][1] + 1))
            self.tiles[self.bee[0]][5] = (True, 2)
        elif self.bee[1] == 6:
            self.tiles[self.bee[0]][5] = (False, None)
            self.Draw_Bee_3((self.bee[0][0], self.bee[0][1] + 1))
            self.tiles[self.bee[0]][5] = (True, 3)
        #reverses the rule
        self.Reverse_Rule()
        for key in self.tiles:
            self.Is_Hot(key)
            #for every tile in the parameters of the screen it refreshes the image of the tile
            if (key[0] >= 0 and key[0] <= self.width_ref - 1) and (key[1] >= 0 and key[1] <= self.height_ref - 1):
                self.Make_Triangle_Tile(key)
        #refreshing the board it redraws the bee before updating the screen
        self.Draw_Bee()
        pygame.display.flip()

    #Move_Bee moves the bee one tile according to the rule and information about the tile
    def Move_Bee(self):
        #see if the bee has been reversed or not
        #if reversed the bee takes an antistep if not the bee takes a step
        if self.reverse:
            self.tiles[self.bee[0]][2] -= 1
            self.tiles[self.bee[0]][6] += 1
        else:
            self.tiles[self.bee[0]][2] += 1
            self.tiles[self.bee[0]][6] -= 1
        #store the location of the bee before the move
        old_loc = self.bee[0]
        #considers the position and direction of the bee and the rule of the tile and determines the new placement of the bee
        if self.bee[1] == 1:
            if self.tiles[self.bee[0]][1] == 'L':
                self.bee = ((self.bee[0][0], self.bee[0][1] + 1), 2)
            elif self.tiles[self.bee[0]][1] == 'R':
                self.bee = ((self.bee[0][0], self.bee[0][1] - 1), 6)
        elif self.bee[1] == 2:
            if self.tiles[self.bee[0]][1] == 'L':
                self.bee = ((self.bee[0][0], self.bee[0][1] + 1), 3)
            elif self.tiles[self.bee[0]][1] == 'R':
                self.bee = ((self.bee[0][0] - 1, self.bee[0][1]), 1)
        elif self.bee[1] == 3:
            if self.tiles[self.bee[0]][1] == 'L':
                self.bee = ((self.bee[0][0]+1, self.bee[0][1]), 4)
            elif self.tiles[self.bee[0]][1] == 'R':
                self.bee = ((self.bee[0][0], self.bee[0][1]+1), 2)
        elif self.bee[1] == 4:
            if self.tiles[self.bee[0]][1] == 'L':
                self.bee = ((self.bee[0][0], self.bee[0][1] - 1), 5)
            elif self.tiles[self.bee[0]][1] == 'R':
                self.bee = ((self.bee[0][0], self.bee[0][1] + 1), 3)
        elif self.bee[1] == 5:
            if self.tiles[self.bee[0]][1] == 'L':
                self.bee = ((self.bee[0][0], self.bee[0][1] - 1), 6)
            elif self.tiles[self.bee[0]][1] == 'R':
                self.bee = ((self.bee[0][0] + 1, self.bee[0][1]), 4)
        elif self.bee[1] == 6:
            if self.tiles[self.bee[0]][1] == 'L':
                self.bee = ((self.bee[0][0] -1, self.bee[0][1]), 1)
            elif self.tiles[self.bee[0]][1] == 'R':
                self.bee = ((self.bee[0][0], self.bee[0][1] - 1), 5)
        #if the bee attempts to move into a tile that doesn't exist
        #create a new tile
        if self.bee[0] not in self.tiles:
            if self.bee[0][0]%2 == self.bee[0][1]%2:
                self.tiles[self.bee[0]] = ["Right"]                       
            if self.bee[0][0]%2 != self.bee[0][1]%2:
                self.tiles[self.bee[0]] = ["Left"]
            self.tiles[self.bee[0]].append(self.rule[0])
            self.tiles[self.bee[0]].append(0)
            self.tiles[self.bee[0]].append(self.white)
            self.tiles[self.bee[0]].append(False)
            self.tiles[self.bee[0]].append((False, None))
            self.tiles[self.bee[0]].append(0)
            self.Is_Hot(self.bee[0])
        #if the old tile is in the screen refresh the tile
        if (old_loc[0] >= 0 and old_loc[0] <= self.width_ref - 1) and (old_loc[1] >= 0 and old_loc[1] <= self.height_ref - 1):
            self.Make_Triangle_Tile(old_loc)
        else:
            self.Color(old_loc)
            self.Is_Hot(old_loc)
            self.Rule(old_loc)
        #if the new tile is in the screen draw the bee
        if (self.bee[0][0] >= 0 and self.bee[0][0] <= self.width_ref - 1) and (self.bee[0][1] >= 0 and self.bee[0][1] <= self.height_ref - 1):
            self.Draw_Bee()
        self.tiles[old_loc][5] = (False, None)
        self.tiles[self.bee[0]][5] = (True, self.bee[1])

    #Move_Bee_Step moves the bee one step
    def Move_Bee_Step(self):
        self.Move_Bee()
        if self.reverse:
            self.time -= 1
        else:
            self.time += 1
        pygame.display.flip()

    #Move_Bee_N moves the bee n steps
    def Move_Bee_N(self, n):
        for x in range(n):
            self.Move_Bee()
        if self.reverse:
            self.time -= n
        else:   
            self.time += n
        pygame.display.flip()

    #Set_Time sets the board to time n
    def Set_Time(self, n):
        #finds the difference between current time and desired time
        if not self.reverse:
            time_diff = n - self.time
        else:
            time_diff = -(n-self.time)
        #moves the bee the nexessary amount of time
        if time_diff > 0:
            self.Move_Bee_N(time_diff)
        if time_diff < 0:
            self.Reverse_Bee()
            self.Move_Bee_N(-(time_diff))
            self.Reverse_Bee()

    #Rule_String takes in an integer and converts it into a string or L's and R's
    def Rule_String(self, num):
        time = self.time
        #converts the number into binary and then into a string of 1's and 0's
        binnum = str(bin(num)[2:])
        #self.rule holds the string of L's and R's
        self.rule = ''
        for letter in str(binnum):
            #for every letter in the string of the binary string
            if letter == '1':
                #if the letter is a 1 then the rule equivalent is an L
                self.rule = self.rule + 'L'
            elif letter == '0':
                #if the letter is a 0 then the rule equivalent is an R
                self.rule = self.rule + 'R'
        #Update the colors
        self.Set_Colors(len(self.rule))
        self.Clear()
        self.Set_Time(time)

    #Reverse_Rule is the inverse of the rule and is the rule for reversed ants
    def Reverse_Rule(self):
        temprule = ''
        for letter in self.rule:
            if letter == 'L':
                #every L becomes an R
                temprule = temprule + 'R'
            if letter == 'R':
                #and every R becomes an L
                temprule = temprule + 'L'
        self.rule = temprule
        for key in self.tiles:
            #update the tiles with the new rule
            self.Rule(key)

    #Rule uses self.rule and a given coordinate to update the rule for a tile
    def Rule(self, coord):
        #the rule for a coordinate equals the equivalency of the number of times the tile has been stepped on mod the length of the rule string
        self.tiles[coord][1] = self.rule[(self.tiles[coord][2] % len(self.rule))]
        if self.reverse:
            #if the bee is a reverse bee
            #then the rule for a tile equals the equivalency of the number of times the tiles has been antistepped on mod the length of the rule string
            self.tiles[coord][1] = self.rule[(-1 * (1 + (self.tiles[coord][6] % len(self.rule))))]

    #Is_Hot checks to see if a tile is hot
    def Is_Hot(self, coord):
        #checks if it's counting steps or antisteps
        if self.reverse:
            count = self.tiles[coord][6]
        else:
            count = self.tiles[coord][2]
        #if the current rule is different from the next rule then it's hot
        if self.rule[(count % len(self.rule))] == self.rule[((count+1) % len(self.rule))]:
            self.tiles[coord][4] = False
        elif self.rule[(count % len(self.rule))] != self.rule[((count+1) % len(self.rule))]:
            self.tiles[coord][4] = True

    #Set_Colors sets the colors for the tiles; num is the length of the rule string
    def Set_Colors(self, num):
        #there will always be black and white
        self.black = (0,0,0)
        self.red = (255,0,0)
        self.green = (0,255,0)
        self.blue = (0,0,255)
        if num >= 1:
            self.white = (255,255,255)
            num -= 1
        #there will be as many grays are necessary to fill out the rest of the tile colors
        if num >= 1:
            self.gray = []
            self.gray.append('')
            num2 = int(255/(num+1))
            for x in range(num):
                num3 = (255-(num2 * (x+1)), 255-(num2 * (x+1)), 255-(num2 * (x+1)))
                self.gray.append(num3)

    #Color sets the color to the tiles
    def Color(self, coord):
        if self.tiles[coord][2] % len(self.rule) == 0:
            self.tiles[coord][3] = self.white
        else:
            self.tiles[coord][3] = self.gray[(self.tiles[coord][2] % len(self.rule))]

    #Single_Visit makes a dictionary of all the tiles that have only been visited once
    def Single_Visit(self):
        self.single = {}
        for key in self.tiles:
            if self.tiles[key][2] == 1:
                self.single[key] = self.tiles[key]

    #False_Move is only used as a helper for other methods to check where the bee is going
    def False_Move(self):
        #store the location of the bee before the move
        old_loc = self.false_bee[0]
        #considers the position and direction of the bee and the rule of the tile and determines the new placement of the bee
        if self.false_bee[1] == 1:
            if self.false_tiles[self.false_bee[0]][1] == 'L':
                self.false_bee = ((self.false_bee[0][0], self.false_bee[0][1] + 1), 2)
            elif self.false_tiles[self.false_bee[0]][1] == 'R':
                self.false_bee = ((self.false_bee[0][0], self.false_bee[0][1] - 1), 6)
        elif self.false_bee[1] == 2:
            if self.false_tiles[self.false_bee[0]][1] == 'L':
                self.false_bee = ((self.false_bee[0][0], self.false_bee[0][1] + 1), 3)
            elif self.false_tiles[self.false_bee[0]][1] == 'R':
                self.false_bee = ((self.false_bee[0][0] - 1, self.false_bee[0][1]), 1)
        elif self.false_bee[1] == 3:
            if self.false_tiles[self.false_bee[0]][1] == 'L':
                self.false_bee = ((self.false_bee[0][0]+1, self.false_bee[0][1]), 4)
            elif self.false_tiles[self.false_bee[0]][1] == 'R':
                self.false_bee = ((self.false_bee[0][0], self.false_bee[0][1]+1), 2)
        elif self.false_bee[1] == 4:
            if self.false_tiles[self.false_bee[0]][1] == 'L':
                self.false_bee = ((self.false_bee[0][0], self.false_bee[0][1] - 1), 5)
            elif self.false_tiles[self.false_bee[0]][1] == 'R':
                self.false_bee = ((self.false_bee[0][0], self.false_bee[0][1] + 1), 3)
        elif self.false_bee[1] == 5:
            if self.false_tiles[self.false_bee[0]][1] == 'L':
                self.false_bee = ((self.false_bee[0][0], self.false_bee[0][1] - 1), 6)
            elif self.false_tiles[self.false_bee[0]][1] == 'R':
                self.false_bee = ((self.false_bee[0][0] + 1, self.false_bee[0][1]), 4)
        elif self.false_bee[1] == 6:
            if self.false_tiles[self.false_bee[0]][1] == 'L':
                self.false_bee = ((self.false_bee[0][0] -1, self.false_bee[0][1]), 1)
            elif self.false_tiles[self.false_bee[0]][1] == 'R':
                self.false_bee = ((self.false_bee[0][0], self.false_bee[0][1] - 1), 5)
        #if the false_bee attempts to move into a tile that doesn't exist
        #create a new tile
        if self.false_bee[0] not in self.false_tiles:
            if self.false_bee[0][0]%2 == self.false_bee[0][1]%2:
                self.false_tiles[self.false_bee[0]] = ["Right"]                       
            if self.false_bee[0][0]%2 != self.false_bee[0][1]%2:
                self.false_tiles[self.false_bee[0]] = ["Left"]
            self.false_tiles[self.false_bee[0]].append(self.rule[0])
            self.false_tiles[self.false_bee[0]].append(0)
            self.false_tiles[self.false_bee[0]].append(self.white)
            self.false_tiles[self.false_bee[0]].append(False)
            self.false_tiles[self.false_bee[0]].append((False, None))
            self.false_tiles[self.false_bee[0]].append(0)
            self.Is_Hot(self.false_bee[0])
        self.false_tiles[old_loc][5] = (False, None)
        self.false_tiles[self.false_bee[0]][5] = (True, self.false_bee[1])

    #Bee_Path is used to mark out the bee's path and see if any hot tiles are visited twice
    def Bee_Path(self):
        self.false_tiles = self.tiles
        self.false_bee = self.bee
        visited_and_changed = sets.Set([])
        while self.symmetry:
            coord = (- 35 + 35*self.false_bee[0][0], -40 + 20*self.false_bee[0][1])
            #if the path hasn't changed
            if(self.false_bee[0] not in visited_and_changed):
                if(self.false_bee[1] %2 == 1):
                    points = [(coord[0] + 35, coord[1]), (coord[0], coord[1] +20), (coord[0] + 35, coord[1] + 40)]
                    if self.false_bee[1] == 1:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[2][0]-11, points[2][1]-11), (22,22)), math.pi/2, 5*math.pi/6, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[0][0]-30, points[0][1]-30), (60,60)), 7*math.pi/6, 3*math.pi/2, 3)
                    elif self.false_bee[1] == 3:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[0][0]-11, points[0][1]-11), (22,22)), 7*math.pi/6, 3*math.pi/2, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[1][0]-30, points[1][1]-30), (60,60)), -math.pi/6, math.pi/6, 3)
                    elif self.false_bee[1] == 5:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[1][0]-11, points[1][1]-11), (22,22)), -math.pi/6, math.pi/6, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[2][0]-30, points[2][1]-30), (60,60)), math.pi/2, 5*math.pi/6, 3)
                elif(self.false_bee[1] %2 == 0):
                    points = [(coord), (coord[0], coord[1] + 40), (coord[0]+35, coord[1]+20)]
                    if self.false_bee[1] == 2:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[2][0]-11, points[2][1]-11), (22,22)), 5*math.pi/6, 7*math.pi/6, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[0][0]-30, points[0][1]-30), (60,60)), 3*math.pi/2, 11*math.pi/6, 3)
                    elif self.false_bee[1] == 4:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[0][0]-11, points[0][1]-11), (22,22)), 3*math.pi/2, 11*math.pi/6, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[1][0]-30, points[1][1]-30), (60,60)), math.pi/6, math.pi/2, 3)
                    elif self.false_bee[1] == 6:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[1][0]-11, points[1][1]-11), (22,22)), math.pi/6, math.pi/2, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (0,200,0), pygame.Rect((points[2][0]-30, points[2][1]-30), (60,60)), 5*math.pi/6, 7*math.pi/6, 3)
            #if the path has changed
            if(self.false_bee[0] in visited_and_changed):
                if(self.false_bee[1] %2 == 1):
                    points = [(coord[0] + 35, coord[1]), (coord[0], coord[1] +20), (coord[0] + 35, coord[1] + 40)]
                    if self.false_bee[1] == 1:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[2][0]-11, points[2][1]-11), (22,22)), math.pi/2, 5*math.pi/6, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[0][0]-30, points[0][1]-30), (60,60)), 7*math.pi/6, 3*math.pi/2, 3)
                    elif self.false_bee[1] == 3:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[0][0]-11, points[0][1]-11), (22,22)), 7*math.pi/6, 3*math.pi/2, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[1][0]-30, points[1][1]-30), (60,60)), -math.pi/6, math.pi/6, 3)
                    elif self.false_bee[1] == 5:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[1][0]-11, points[1][1]-11), (22,22)), -math.pi/6, math.pi/6, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[2][0]-30, points[2][1]-30), (60,60)), math.pi/2, 5*math.pi/6, 3)
                elif(self.false_bee[1] %2 == 0):
                    points = [(coord), (coord[0], coord[1] + 40), (coord[0]+35, coord[1]+20)]
                    if self.false_bee[1] == 2:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[2][0]-11, points[2][1]-11), (22,22)), 5*math.pi/6, 7*math.pi/6, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[0][0]-30, points[0][1]-30), (60,60)), 3*math.pi/2, 11*math.pi/6, 3)
                    elif self.false_bee[1] == 4:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[0][0]-11, points[0][1]-11), (22,22)), 3*math.pi/2, 11*math.pi/6, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[1][0]-30, points[1][1]-30), (60,60)), math.pi/6, math.pi/2, 3)
                    elif self.false_bee[1] == 6:
                        if self.false_tiles[self.false_bee[0]][1] == 'L':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[1][0]-11, points[1][1]-11), (22,22)), math.pi/6, math.pi/2, 3)
                        elif self.false_tiles[self.false_bee[0]][1] == 'R':
                            pygame.draw.arc(self.board, (200,0,0), pygame.Rect((points[2][0]-30, points[2][1]-30), (60,60)), 5*math.pi/6, 7*math.pi/6, 3)
                self.symmetry = False
                self.screen.blit(self.board, (0,0))
                pygame.display.flip()
            #if the tile was hot and changed we want to store it
            if self.false_tiles[self.false_bee[0]][4]:
                visited_and_changed.add(self.false_bee[0])
            self.False_Move()
            if self.false_bee == self.origin:
                self.screen.blit(self.board, (0,0))
                pygame.display.flip()
                break

    #Run_Time_Step runs in steps with a slight time delay in between each step
    def Run_Time_Step(self):
        while 1:
            self.Move_Bee_Step()
            pygame.time.delay(1)
            e = pygame.event.get()
            for event in e:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            press = pygame.key.get_pressed()
            #press r to reverse
            if press[114] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[114] == 0:
                    self.Reverse_Bee()
                    pygame.display.flip()
            #press shift to break
            if press[304] == 1 or press[303] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[304] == 0 or press[303] == 0:
                    x = 1
                    break
            if self.bee == self.origin:
                #self.Bee_Path()
                self.Update()
            self.screen.blit(self.board, (0,0))
            pygame.display.flip()

    #Run_Time_N runs in jumps of n with a slight time delay in between each step
    def Run_Time_N(self, n):
        while 1:
            self.Move_Bee_N(n)
            print('Time = ' + str(self.time))
            pygame.time.delay(1)
            pygame.event.get()
            press2 = pygame.key.get_pressed()
            if press2[114] == 1:
                pygame.event.wait()
                press2 = pygame.key.get_pressed()
                if press2[114] == 0:
                    print('Reverse')
                    self.Reverse_Bee()
                    pygame.display.flip()
            self.screen.blit(self.board, (0,0))
            pygame.display.flip()

    #Run_Click_Step runs with steps with mouse clicks
    def Run_Click_Step(self):
        while 1:
            pygame.event.wait()
            press = pygame.mouse.get_pressed()
            if press[0]:
                pygame.event.wait()
                press = pygame.mouse.get_pressed()
                if press[0] != True:
                    self.Move_Bee_Step()
                    print('Time = ' + str(self.time))
            self.screen.blit(self.board, (0,0))
            pygame.display.flip()

    #Run_Click_N runs with jumps of n with mouse clicks               
    def Run_Click_N(self, n):
        while 1:
            pygame.event.wait()
            press = pygame.mouse.get_pressed()
            if press[0]:
                pygame.event.wait()
                press = pygame.mouse.get_pressed()
                if press[0] != True:
                    self.Move_Bee_N(n)
                    print('Time = ' + str(self.time))
            self.screen.blit(self.board, (0,0))
            pygame.display.flip()

    #Run runs the bees program and simulates the behavior
    def Run(self):
        while True:
            #wait for user command from the user
            e = pygame.event.wait()
            press = pygame.key.get_pressed()
            #space takes a step
            if press[32]:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[32] != True:
                    self.Move_Bee_Step()
                    print('time: ' + str(self.time))
            #esc pulls up the menu
            if press[27]:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[27] != True:
                    self.Main_Menu()
            #r reverses
            if press[114] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[114] == 0:
                    print('Reverse')
                    self.Reverse_Bee()
                    pygame.display.flip()
            #shift toggles run time
            if press[303] == 1 or press[304] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[303] == 0 and press[304] == 0:
                    self.Run_Time_Step()
            #n steps to origin
            if press[110] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[110] == 0:
                    self.Move_Bee_Step()
                    self.screen.blit(self.board, (0,0))
                    pygame.display.flip()
                    print('Time = ' + str(self.time))
                    while self.bee != self.origin:
                        e2 = pygame.event.get()
                        for event in e2:
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        self.Move_Bee_Step()
                        print('Time = ' + str(self.time))
                        self.screen.blit(self.board, (0,0))
                        pygame.display.flip()
            #m skips to origin
            if press[109] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[109] == 0:
                    n = 0
                    self.Move_Bee()
                    n += 1
                    while self.bee != self.origin:
                        self.Move_Bee()
                        n += 1
                    self.time += n
                    pygame.display.flip()
                    print('Time = ' + str(self.time))
            #t sets time
            if press[116] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[116] == 0:
                    self.Set_Time_Input()
            #c bring up the controls
            if press[99] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[99] == 0:
                    self.Control_Screen()
            if self.bee == self.origin:
                self.Update()
            #update the screen
            self.screen.blit(self.board, (0,0))
            pygame.display.flip()

            if e.type == pygame.QUIT:
             pygame.quit()
             sys.exit()
