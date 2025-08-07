import time
import random
import socket
import threading
import json

ACT_ONLY_AS_SERVER = True

if not ACT_ONLY_AS_SERVER:
    import pygame

GRID_W = 30

elements = ["nothing", "sand", "water", "block", "cloud", "gas", "void", "clone"]

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
        
        if element_type == "gas":
            self.is_gas = True
        else:
            self.is_gas = False
        
        if element_type != "nothing" and element_type != "block" and element_type != "void" and element_type != "clone":
            self.voided_by_void = True
        else:
            self.voided_by_void = False
        
        if element_type != "nothing" and element_type != "block" and element_type != "void" and element_type != "clone":
            self.cloned_by_clone = True
        else:
            self.cloned_by_clone = False
        
        if element_type == "clone":
            self.cloning_element_type = "nothing"

# Initialize grid as list of columns, each containing rows (grid[col][row])
grid = []
for x in range(GRID_W):  # columns
    col = []
    for y in range(GRID_W):  # rows
        col.append(Element("nothing"))
    grid.append(col)

# Threading lock for grid access
lock = threading.Lock()

# List of connected clients
clients = []

# Function to handle client connections
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        conn.setblocking(False)  # Non-blocking to avoid hanging
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                msg = json.loads(data.decode('utf-8'))
                if msg.get('action') == 'place':
                    col = msg.get('x')
                    row = msg.get('y')
                    el_type = msg.get('element')
                    if 0 <= col < GRID_W and 0 <= row < GRID_W and el_type in elements:
                        with lock:
                            grid[col][row] = Element(el_type)
            except json.JSONDecodeError:
                pass
            except BlockingIOError:
                time.sleep(0.01)  # Small sleep to prevent CPU spin
            except Exception as e:
                print(f"Error handling client {addr}: {e}")
                break
    with lock:
        if conn in clients:
            clients.remove(conn)

# Start server in a separate thread
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 6001))
    server.listen(5)
    server.setblocking(False)
    print("Server listening on port 6001")
    while True:
        try:
            conn, addr = server.accept()
            with lock:
                clients.append(conn)
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
        except BlockingIOError:
            time.sleep(0.01)

threading.Thread(target=start_server, daemon=True).start()

def simulate_and_send(force_sim=False):
    with lock:
        if force_sim or len(clients) > 0:
            # Falling simulation
            for y in range(GRID_W - 2, -1, -1):
                for x in range(GRID_W):
                    if grid[x][y].can_fall and grid[x][y + 1].element_type == "nothing":
                        elem = grid[x][y].element_type
                        grid[x][y + 1] = Element(elem)
                        grid[x][y] = Element("nothing")
            
            # Spreading simulation
            for y in range(GRID_W):
                for x in range(GRID_W):
                    el_type = grid[x][y].element_type
                    if el_type == "water":
                        r = random.uniform(0, 1)
                        if r < 0.02:
                            direction = random.randint(0, 1)
                            if direction == 0 and x > 0:
                                if grid[x - 1][y].element_type == "nothing":
                                    grid[x][y] = Element("nothing")
                                    grid[x - 1][y] = Element("water")
                            elif direction == 1 and x < GRID_W - 1:
                                if grid[x + 1][y].element_type == "nothing":
                                    grid[x][y] = Element("nothing")
                                    grid[x + 1][y] = Element("water")
                    elif el_type == "cloud":
                        r = random.uniform(0, 1)
                        if r < 0.1:
                            direction = random.randint(0, 1)
                            if direction == 0 and x > 0:
                                if grid[x - 1][y].element_type == "nothing":
                                    grid[x][y] = Element("nothing")
                                    grid[x - 1][y] = Element("cloud")
                            elif direction == 1 and x < GRID_W - 1:
                                if grid[x + 1][y].element_type == "nothing":
                                    grid[x][y] = Element("nothing")
                                    grid[x + 1][y] = Element("cloud")
                    elif el_type == "gas":
                        r = random.uniform(0, 1)
                        if r < 0.13:
                            direction = random.randint(0, 3)
                            if direction == 0 and x > 0:
                                if grid[x - 1][y].element_type == "nothing":
                                    grid[x][y] = Element("nothing")
                                    grid[x - 1][y] = Element("gas")
                            elif direction == 1 and x < GRID_W - 1:
                                if grid[x + 1][y].element_type == "nothing":
                                    grid[x][y] = Element("nothing")
                                    grid[x + 1][y] = Element("gas")
                            elif direction == 2 and y > 0:
                                if grid[x][y - 1].element_type == "nothing":
                                    grid[x][y] = Element("nothing")
                                    grid[x][y - 1] = Element("gas")
                            elif direction == 3 and y < GRID_W - 1:
                                if grid[x][y + 1].element_type == "nothing":
                                    grid[x][y] = Element("nothing")
                                    grid[x][y + 1] = Element("gas")
                    elif el_type == "void":
                        if x > 0:
                            if grid[x - 1][y].voided_by_void:
                                grid[x - 1][y] = Element("nothing")
                        if y > 0:
                            if grid[x][y - 1].voided_by_void:
                                grid[x][y - 1] = Element("nothing")
                        if x < GRID_W - 1:
                            if grid[x + 1][y].voided_by_void:
                                grid[x + 1][y] = Element("nothing")
                        if y < GRID_W - 1:
                            if grid[x][y + 1].voided_by_void:
                                grid[x][y + 1] = Element("nothing")
                    elif el_type == "clone":
                        if grid[x][y].cloning_element_type == "nothing":
                            if x > 0:
                                if grid[x - 1][y].cloned_by_clone:
                                    grid[x][y].cloning_element_type = grid[x - 1][y].element_type
                            if y > 0:
                                if grid[x][y - 1].cloned_by_clone:
                                    grid[x][y].cloning_element_type = grid[x][y - 1].element_type
                            if x < GRID_W - 1:
                                if grid[x + 1][y].cloned_by_clone:
                                    grid[x][y].cloning_element_type = grid[x + 1][y].element_type
                            if y < GRID_W - 1:
                                if grid[x][y + 1].cloned_by_clone:
                                    grid[x][y].cloning_element_type = grid[x][y + 1].element_type
                        else:
                            r = random.uniform(0, 1)
                            if 1:
                                direction = random.randint(0, 3)
                                if direction == 0 and x < GRID_W - 1:
                                    if grid[x + 1][y].element_type == "nothing":
                                        grid[x + 1][y] = Element(grid[x][y].cloning_element_type)
                                if direction == 1 and y > 0:
                                    if grid[x][y - 1].element_type == "nothing":
                                        grid[x][y - 1] = Element(grid[x][y].cloning_element_type)
                                if direction == 2 and x > 0:
                                    if grid[x - 1][y].element_type == "nothing":
                                        grid[x - 1][y] = Element(grid[x][y].cloning_element_type)
                                if direction == 3 and y < GRID_W - 1:
                                    if grid[x][y + 1].element_type == "nothing":
                                        grid[x][y + 1] = Element(grid[x][y].cloning_element_type)

        if len(clients) > 0:
            # Prepare state for clients
            state_grid = []
            for y in range(GRID_W):  # rows
                row = []
                for x in range(GRID_W):  # cols
                    row.append(grid[x][y].element_type)
                state_grid.append(row)
            state = {'type': 'state', 'grid': state_grid}
            state_json = json.dumps(state) + '\n'

            # Send to all clients
            for c in clients[:]:
                try:
                    c.sendall(state_json.encode('utf-8'))
                except Exception as e:
                    print(f"Error sending to client: {e}")
                    clients.remove(c)
                    c.close()

if ACT_ONLY_AS_SERVER:
    while True:
        simulate_and_send()
        time.sleep(0.025)
else:
    WIDTH, HEIGHT = 800, 800
    el_selected = 1
    mouse_pos = (0, 0)
    has_updated = False
    time_since_change_el = time.time()
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
        if keys[pygame.K_h] and time.time() - time_since_change_el > 0.2:
            el_selected = (el_selected + 1) % len(elements)
            time_since_change_el = time.time()
            

        window.fill((0, 0, 0))

        with lock:
            for y in range(GRID_W):
                for x in range(GRID_W):
                    el_type = grid[x][y].element_type
                    if el_type == "sand":
                        color = (100, 100, 10)
                    elif el_type == "water":
                        color = (0, 0, 255)
                    elif el_type == "block":
                        color = (100, 100, 100)
                    elif el_type == "cloud":
                        color = (173, 216, 230)
                    elif el_type == "gas":
                        color = (245, 11, 148)
                    elif el_type == "void":
                        color = (30, 0, 0)
                    elif el_type == "clone":
                        color = (255, 255, 0)
                    else:
                        color = (15, 15, 15)
                    
                    pix_s = WIDTH / GRID_W
                    x_draw = int(pix_s * x)
                    y_draw = int(pix_s * y)
                    pygame.draw.rect(window, color, (x_draw, y_draw, pix_s, pix_s))
        
        col_index = int(mouse_pos[0] / WIDTH * GRID_W)
        row_index = int(mouse_pos[1] / HEIGHT * GRID_W)

        if has_updated:
            if 0 <= col_index < GRID_W and 0 <= row_index < GRID_W:
                with lock:
                    grid[col_index][row_index] = Element(elements[el_selected])

        pygame.draw.rect(window, (255, 255, 0), (mouse_pos[0] - 2, mouse_pos[1] - 2, 4, 4))
        text = font.render(f"Element: {elements[el_selected]}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(110, 30))
        window.blit(text, text_rect)
        pygame.display.flip()

        simulate_and_send(force_sim=True)

        time.sleep(0.025)

    pygame.quit()