#!/usr/bin/env python

import os
import pygame
import sys
from copy import deepcopy, copy
from random import randint, choice

class Board():
    '''xres=240, yres=320, blocksize=16, bgcolor=black'''
    def __init__(self, xres=240, yres=320, blocksize=16, bgcolor=(255,255,255)):
        if xres%blocksize:
            raise
        if yres%blocksize:
            raise
        self.xres=xres
        self.yres=yres
        self.blocksize=blocksize
        self.width=xres/blocksize
        self.height=yres/blocksize
        self.bgcolor=bgcolor
        self.screen = pygame.display.set_mode((self.xres, self.yres))
        self.running = True
        self.grid = []
        for row in range(self.height):
            self.grid.append([])
            for cell in range(self.width):
                self.grid[row].append(False)

    def __update_cells(self):
        for yy in range(self.height):
            for xx in range(self.width):
                if self.grid[yy][xx]:
                    self.grid[yy][xx].x = xx
                    self.grid[yy][xx].y = yy

    def initscreen(self):
        self.screen = pygame.display.set_mode((self.xres, self.yres))
        
    def printg(self):
        yy = 0
        for row in self.grid:
            xx = 0
            for cell in row:
                if cell:
                    print '%d,%d' % (cell.x,cell.y),
                else:
                    print '    ',
                xx += 1
            print
            yy += 1

    def drop_rows(self):
        yy = 0
        while yy < self.height:
            line_full = True
            for cell in self.grid[yy]:
                if not cell: line_full = False
            if line_full:
                for cell in self.grid[yy]: cell.erase()
                self.grid.pop(yy)
                self.grid.insert(0, [False for cell in range(self.width)])
                self.__update_cells()
                self.draw()
                PIECE.draw()
                pygame.display.flip()
            else:
                yy += 1
                
    def draw(self):
        yy = 0
        for row in self.grid:
            xx = 0
            for cell in row:
                if cell:
                    cell.draw()
                else:
                    rect = pygame.Rect(
                            (xx*self.blocksize, yy*self.blocksize),
                            (self.blocksize, self.blocksize)
                            )
                    pygame.draw.rect(self.screen, self.bgcolor, rect)
                xx += 1
            yy += 1

class Block():
    '''board, color=random, (x,y)=(0,0)'''
    def __init__(self, board, color=None, (x,y)=(0,0)):
        self.x = x
        self.y = y
        self.board = board
        self.surface = self.board.screen
        if color == None:
            self.color = randcolor()
        else:
            self.color = color

    def __abs_x(self):
        return self.x*self.board.blocksize
    def __abs_y(self):
        return self.y*self.board.blocksize
    def draw(self, drcolor=None):
        if drcolor == None:
            drcolor = self.color

        rect = pygame.Rect(
                (self.__abs_x(), self.__abs_y()),
                (self.board.blocksize, self.board.blocksize)
                )
        pygame.draw.rect(self.surface, drcolor, rect)

##this uses shitloads of cpu
#       if drcolor == self.color: #cheap hack to prevent text from drawing upon erase
#           text = '%d,%d' % (self.x,self.y)
#           font = pygame.font.Font(None, 18)
#           txtimg = font.render(text, 0, (255,255,255))
#           self.surface.blit(txtimg, (self.abs_x(), self.abs_y()))

    def erase(self):
        self.draw(self.board.bgcolor)

class Shape():
    '''board, grid=None, color=random, (x,y)=(0,0)'''
    def __init__(self, board, grid=None, color=None, (x,y)=(False,0)):
        '''make a shape'''
        self.board = board
        self.surface = self.board.screen
        self.color = color
        self.y = y
        if x:
            self.x = x
        else:
            self.x = self.board.width/2
        self.landed = False
        #Initialize Grid
        if grid == None:
            self.grid = [[True]]
        else:
            self.grid = grid

        self.height = len(self.grid)
        self.heightidx = self.height-1
        self.width = len(self.grid[0])
        self.widthidx = self.width-1
        for yy in range(self.height):
            for xx in range(self.width):
                if self.grid[yy][xx]:
                    self.grid[yy][xx] = Block(self.board, self.color, (self.x+xx, self.y+yy))

    def __update_cells(self):
        self.width = len(self.grid[0])
        self.widthidx = self.width-1
        self.height = len(self.grid)
        self.heightidx = self.height-1
        for yy in range(self.height):
            for xx in range(self.width):
                if self.grid[yy][xx]:
                    self.grid[yy][xx].x = self.x+xx
                    self.grid[yy][xx].y = self.y+yy

    def key_event(self, event):
        if event.key == pygame.K_DOWN:
            self.move(0,1)
        elif event.key == pygame.K_LEFT:
            self.move(-1,0)
        elif event.key == pygame.K_RIGHT:
            self.move(1,0)
        elif event.key == pygame.K_UP:
            self.rotate()
        elif event.key == pygame.K_SPACE:
            while not self.landed:
                self.move(0,1)

    def move(self, dx, dy):
        '''move the piece by dx,dy - handles collisions, returns True if moved'''
        testcp = deepcopy(self)
        testcp.x += dx
        testcp.y += dy
        testcp.__update_cells()
        if not testcp.collided():
            self.x += dx
            self.y += dy
            self.__update_cells()
            return True
        elif dy == 1:
            self.landed = True
            return False
        else:
            return False

    def collided(self):
        '''checks contents of self against self.board.grid'''

        #check walls and floor by brute force
        for row in self.grid:
            #left
            if row[0]:
                if row[0].x < 0:
                    #print 'left border'
                    return True
            #right
            if row[self.widthidx]:
                if row[self.widthidx].x >= self.board.width:
                    #print 'right border'
                    return True
        #bottom
        for col in range(self.width):
            if self.grid[self.heightidx][col]:
                if self.grid[self.heightidx][col].y >= self.board.height:
                    #print 'bottom border'
                    return True
        
        collided = False
        for yy in range(self.height):
            for xx in range(self.width):
                testcell = self.grid[yy][xx]
                if testcell and self.board.grid[testcell.y][testcell.x]:
                    #print 'collided at %d,%d' % (xx, yy)
                    return True
        return False

    def draw(self):
        for row in self.grid:
            for cell in row:
                if cell:
                    cell.draw()

    def erase(self):
        for row in self.grid:
            for cell in row:
                if cell:
                    cell.erase()

    def rotate(self):
        def __rot90(A):
            B = deepcopy(A)
            height = len(A)
            width = len(A[0])
            for yy in range(height):
                for xx in range(width):
                    B[height-1-xx][yy] = A[yy][xx]
            return B

        # rejigger the grid 90 degrees
        #rot90 = lambda tetrad: zip(*tetrad[::-1]) #shamelessly stolen
        testcp = deepcopy(self)
        testcp.grid = __rot90(testcp.grid)
        testcp.__update_cells()
        if not testcp.collided():
            self.grid = rot90(self.grid)
            self.__update_cells()

class I(Shape):
    def __init__(self, board, color=None):
        self.board = board
        self.color = color
        self.grid = [[True],[True],[True],[True]]
        Shape.__init__(self, self.board, self.grid)

class J(Shape):
    def __init__(self, board, color=None):
        self.board = board
        self.color = color
        self.grid = [[True,False,False],
                     [True,True,True]]
        Shape.__init__(self, self.board, self.grid)

class L(Shape):
    def __init__(self, board, color=None):
        self.board = board
        self.color = color
        self.grid = [[False,False,True],
                     [True,True,True]]
        Shape.__init__(self, self.board, self.grid)

class O(Shape):
    def __init__(self, board, color=None):
        self.board = board
        self.color = color
        self.grid = [[True,True],
                     [True,True]]
        Shape.__init__(self, self.board, self.grid)
    def rotate(self):
        pass

class S(Shape):
    def __init__(self, board, color=None):
        self.board = board
        self.color = color
        self.grid = [[False,True,True],
                     [True,True,False]]
        Shape.__init__(self, self.board, self.grid)

class T(Shape):
    def __init__(self, board, color=None):
        self.board = board
        self.color = color
        self.grid = [[False,True,False],
                     [True,True,True]]
        Shape.__init__(self, self.board, self.grid)

class Z(Shape):
    def __init__(self, board, color=None):
        self.board = board
        self.color = color
        self.grid = [[True,True,False],
                     [False,True,True]]
        Shape.__init__(self, self.board, self.grid)


def randcolor(min=pygame.Color('gray'), max=pygame.Color('white')):
    '''returns a random color with values between two inputs min and max'''
    (minr,ming,minb) = min[:3]
    (maxr,maxg,maxb) = max[:3]
    return (randint(minr,maxr),randint(ming,maxg),randint(minb,maxb))


# initialize pygame and set some globals
pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = '800,10'   # hack for macbook screen
BOARD = Board(320,640,32, (0,0,0))
BOARD.screen.fill(BOARD.bgcolor)
SHAPES = [I,J,L,O,S,T,Z]
PIECE = choice(SHAPES)(BOARD, color=randcolor())
CLOCK = pygame.time.Clock()
DROP = 0
pygame.display.flip()

# MAIN LOOP
while BOARD.running:

    BOARD.draw()

    #print PIECE.width, PIECE.height, PIECE.x, PIECE.y
    PIECE.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            BOARD.running = False
        elif event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_q) and pygame.key.get_mods()%pygame.K_LSHIFT:
                BOARD.running = False
            else: 
#                PIECE.erase()
                PIECE.key_event(event)
                PIECE.draw()

    if DROP > 1000:
#        PIECE.erase()
        PIECE.move(0,1)
        PIECE.draw()
        DROP = 0

    if PIECE.landed:
        #print 'landed'
#        PIECE.erase()
        for row in PIECE.grid:
            for cell in row:
                if cell: BOARD.grid[cell.y][cell.x] = cell
        PIECE = choice(SHAPES)(BOARD)
        DROP = 0

    BOARD.drop_rows()
    pygame.display.flip()
    DROP += CLOCK.tick(240)

pygame.quit()

#if __name__ == '__main__':
#    main()
