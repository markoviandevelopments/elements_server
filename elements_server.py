import pygame
import time
import random


WIDTH, HEIGHT = 800, 800
GRID_W = 20

el_selected = 1

mouse_pos = (0,0)

grid = []

has_updated = False


for y in range(GRID_W):
    grid_tmp = []
    for x in range(GRID_W):
        grid_tmp.append(0)
    grid.append(grid_tmp)

pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT))

running = True
while running:
    has_updated = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            has_updated = True
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_h]:
        el_selected = (el_selected + 1) % 5
        

    window.fill((0,0,0))

    for y in range(GRID_W):
        for x in range(GRID_W):
            if grid[x][y] == 1:
                color = (100, 100, 10)
            elif grid[x][y] == 2:
                color = (0,0,255)
            elif grid[x][y] == 3:
                color = (100,100,100)
            elif grid[x][y] == 4:
                color = (250, 114, 64)
            else:
                color = (15, 15, 15)
            
            Pix_S = WIDTH / GRID_W
            x_draw = int(Pix_S * x)
            y_draw = int(Pix_S * y)
            pygame.draw.rect(window, color, (x_draw, y_draw, Pix_S, Pix_S))
    
    
    
    x_index = int(mouse_pos[0] / WIDTH * GRID_W)
    y_index = int(mouse_pos[1] / WIDTH * GRID_W)

    if has_updated:
        grid[x_index][y_index] = el_selected
            


    pygame.draw.rect(window, (255, 255, 0), (mouse_pos[0] - 2, mouse_pos[1] - 2, 4, 4))
    pygame.display.flip()

    for y in range(GRID_W - 2, -1, -1):
        for x in range(GRID_W):
            if grid[x][y] == 1 or grid[x][y] == 2 and grid[x][y + 1] == 0:
                elem = grid[x][y]
                grid[x][y+1] = elem
                grid[x][y] = 0
    
    for y in range(GRID_W):
        for x in range(GRID_W):
            if grid[x][y] == 2:
                r = random.uniform(0, 1)
                if r < 0.02:
                    if random.randint(0, 1):
                        if x > 0:   # Check left to see if we can move left
                            if grid[x - 1][y] == 0:
                                grid[x][y] = 0
                                grid[x - 1][y] = 2
                    else:
                        if x < GRID_W - 1:
                            if grid[x + 1][y] == 0:
                                grid[x][y] = 0
                                grid[x + 1][y] = 2
            if grid[x][y] == 4:
                r = random.uniform(0, 1)
                if r < 0.1:
                    if random.randint(0, 1):
                        if x > 0:
                            if grid[x - 1][y] == 0:
                                grid[x][y] = 0
                                grid[x - 1][y] = 4
                    else:
                        if x < GRID_W - 1:
                            if grid[x + 1][y] == 0:
                                grid[x][y] = 0
                                grid[x + 1][y] = 4
    
    time.sleep(0.025)
pygame.display.quit()
