##  \file ants.py
#   \author Zach Halladay
#
#   This is a simulation of the problem described in chapter 18 of
#   Tracking the Automatic Ant, by David Gale. This class is written in
#   Pygame/Python, and is written in a so that to run it you just need
#   to create an object of the Ants class.
#
#       This program is free software.

import pygame, math, sys, eztext
from menu import *


class Ants:
    def __init__(self, screen):
        #time starts at 0
        self.time = 0
        
        #initialize pygame
        pygame.init()
       
        #set the display screen
        self.scale = 2
        self.screen_width=screen.get_width()
        self.width_ref = int(self.screen_width / 40)
        self.screen_height=screen.get_height()
        self.height_ref = int(self.screen_height / 40)
        self.screen=screen

        #set the font
        self.font = pygame.font.Font(None, 96)
        
        #block mouse motion to save resources
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        #set up black and white
        self.Set_Colors(1)

        #create a surface to represent our board
        self.board = pygame.Surface((self.screen_width, self.screen_height))

        #create reference coordinates for the starting tile
        self.center = ((int((self.width_ref/2) - 1)), (int((self.height_ref/2) - 1)))

        #create a variable to keep up with where the ant is
        self.ant = None

        #create a variable to tell you if the ant is reversed or not
        self.reverse = False

        #a dictionary to hold information about all the tiles
        self.tiles = {}

        #show the control screen
        self.Control_Screen()

        #let the user set the rules
        self.Set_Rule_Input()
        
        #create Truchet Tiles and record if each tile is a Horizontal or a Vertical tile
        for x in range(self.width_ref):
            for y in range(self.height_ref):
                coord = (x, y)
                if x%2 == y%2:
                    self.tiles[coord] = ["H"]                       
                if x%2 != y%2:
                    self.tiles[coord] = ["V"]

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
            #no tile has an ant in it
            self.tiles[key].append((False, None))
            #"reverse steps" or "antisteps"
            self.tiles[key].append(0)
            #fill out the board
            self.Make_Truchet_Tile(key)

            #self.tiles[][0] holds either 'H' or 'V' representing Horizontal and Vertical
            #self.tiles[][1] holds either 'L' or 'R' representing Left and Right
            #self.tiles[][2] holds an integer representing the number of times a tile has been stepped on
            #self.tiles[][3] holds an RGB value representing the color of the tile
            #self.tiles[][4] holds a boolean value representing if the tile is hot
            #self.tiles[][5] holds a tuple with a boolean and an integer between 1 and 4
            #the boolean represents if there's an ant in that tile and the integer represents the location of the ant
            #with 1 meaning a left facing ant, 2 meaning an upward facing ant, 3 meaning a right facing ant, and 4 meaning a downward facing ant
            #self.tiles[][6] holds an integer representing the antisteps(the negative of how many times a tiles been stepped on,
            #or how many times a tile has been stepped on by a reversed ant)

        #create with a new ant in the center
        self.Make_Ant_Center()

        #update the board to the screen
        self.Update()

        #run the program
        self.Run()

    #Clears the board back to its starting state
    def Clear(self):
        #time starts at 0
        self.time = 0

        #create a surface to represent our board
        self.board = pygame.Surface((self.screen_width, self.screen_height))

        #create a variable to keep up with where the ant is
        self.ant = None

        #create a variable to tell you if the ant is reversed or not
        self.reverse = False

        #a dictionary to hold information about all the tiles
        self.tiles = {}
        
        #create Truchet Tiles and record if each tile is a Horizontal or a Vertical tile
        for x in range(self.width_ref):
            for y in range(self.height_ref):
                coord = (x, y)
                if x%2 == y%2:
                    self.tiles[coord] = ["H"]                       
                if x%2 != y%2:
                    self.tiles[coord] = ["V"]

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
            #no tile has an ant in it
            self.tiles[key].append((False, None))
            #"reverse steps" or "antisteps"
            self.tiles[key].append(0)
            #fill out the board
            self.Make_Truchet_Tile(key)

            #self.tiles[][0] holds either 'H' or 'V' representing Horizontal and Vertical
            #self.tiles[][1] holds either 'L' or 'R' representing Left and Right
            #self.tiles[][2] holds an integer representing the number of times a tile has been stepped on
            #self.tiles[][3] holds an RGB value representing the color of the tile
            #self.tiles[][4] holds a boolean value representing if the tile is hot
            #self.tiles[][5] holds a tuple with a boolean and an integer between 1 and 4
            #the boolean represents if there's an ant in that tile and the integer represents the location of the ant
            #with 1 meaning a left facing ant, 2 meaning an upward facing ant, 3 meaning a right facing ant, and 4 meaning a downward facing ant
            #self.tiles[][6] holds an integer representing the antisteps(the negative of how many times a tiles been stepped on,
            #or how many times a tile has been stepped on by a reversed ant)

        #create with a new ant in the center
        self.Make_Ant_Center()

        #update the board to the screen
        self.Update()

    #Update updates self.board then blits it to the screen
    def Update(self):
        for key in self.tiles:
            if (key[0] >= 0 and key[0] <= self.width_ref - 1) and (key[1] >= 0 and key[1] <= self.height_ref - 1):
                self.Make_Truchet_Tile(key)
            else:
                self.Color(key)
                self.Is_Hot(key)
                self.Rule(key)
        if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
            self.Draw_Ant()
        self.screen.blit(self.board, (0,0))
        pygame.display.flip

    #For my Menu function I used the Simple_Example file that came with the menu.py as a template for my menu and modified it as needed
    def Main_Menu(self):
        self.screen.fill(self.black)
        menu = cMenu(100, 100, 20, 5, 'vertical', 100, self.screen,
           [('New Ant', 1, None),
            ('Set Rule',  2, None),
            ('Set Time',    3, None),
            ('Reverse',       4, None),
            ('Controls', 5, None),
            ('Back', 6, None),
            ('Exit', 7, None)])

        menu.set_font(pygame.font.Font(None, 96))

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
                print('New Ant')
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
                self.Reverse_Ant()
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
        line1 = self.font.render('Space - Step', 1, self.white)
        line2 = self.font.render('t - Set Time', 1, self.white)
        line3 = self.font.render('r - Reverse', 1, self.white)
        line4 = self.font.render('Shift - Toggle automatic step', 1, self.white)
        line5 = self.font.render('n - Steps till returning to origin', 1, self.white)
        line6 = self.font.render('m - Skips till returning to origin', 1, self.white)
        line7 = self.font.render('c - Controls', 1, self.white)
        line8 = self.font.render('esc - Menu', 1, self.white)
        line9 = self.font.render('enter - Next', 1, self.white)
        self.screen.blit(line1, (1000,400))
        self.screen.blit(line2, (1000,480))
        self.screen.blit(line3, (1000,560))
        self.screen.blit(line4, (1000,640))
        self.screen.blit(line5, (1000,720))
        self.screen.blit(line6, (1000,800))
        self.screen.blit(line7, (1000,880))
        self.screen.blit(line8, (1000,960))
        self.screen.blit(line9, (1000,1040))
        pygame.display.flip()
        while 1:
            e = pygame.event.wait()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    break
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    #Set_Rule_Input lets the user set the rule string
    def Set_Rule_Input(self):
        self.screen.fill(self.black)
        textbox = eztext.Input(maxlength=45, color=(self.white), prompt='Ant Number: ')
        textbox.font = pygame.font.Font(None, 96)
        textbox.set_pos(1000, 600)
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
        textbox.font = pygame.font.Font(None, 96)
        textbox.set_pos(1000, 600)
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
            

    #Left_Horiztonal_Truchet returns a surface of a left horizontal tile
    def Left_Horizontal_Truchet(self, color, coord):
        self.surface = pygame.Surface((40,40))
        self.surface.fill(color)
        pygame.draw.rect(self.surface, self.black, (0,0,40,40), 1)
        pygame.draw.arc(self.surface, self.black, (20,20,40,40), (math.pi/2), math.pi, 2)
        pygame.draw.arc(self.surface, self.black, (-20,-20,40,40), ((math.pi)*3/2), 2*math.pi, 2)
        pygame.draw.polygon(self.surface, self.black, ((20,40),(15,35),(25,35)),0)
        pygame.draw.polygon(self.surface, self.black, ((20,0),(15,5),(25,5)),0)
        self.Draw_Diagonal2(coord, self.black)
        return self.surface

    #Right_Horiztonal_Truchet returns a surface of a right horizontal tile
    def Right_Horizontal_Truchet(self, color, coord):
        self.surface = pygame.Surface((40,40))
        self.surface.fill(color)
        pygame.draw.rect(self.surface, self.black, (0,0,40,40), 1)
        pygame.draw.arc(self.surface, self.black, (20,-20,40,40), (math.pi), math.pi*3/2, 2)
        pygame.draw.arc(self.surface, self.black, (-20,20,40,40), 0, math.pi/2 , 2)
        pygame.draw.polygon(self.surface, self.black, ((20,40),(15,35),(25,35)),0)
        pygame.draw.polygon(self.surface, self.black, ((20,0),(15,5),(25,5)),0)
        self.Draw_Diagonal1(coord,self.black)
        return self.surface

    #Left_Vertical_Truchet returns a surface of a left vertical tile
    def Left_Vertical_Truchet(self, color, coord):
        self.surface = pygame.Surface((40,40))
        self.surface.fill(color)
        pygame.draw.rect(self.surface, self.black, (0,0,40,40), 1)
        pygame.draw.arc(self.surface, self.black, (20,-20,40,40), (math.pi), math.pi*3/2, 2)
        pygame.draw.arc(self.surface, self.black, (-20,20,40,40), 0, math.pi/2 , 2)
        pygame.draw.polygon(self.surface, self.black, ((0,20),(5,15),(5,25)),0)
        pygame.draw.polygon(self.surface, self.black, ((40,20),(35,15),(35,25)),0)
        self.Draw_Diagonal1(coord, self.black)
        return self.surface

    #Right_Vertical_Truchet returns a surface of a right vertical tile
    def Right_Vertical_Truchet(self, color, coord):
        self.surface = pygame.Surface((40,40))
        self.surface.fill(color)
        pygame.draw.rect(self.surface, self.black, (0,0,40,40), 1)
        pygame.draw.arc(self.surface, self.black, (20,20,40,40), (math.pi/2), math.pi, 2)
        pygame.draw.arc(self.surface, self.black, (-20,-20,40,40), ((math.pi)*3/2), 2*math.pi, 2)
        pygame.draw.polygon(self.surface, self.black, ((0,20),(5,15),(5,25)),0)
        pygame.draw.polygon(self.surface, self.black, ((40,20),(35,15),(35,25)),0)
        self.Draw_Diagonal2(coord,self.black)
        return self.surface

    #Make_Truchet_Tile makes a Truchet Tile at the given coordinates
    def Make_Truchet_Tile(self,(x,y)):
        #loc is the coordinates of the tile on the board given the dictionary coordinates of the tile
        loc = (40*x, 40*y)
        #sets the color of the tile
        self.Color((x,y))
        color = self.tiles[(x,y)][3]
        #checks if the tiles is hot
        self.Is_Hot((x,y))
        #updates the rule for the tile
        self.Rule((x,y))
        #checks if the tile is a horizontal tile
        if self.tiles[(x,y)][0] == 'H':
            #checks if it's a left tile
            if self.tiles[(x,y)][1] == 'L':
                #if it is then it makes a left horizontal tile
                self.board.blit(self.Left_Horizontal_Truchet(color, (x,y)), loc)
            #if not then it's a right tile
            if self.tiles[(x,y)][1] == 'R':
                #if it is then it makes a right horizontal tile
                self.board.blit(self.Right_Horizontal_Truchet(color, (x,y)), loc)
        #if it's not then it's a vertical tile
        if self.tiles[(x,y)][0] == 'V':
            #checks if it's a left tile
            if self.tiles[(x,y)][1] == 'L':
                #if it is it makes a left vertical tile
                self.board.blit(self.Left_Vertical_Truchet(color,(x,y)), loc)
            #if not then it's a right tile
            if self.tiles[(x,y)][1] == 'R':
                #if it is it makes a right vertical tile
                self.board.blit(self.Right_Vertical_Truchet(color, (x,y)), loc)

    #Draw_Left_Ant draws a left facing ant on the tile given
    def Draw_Left_Ant(self, (col, row)):
        #get the coordinates on the screen for where the ant should be
        x = 30 + 40 * col
        y = 20 + 40 * row
        #draw the ant
        pygame.draw.polygon(self.board, (255,0,0), ((x,y), (x+9,y+10), (x+9,y-10)),)
        #store the ant's location
        self.ant = ((col, row), 1)

    #Draw_Right_Ant draws a right facing ant on the tile given        
    def Draw_Right_Ant(self, (col,row)):
        #get the coordinates on the screen for where the ant should be
        x = 10 + 40 * col
        y = 20 + 40 * row
        #draw the ant
        pygame.draw.polygon(self.board, (255,0,0), ((x,y), (x-9,y+10), (x-9,y-10)),)
        #store the ant's location
        self.ant = ((col, row), 3)

    #Draw_Up_Ant draws an upward facing ant on the tile given
    def Draw_Up_Ant(self, (col,row)):
        #get the coordinates on the screen for where the ant should be
        x = 20 + 40 * col
        y = 30 + 40 * row
        #draw the ant
        pygame.draw.polygon(self.board, (255,0,0), ((x,y), (x+10,y+9), (x-10,y+9)),)
        #store the ant's location
        self.ant = ((col, row), 2)

    #Draw_Down_Ant draws a downward facing ant on the tile given
    def Draw_Down_Ant(self, (col,row)):
        #get the coordinates on the screen for where the ant should be
        x = 20 + 40 * col
        y = 10 + 40 * row
        #draw the ant
        pygame.draw.polygon(self.board, (255,0,0), ((x,y), (x+10,y-9), (x-10,y-9)),)
        #store the ant's location
        self.ant = ((col, row), 4)

    #Draw_Ant draws an ant at the tile stored self.ant and the direction stored in self.ant
    def Draw_Ant(self):
        if self.ant[1] == 1:
            self.Draw_Left_Ant(self.ant[0])
        if self.ant[1] == 2:
            self.Draw_Up_Ant(self.ant[0])
        if self.ant[1] == 3:
            self.Draw_Right_Ant(self.ant[0])
        if self.ant[1] == 4:
            self.Draw_Down_Ant(self.ant[0])

    #Make_Ant takes in a tile and a direction and creates an ant there
    def Make_Ant(self, (x,y), direct):
        #if the given tile is a horizontal tile
        if self.tiles[(x, y)][0] == 'H':
            if direct == 1:
                #if the direction calls for a left facing ant
                self.Draw_Left_Ant((x,y))
            else:
                #if the direction calls for a right facing ant
                self.Draw_Right_Ant((x,y))
        #else, the tile is a vertical tile
        elif self.tiles[(x, y)][0] == 'V':
            if direct == 2:
                #if the direction calls for an upward facing ant
                self.Draw_Up_Ant((x,y))
            else:
                #if the direction calls for a downward facing ant
                self.Draw_Down_Ant((x,y))
        #store the ant's location
        self.tiles[(x,y)][5] = (True, direct)
        #set the origin to the tile
        self.origin = ((x,y), direct)
        pygame.display.flip()

    #Make_Ant_Center makes a left facing ant at the center
    def Make_Ant_Center(self):
        self.Make_Ant(self.center,1)

    #Make_New_Ant takes away any existing ants and makes a new ant at the given tile
    def Make_New_Ant(self, (x,y), direct):
        #checks to see if there is an existing ant
        if self.ant != None:
            #clears the information holding the ant
            self.tiles[self.ant[0]][5] = (False, None)
            #checks if the ant was inside the screen parameters
            if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                #if the ant is inside the screen it clears the tile it was on
                self.Make_Truchet_Tile(self.ant[0])
        #once the old ant is gone, it makes a new ant
        self.Make_Ant((x,y), direct)

    #Make_New_Center_Ant makes a new ant at the center
    def Make_New_Center_Ant(self):
        self.Make_New_Ant(self.center, 1)

    #Reverse_Ant reverses the ant's direction
    def Reverse_Ant(self,):
        #Check to see if the ant is already reversed
        if self.reverse:
            #if it is reversed it reverses it again
            self.reverse = False
        else:
            self.reverse = True
        if self.ant[1] == 1:
            #if the ant is left facing it removes the ant from the tile
            #then it draws a right facing ant on the tile one tile to the right
            #and it stores the new ant location in self.ant
            self.tiles[self.ant[0]][5] = (False, None)
            self.Draw_Right_Ant((self.ant[0][0] + 1, self.ant[0][1]))
            self.tiles[self.ant[0]][5] = (True, 3)
        elif self.ant[1] == 2:
            #if the ant is upward facing it removes the ant from the tile
            #then it draws a downward facing ant on the tile one tile down
            #and it stores the new ant location in self.ant
            self.tiles[self.ant[0]][5] = (False, None)
            self.Draw_Down_Ant((self.ant[0][0], self.ant[0][1] + 1))
            self.tiles[self.ant[0]][5] = (True, 4)
        elif self.ant[1] == 3:
            #if the ant is right facing it removes the ant from the tile
            #then it draws a left facing ant on the tile one tile to the left
            #and it stores the new ant location in self.ant
            self.tiles[self.ant[0]][5] = (False, None)
            self.Draw_Left_Ant((self.ant[0][0] - 1, self.ant[0][1]))
            self.tiles[self.ant[0]][5] = (True, 1)
        elif self.ant[1] == 4:
            #if the ant is downward facing it removes the ant from the tile
            #then it draws an upward facing ant on the tile one tile up
            #and it stores the new ant location in self.ant
            self.tiles[self.ant[0]][5] = (False, None)
            self.Draw_Up_Ant((self.ant[0][0], self.ant[0][1] - 1))
            self.tiles[self.ant[0]][5] = (True, 2)
        #reverses the rule
        self.Reverse_Rule()
        for key in self.tiles:
            #for every tile it changes the vertical tiles to horizontal tiles and the horizontal tiles to vertical tiles
            if self.tiles[key][0] == 'V':
                self.tiles[key][0] = 'H'
            else:
                self.tiles[key][0] = 'V'
            #updates if the tile is hot
            self.Is_Hot(key)
            #for every tile in the parameters of the screen it refreshes the image of the tile
            if (key[0] >= 0 and key[0] <= self.width_ref - 1) and (key[1] >= 0 and key[1] <= self.height_ref - 1):
                self.Make_Truchet_Tile(key)
        #refreshing the board it redraws the ant before updating the screen
        self.Draw_Ant()
        pygame.display.flip()

    #Move_Ant moves the ant one tile according to the rule and information about the tile
    def Move_Ant(self):
        #Move_Ant first finds which tile the ant is in and which position in that tile the ant is.
        if self.tiles[self.ant[0]][5][1] == 1:
            #Then it sees if the ant is moving left or right.
            if self.tiles[self.ant[0]][1] == 'L':
                #It checks if it's reversed
                if self.reverse:
                    #if it is then the count of steps decreases and antisteps increases
                    self.tiles[self.ant[0]][2] -= 1
                    self.tiles[self.ant[0]][6] += 1
                else:
                    #if it isn't then the count of steps increases and antisteps decreases
                    self.tiles[self.ant[0]][2] += 1
                    self.tiles[self.ant[0]][6] -= 1
                #It makes sure that the ant is within the screen, before attempting to draw anything
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    #it then refreshes the tile that the ant was in
                    self.Make_Truchet_Tile(self.ant[0])
                else:
                    #if the tile isn't on the screen it still updates information about that tile
                    self.Color(self.ant[0])
                    self.Is_Hot(self.ant[0])
                    self.Rule(self.ant[0])
                #Moves the ant's position to the new tile.
                self.tiles[self.ant[0]][5] = (False, None)
                self.ant = ((self.ant[0][0], self.ant[0][1] + 1), 4)
                #And checks to see if the new tile is in the dictionary, if not it adds it to the dictionary
                if self.ant[0] not in self.tiles:
                    if self.reverse:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]
                    else:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]
                    self.tiles[self.ant[0]].append(self.rule[0])
                    self.tiles[self.ant[0]].append(0)
                    self.tiles[self.ant[0]].append(self.white)
                    self.tiles[self.ant[0]].append(False)
                    self.tiles[self.ant[0]].append((False, None))
                    self.tiles[self.ant[0]].append(0)
                    self.Is_Hot(self.ant[0])
                #And once again, we only draw it if it's in the screen parameters.
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Draw_Down_Ant(self.ant[0])
                #Set the new position of the ant
                self.tiles[self.ant[0]][5] = (True, 4)
            #It does the same thing if the ant turns right
            elif self.tiles[self.ant[0]][1] == 'R':
                if self.reverse:
                    self.tiles[self.ant[0]][2] -= 1
                    self.tiles[self.ant[0]][6] += 1
                else:
                    self.tiles[self.ant[0]][2] += 1
                    self.tiles[self.ant[0]][6] -= 1
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Make_Truchet_Tile(self.ant[0])
                else:
                    self.Color(self.ant[0])
                    self.Is_Hot(self.ant[0])
                    self.Rule(self.ant[0])
                self.tiles[self.ant[0]][5] = (False, None)
                self.ant = ((self.ant[0][0], self.ant[0][1] - 1), 2)
                if self.ant[0] not in self.tiles:
                    if self.reverse:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]
                    else:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]
                    self.tiles[self.ant[0]].append(self.rule[0])
                    self.tiles[self.ant[0]].append(0)
                    self.tiles[self.ant[0]].append(self.white)
                    self.tiles[self.ant[0]].append(False)
                    self.tiles[self.ant[0]].append((False, None))
                    self.tiles[self.ant[0]].append(0)
                    self.Is_Hot(self.ant[0])
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Draw_Up_Ant(self.ant[0])
                self.tiles[self.ant[0]][5] = (True, 2)
                
        #Or if the ant is at a different position in the square        
        elif self.tiles[self.ant[0]][5][1] == 2:
            if self.tiles[self.ant[0]][1] == 'L':
                if self.reverse:
                    self.tiles[self.ant[0]][2] -= 1
                    self.tiles[self.ant[0]][6] += 1
                else:
                    self.tiles[self.ant[0]][2] += 1
                    self.tiles[self.ant[0]][6] -= 1
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Make_Truchet_Tile(self.ant[0])
                else:
                    self.Color(self.ant[0])
                    self.Is_Hot(self.ant[0])
                    self.Rule(self.ant[0])
                self.tiles[self.ant[0]][5] = (False, None)
                self.ant = ((self.ant[0][0] - 1, self.ant[0][1]), 1)
                if self.ant[0] not in self.tiles:
                    if self.reverse:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]
                    else:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]
                    self.tiles[self.ant[0]].append(self.rule[0])
                    self.tiles[self.ant[0]].append(0)
                    self.tiles[self.ant[0]].append(self.white)
                    self.tiles[self.ant[0]].append(False)
                    self.tiles[self.ant[0]].append((False, None))
                    self.tiles[self.ant[0]].append(0)
                    self.Is_Hot(self.ant[0])
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Draw_Left_Ant(self.ant[0])
                self.tiles[self.ant[0]][5] = (True, 1)
            elif self.tiles[self.ant[0]][1] == 'R':
                if self.reverse:
                    self.tiles[self.ant[0]][2] -= 1
                    self.tiles[self.ant[0]][6] += 1
                else:
                    self.tiles[self.ant[0]][2] += 1
                    self.tiles[self.ant[0]][6] -= 1
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Make_Truchet_Tile(self.ant[0])
                else:
                    self.Color(self.ant[0])
                    self.Is_Hot(self.ant[0])
                    self.Rule(self.ant[0])
                self.tiles[self.ant[0]][5] = (False, None)
                self.ant = ((self.ant[0][0] + 1, self.ant[0][1]), 3)
                if self.ant[0] not in self.tiles:
                    if self.reverse:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]
                    else:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]
                    self.tiles[self.ant[0]].append(self.rule[0])
                    self.tiles[self.ant[0]].append(0)
                    self.tiles[self.ant[0]].append(self.white)
                    self.tiles[self.ant[0]].append(False)
                    self.tiles[self.ant[0]].append((False, None))
                    self.tiles[self.ant[0]].append(0)
                    self.Is_Hot(self.ant[0])
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Draw_Right_Ant(self.ant[0])
                self.tiles[self.ant[0]][5] = (True, 3)

        elif self.tiles[self.ant[0]][5][1] == 3:
            if self.tiles[self.ant[0]][1] == 'L':
                if self.reverse:
                    self.tiles[self.ant[0]][2] -= 1
                    self.tiles[self.ant[0]][6] += 1
                else:
                    self.tiles[self.ant[0]][2] += 1
                    self.tiles[self.ant[0]][6] -= 1
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Make_Truchet_Tile(self.ant[0])
                else:
                    self.Color(self.ant[0])
                    self.Is_Hot(self.ant[0])
                    self.Rule(self.ant[0])
                self.tiles[self.ant[0]][5] = (False, None)
                self.ant = ((self.ant[0][0], self.ant[0][1] - 1), 2)
                if self.ant[0] not in self.tiles:
                    if self.reverse:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]
                    else:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]
                    self.tiles[self.ant[0]].append(self.rule[0])
                    self.tiles[self.ant[0]].append(0)
                    self.tiles[self.ant[0]].append(self.white)
                    self.tiles[self.ant[0]].append(False)
                    self.tiles[self.ant[0]].append((False, None))
                    self.tiles[self.ant[0]].append(0)
                    self.Is_Hot(self.ant[0])
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Draw_Up_Ant(self.ant[0])
                self.tiles[self.ant[0]][5] = (True, 2)
            elif self.tiles[self.ant[0]][1] == 'R':
                if self.reverse:
                    self.tiles[self.ant[0]][2] -= 1
                    self.tiles[self.ant[0]][6] += 1
                else:
                    self.tiles[self.ant[0]][2] += 1
                    self.tiles[self.ant[0]][6] -= 1
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Make_Truchet_Tile(self.ant[0])
                else:
                    self.Color(self.ant[0])
                    self.Is_Hot(self.ant[0])
                    self.Rule(self.ant[0])
                self.tiles[self.ant[0]][5] = (False, None)
                self.ant = ((self.ant[0][0], self.ant[0][1] + 1), 4)
                if self.ant[0] not in self.tiles:
                    if self.reverse:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]
                    else:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]
                    self.tiles[self.ant[0]].append(self.rule[0])
                    self.tiles[self.ant[0]].append(0)
                    self.tiles[self.ant[0]].append(self.white)
                    self.tiles[self.ant[0]].append(False)
                    self.tiles[self.ant[0]].append((False, None))
                    self.tiles[self.ant[0]].append(0)
                    self.Is_Hot(self.ant[0])
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Draw_Down_Ant(self.ant[0])
                self.tiles[self.ant[0]][5] = (True, 4)

        elif self.tiles[self.ant[0]][5][1] == 4:
            if self.tiles[self.ant[0]][1] == 'L':
                if self.reverse:
                    self.tiles[self.ant[0]][2] -= 1
                    self.tiles[self.ant[0]][6] += 1
                else:
                    self.tiles[self.ant[0]][2] += 1
                    self.tiles[self.ant[0]][6] -= 1
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Make_Truchet_Tile(self.ant[0])
                else:
                    self.Color(self.ant[0])
                    self.Is_Hot(self.ant[0])
                    self.Rule(self.ant[0])
                self.tiles[self.ant[0]][5] = (False, None)
                self.ant = ((self.ant[0][0] + 1, self.ant[0][1]), 3)
                if self.ant[0] not in self.tiles:
                    if self.reverse:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]
                    else:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]
                    self.tiles[self.ant[0]].append(self.rule[0])
                    self.tiles[self.ant[0]].append(0)
                    self.tiles[self.ant[0]].append(self.white)
                    self.tiles[self.ant[0]].append(False)
                    self.tiles[self.ant[0]].append((False, None))
                    self.tiles[self.ant[0]].append(0)
                    self.Is_Hot(self.ant[0])
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Draw_Right_Ant(self.ant[0])
                self.tiles[self.ant[0]][5] = (True, 3)
            elif self.tiles[self.ant[0]][1] == 'R':
                if self.reverse:
                    self.tiles[self.ant[0]][2] -= 1
                    self.tiles[self.ant[0]][6] += 1
                else:
                    self.tiles[self.ant[0]][2] += 1
                    self.tiles[self.ant[0]][6] -= 1
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Make_Truchet_Tile(self.ant[0])
                else:
                    self.Color(self.ant[0])
                    self.Is_Hot(self.ant[0])
                    self.Rule(self.ant[0])
                self.tiles[self.ant[0]][5] = (False, None)
                self.ant = ((self.ant[0][0] - 1, self.ant[0][1]), 1)
                if self.ant[0] not in self.tiles:
                    if self.reverse:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]
                    else:
                        if self.ant[0][0]%2 == self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["H"]                       
                        if self.ant[0][0]%2 != self.ant[0][1]%2:
                            self.tiles[self.ant[0]] = ["V"]
                    self.tiles[self.ant[0]].append(self.rule[0])
                    self.tiles[self.ant[0]].append(0)
                    self.tiles[self.ant[0]].append(self.white)
                    self.tiles[self.ant[0]].append(False)
                    self.tiles[self.ant[0]].append((False, None))
                    self.tiles[self.ant[0]].append(0)
                    self.Is_Hot(self.ant[0])
                if (self.ant[0][0] >= 0 and self.ant[0][0] <= self.width_ref - 1) and (self.ant[0][1] >= 0 and self.ant[0][1] <= self.height_ref - 1):
                    self.Draw_Left_Ant(self.ant[0])
                self.tiles[self.ant[0]][5] = (True, 1)

    #Move_Ant_Step moves the ant one step
    def Move_Ant_Step(self):
        self.Move_Ant()
        if self.reverse:
            self.time -= 1
        else:
            self.time += 1
        pygame.display.flip()

    #Move_Ant_N moves the ant n steps
    def Move_Ant_N(self, n):
        for x in range(n):
            self.Move_Ant()
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
        #moves the ant the nexessary amount of time
        if time_diff > 0:
            self.Move_Ant_N(time_diff)
        if time_diff < 0:
            self.Reverse_Ant()
            self.Move_Ant_N(-(time_diff))
            self.Reverse_Ant()

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
            #if the ant is a reverse ant
            #then the rule for a tile equals the equivalency of the number of times the tiles has been antistepped on mod the length of the rule string
            self.tiles[coord][1] = self.rule[(-1 * (1 + (self.tiles[coord][6] % len(self.rule))))]

    #Draw_Diagonal1 draws a diagonal line through right horizontal tiles and left vertical tiles
    def Draw_Diagonal1(self, (x,y), color):
        if self.tiles[(x,y)][4]:
            pygame.draw.lines(self.surface, color, True, ((0, 0), (40, 40)), 1)

    #Draw_Diagonal2 draws a diagonal line through left horizontal tiles and right vertical tiles
    def Draw_Diagonal2(self, (x,y), color):
        if self.tiles[(x,y)][4]:
            pygame.draw.lines(self.surface, color, True, ((40, 0), (0, 40)), 1)

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

    #Run_Time_Step runs in steps with a slight time delay in between each step
    def Run_Time_Step(self):
        while 1:
            self.Move_Ant_Step()
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
                    self.Reverse_Ant()
                    pygame.display.flip()
            #press shift to break
            if press[304] == 1 or press[303] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[304] == 0 or press[303] == 0:
                    x = 1
                    break
                
            self.screen.blit(self.board, (0,0))
            pygame.display.flip()

    #Run_Time_N runs in jumps of n with a slight time delay in between each step
    def Run_Time_N(self, n):
        while 1:
            self.Move_Ant_N(n)
            print('Time = ' + str(self.time))
            pygame.time.delay(1)
            pygame.event.get()
            press2 = pygame.key.get_pressed()
            if press2[114] == 1:
                pygame.event.wait()
                press2 = pygame.key.get_pressed()
                if press2[114] == 0:
                    print('Reverse')
                    self.Reverse_Ant()
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
                    self.Move_Ant_Step()
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
                    self.Move_Ant_N(n)
                    print('Time = ' + str(self.time))
            self.screen.blit(self.board, (0,0))
            pygame.display.flip()

    #Run runs the ants program and simulates the behavior
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
                    self.Move_Ant_Step()
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
                    self.Reverse_Ant()
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
                    self.Move_Ant_Step()
                    self.screen.blit(self.board, (0,0))
                    pygame.display.flip()
                    print('Time = ' + str(self.time))
                    while self.ant != self.origin:
                        e2 = pygame.event.get()
                        for event in e2:
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        self.Move_Ant_Step()
                        print('Time = ' + str(self.time))
                        self.screen.blit(self.board, (0,0))
                        pygame.display.flip()
            #m skips to origin
            if press[109] == 1:
                pygame.event.wait()
                press = pygame.key.get_pressed()
                if press[109] == 0:
                    n = 0
                    self.Move_Ant()
                    n += 1
                    while self.ant != self.origin:
                        self.Move_Ant()
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
            #update the screen
            self.screen.blit(self.board, (0,0))
            pygame.display.flip()

            if e.type == pygame.QUIT:
             pygame.quit()
             sys.exit()
