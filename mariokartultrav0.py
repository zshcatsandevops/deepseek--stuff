from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader
import random
import math

app = Ursina()

# Game settings
window.borderless = False
window.fullscreen = False
window.title = 'Mario Kart Clone'
window.exit_button.visible = False

# Track generation
def generate_track():
    track_entities = []
    
    # Create road segments in a circular pattern
    segments = 20
    for i in range(segments):
        angle = (i / segments) * 360
        x = math.cos(math.radians(angle)) * 20
        z = math.sin(math.radians(angle)) * 20
        
        road = Entity(
            model='cube',
            color=color.gray,
            position=(x, -0.5, z),
            scale=(5, 0.1, 5),
            rotation=(0, angle, 0)
        )
        track_entities.append(road)
        
        # Add road borders
        border1 = Entity(
            model='cube',
            color=color.red,
            position=(x + 2.5, -0.4, z),
            scale=(0.2, 0.2, 5),
            rotation=(0, angle, 0)
        )
        
        border2 = Entity(
            model='cube',
            color=color.red,
            position=(x - 2.5, -0.4, z),
            scale=(0.2, 0.2, 5),
            rotation=(0, angle, 0)
        )
        
        track_entities.extend([border1, border2])
    
    # Add some obstacles and items - FIXED VERSION
    obstacles = []
    items = []
    for i in range(10):
        angle = random.randint(0, 360)
        x = math.cos(math.radians(angle)) * 18
        z = math.sin(math.radians(angle)) * 18
        
        # Use the same random value for both decisions
        if random.random() > 0.5:
            # Obstacle
            obstacle = Entity(
                model='cube',
                color=color.orange,
                position=(x, 0, z),
                scale=(1, 1, 1),
                collider='box'
            )
            obstacles.append(obstacle)
            track_entities.append(obstacle)
        else:
            # Item box
            item = Entity(
                model='cube',
                color=color.yellow,
                position=(x, 0.5, z),
                scale=(1, 1, 1),
                collider='box'
            )
            items.append(item)
            track_entities.append(item)
    
    return track_entities, obstacles, items

# Kart class
class Kart(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.model = 'cube'
        self.color = color.blue
        self.scale = (1, 0.5, 2)
        self.position = (0, 0, 0)
        self.rotation = (0, 0, 0)
        self.collider = 'box'
        
        self.speed = 0
        self.max_speed = 20
        self.acceleration = 0.5
        self.steering_speed = 2
        self.drift_factor = 0.95
        self.is_drifting = False
        self.has_item = False
        self.item_type = None
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def update(self):
        # Movement controls
        if held_keys['w'] or held_keys['up arrow']:
            self.speed += self.acceleration * time.dt
        elif held_keys['s'] or held_keys['down arrow']:
            self.speed -= self.acceleration * time.dt
        else:
            # Gradual slowdown
            self.speed *= 0.95
            
        # Limit speed
        self.speed = max(-self.max_speed/2, min(self.speed, self.max_speed))
        
        # Steering
        if held_keys['a'] or held_keys['left arrow']:
            self.rotation_y -= self.steering_speed * (self.speed/self.max_speed) * 50 * time.dt
        if held_keys['d'] or held_keys['right arrow']:
            self.rotation_y += self.steering_speed * (self.speed/self.max_speed) * 50 * time.dt
            
        # Drifting
        if held_keys['space'] and abs(self.speed) > self.max_speed/3:
            self.is_drifting = True
            self.color = color.cyan
        else:
            self.is_drifting = False
            self.color = color.blue
            
        # Move the kart
        self.position += self.forward * self.speed * time.dt
        
        # Keep kart on track
        if self.y < -1:
            self.y = 0
            self.speed *= 0.5
            
        # Check for collisions with obstacles
        for obstacle in obstacles:
            if distance(self, obstacle) < 2:
                self.speed *= 0.5  # Slow down when hitting obstacle
                obstacle.shake(duration=0.5)
                
        # Use item if player has one
        if self.has_item and held_keys['e']:
            self.use_item()

    def use_item(self):
        if self.item_type == "mushroom":
            self.speed += 10  # Boost speed
            invoke(setattr, self, 'speed', self.speed - 10, delay=2)  # Remove boost after 2 seconds
        self.has_item = False
        self.item_type = None
        item_text.text = 'Item: None'

# Camera follow system
def camera_follow():
    if player:
        camera.position = player.position - player.forward * 10 + Vec3(0, 5, 0)
        camera.rotation_x = 20
        camera.look_at(player.position)

# Create game elements
track, obstacles, items = generate_track()
player = Kart()
sky = Sky()

# UI elements
speed_text = Text(text='Speed: 0', position=(-0.8, 0.4), scale=2)
item_text = Text(text='Item: None', position=(-0.8, 0.3), scale=2)

# Update function
def update():
    camera_follow()
    if player:
        speed_text.text = f'Speed: {int(abs(player.speed))}'
    
    # Check for item collisions
    for item in items:
        if distance(player, item) < 2:
            player.has_item = True
            player.item_type = "mushroom"
            item_text.text = 'Item: Mushroom (Press E to use)'
            # Reposition the item
            angle = random.randint(0, 360)
            x = math.cos(math.radians(angle)) * 18
            z = math.sin(math.radians(angle)) * 18
            item.position = (x, 0.5, z)

# Start game
def input(key):
    if key == 'r':
        player.position = (0, 0, 0)
        player.speed = 0
        player.rotation = (0, 0, 0)
    if key == 'escape':
        app.quit()

# Instructions
instructions = Text(
    text='Controls: WASD/Arrows to move, Space to drift, R to reset, E to use item',
    position=(-0.8, -0.4),
    scale=1.5
)

app.run()
