import pygame
import time
import random


WIDTH, HEIGHT = 800, 800
GRID_W = 20

el_selected = 1

mouse_pos = (0,0)

grid = []

has_updated = False

elements = ["nothing", "sand", "water", "block", "cloud"]



class Element:
    def __init__(self, element_type):
        self.element_type = element_type
        self.can_fall = False
        if self.element_type == "sand" or self.element_type == "water":
            self.can_fall = True
        else:
            self.can_fall = False
        
        if element_type == "water":
            self.is_liquid = True
        else:
            self.is_liquid = False

    

        

for y in range(GRID_W):
    grid_tmp = []
    for x in range(GRID_W):
        grid_tmp.append(Element("nothing"))
    grid.append(grid_tmp)

pygame.init()
font = pygame.font.Font(None, 36)

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
            if grid[x][y].element_type == "sand":
                color = (100, 100, 10)
            elif grid[x][y].element_type == "water":
                color = (0,0,255)
            elif grid[x][y].element_type == "block":
                color = (100,100,100)
            elif grid[x][y].element_type == "cloud":
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
        grid[x_index][y_index] = Element(elements[el_selected])
            


    pygame.draw.rect(window, (255, 255, 0), (mouse_pos[0] - 2, mouse_pos[1] - 2, 4, 4))
    text = font.render(f"Element: {elements[el_selected]}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(110, 30))
    window.blit(text, text_rect)
    pygame.display.flip()

    for y in range(GRID_W - 2, -1, -1):
        for x in range(GRID_W):
            if grid[x][y].can_fall and grid[x][y + 1].element_type == "nothing":
                elem = grid[x][y].element_type
                grid[x][y+1] = Element(elem)
                grid[x][y] = Element("nothing")
    
    for y in range(GRID_W):
        for x in range(GRID_W):
            if grid[x][y].element_type == "water":
                r = random.uniform(0, 1)
                if r < 0.02:
                    if random.randint(0, 1):
                        if x > 0:   # Check left to see if we can move left
                            if grid[x - 1][y].element_type == "nothing":
                                grid[x][y] = Element("nothing")
                                grid[x - 1][y] = Element("water")
                    else:
                        if x < GRID_W - 1:
                            if grid[x + 1][y].element_type == "nothing":
                                grid[x][y] = Element("nothing")
                                grid[x + 1][y] = Element("water")
            if grid[x][y].element_type == "cloud":
                r = random.uniform(0, 1)
                if r < 0.1:
                    if random.randint(0, 1):
                        if x > 0:
                            if grid[x - 1][y].element_type == "nothing":
                                grid[x][y] = Element("nothing")
                                grid[x - 1][y] = Element("cloud")
                    else:
                        if x < GRID_W - 1:
                            if grid[x + 1][y].element_type == "nothing":
                                grid[x][y] = Element("nothing")
                                grid[x + 1][y] = Element("cloud")
    
    time.sleep(0.025)
pygame.display.quit()
