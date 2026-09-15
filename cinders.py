from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import time

app = Ursina(title='ChaosCinders 3D Adventure Game')
camera.position = (0, 5, 0)
camera.rotation_x = 45

# Player
player = FirstPersonController(height=2, speed=10, mouse_sensitivity=Vec3(80, 80, 0))

# Environment - Ground
ground = Entity(
    model='cube',
    scale=(100, 1, 100),
    color=color.dark_gray,
    texture='brick',
    collider='box'
)
ground.y = -1

# Sky Box
sky = Entity(
    model='cube',
    scale=(500, 500, 500),
    texture='white_cube',
    double_sided=True
)

# Game Variables
score = 0
coins_collected = 0
level = 1
game_started = False
start_time = 0
paused = False
paused_time = 0

# Coins (Sammelbare Objekte)
coins = []

def spawn_coins(count=20):
    """Spawn coins in random positions"""
    for i in range(count):
        coin = Entity(
            model='sphere',
            scale=0.5,
            color=color.yellow,
            position=(
                random.randint(-40, 40),
                2,
                random.randint(-40, 40)
            ),
            collider='sphere'
        )
        coins.append(coin)

# Obstacles (Hindernisse)
obstacles = []

def spawn_obstacles(count=15):
    """Spawn obstacles in random positions"""
    for i in range(count):
        obstacle = Entity(
            model='cube',
            scale=(1.5, 3, 1.5),
            color=color.red,
            position=(
                random.randint(-40, 40),
                1.5,
                random.randint(-40, 40)
            ),
            collider='box',
            texture='brick'
        )
        obstacles.append(obstacle)

# Bonus Items (Spezielle Gegenstände)
bonuses = []

def spawn_bonuses(count=5):
    """Spawn bonus items"""
    for i in range(count):
        bonus = Entity(
            model='sphere',
            scale=0.7,
            color=color.cyan,
            position=(
                random.randint(-40, 40),
                2,
                random.randint(-40, 40)
            ),
            collider='sphere'
        )
        bonuses.append(bonus)

# UI Text
ui_text = {
    'score': Text(text=f'Score: 0', origin=(-0.5, 0.45), scale=2.5, position=(-0.9, 0.45)),
    'level': Text(text=f'Level: 1', origin=(-0.5, 0.35), scale=2.5, position=(-0.9, 0.35)),
    'coins': Text(text=f'Coins: 0', origin=(-0.5, 0.25), scale=2.5, position=(-0.9, 0.25)),
    'time': Text(text=f'Time: 00:00', origin=(-0.5, 0.15), scale=2.5, position=(-0.9, 0.15)),
    'status': Text(text=f'Status: Bereit', origin=(-0.5, 0.05), scale=2, position=(-0.9, 0.05)),
    'controls': Text(
        text='WASD=Move | SPACE=Jump | ESC=Menu | P=Pause | R=Reset',
        origin=(0, 0.5),
        scale=1.5,
        position=(0, -0.45)
    )
}

# Lighting - Korrigiert
try:
    light = DirectionalLight(direction=(1, -1, -1))
    light.color = color.white()
except:
    # Fallback wenn DirectionalLight Probleme macht
    print("DirectionalLight konnte nicht vollständig initialisiert werden, aber das Spiel läuft!")

# Ambientes Licht
ambient_light = AmbientLight(color=color.rgba(255, 255, 255, 150))

def start_game():
    """Start das Spiel"""
    global game_started, start_time, paused, score, coins_collected, level
    game_started = True
    paused = False
    score = 0
    coins_collected = 0
    level = 1
    start_time = time.time()
    
    # Clear alte Objekte
    for coin in coins:
        destroy(coin)
    for obstacle in obstacles:
        destroy(obstacle)
    for bonus in bonuses:
        destroy(bonus)
    coins.clear()
    obstacles.clear()
    bonuses.clear()
    
    # Spawn neue Objekte
    spawn_coins(20)
    spawn_obstacles(15)
    spawn_bonuses(5)
    
    player.position = (0, 5, 0)
    ui_text['status'].text = 'Status: Läuft'
    print("🎮 Spiel gestartet!")

def pause_game():
    """Pausiere das Spiel"""
    global paused, paused_time
    if game_started:
        paused = not paused
        if paused:
            paused_time = time.time()
            ui_text['status'].text = 'Status: Pausiert'
        else:
            start_time += time.time() - paused_time
            ui_text['status'].text = 'Status: Läuft'
        print(f"Spiel {'pausiert' if paused else 'fortgesetzt'}")

def reset_game():
    """Setze das Spiel zurück"""
    global game_started, score, coins_collected, level, paused
    game_started = False
    paused = False
    score = 0
    coins_collected = 0
    level = 1
    
    for coin in coins:
        destroy(coin)
    for obstacle in obstacles:
        destroy(obstacle)
    for bonus in bonuses:
        destroy(bonus)
    coins.clear()
    obstacles.clear()
    bonuses.clear()
    
    player.position = (0, 5, 0)
    ui_text['status'].text = 'Status: Bereit'
    update_ui()
    print("🔄 Spiel zurückgesetzt!")

def update_ui():
    """Update die UI"""
    ui_text['score'].text = f'Score: {int(score)}'
    ui_text['level'].text = f'Level: {level}'
    ui_text['coins'].text = f'Coins: {coins_collected}'
    
    if game_started:
        elapsed = time.time() - start_time
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        ui_text['time'].text = f'Time: {minutes:02d}:{seconds:02d}'

def check_boundaries():
    """Überprüfe Spieler-Grenzen"""
    global score
    if abs(player.x) > 50 or abs(player.z) > 50:
        score -= 10
        player.position = (0, 5, 0)

def update():
    """Hauptupdate-Funktion"""
    global score, coins_collected, level, game_started
    
    if not game_started or paused:
        return
    
    # Münzen sammeln
    for coin in coins[:]:
        distance_to_coin = distance(player.position, coin.position)
        if distance_to_coin < 1.5:
            destroy(coin)
            coins.remove(coin)
            score += 10
            coins_collected += 1
            
            # Neue Münze spawnen
            new_coin = Entity(
                model='sphere',
                scale=0.5,
                color=color.yellow,
                position=(
                    random.randint(-40, 40),
                    2,
                    random.randint(-40, 40)
                ),
                collider='sphere'
            )
            coins.append(new_coin)
            
            # Level erhöhen
            if coins_collected % 10 == 0:
                level += 1
                print(f"⬆️ Level {level} erreicht!")
    
    # Bonus-Items sammeln
    for bonus in bonuses[:]:
        distance_to_bonus = distance(player.position, bonus.position)
        if distance_to_bonus < 1.5:
            destroy(bonus)
            bonuses.remove(bonus)
            score += 50
            print("⭐ Bonus gesammelt! +50 Punkte")
    
    # Collision mit Obstacles
    for obstacle in obstacles:
        distance_to_obstacle = distance(player.position, obstacle.position)
        if distance_to_obstacle < 2:
            score -= 5
            player.position = (0, 5, 0)
            print("💥 Mit Hindernis kollisioniert! -5 Punkte")
    
    # Grenzen prüfen
    check_boundaries()
    
    # UI aktualisieren
    update_ui()

def input(key):
    """Tastatureingaben"""
    if key == 'escape':
        print("Spiel beendet!")
        exit()
    elif key == 'g':
        start_game()
    elif key == 'p':
        pause_game()
    elif key == 'r':
        reset_game()

# Starte das Spiel automatisch
print("""
╔════════════════════════════════════════╗
║  ChaosCinders 3D Adventure Game 🎮     ║
╚════════════════════════════════════════╝

Steuerung:
  W/A/S/D    - Bewegen
  SPACE      - Springen
  MAUS       - Kamera kontrollieren
  G          - Spiel starten
  P          - Pausieren/Fortsetzen
  R          - Zurücksetzen
  ESC        - Beenden

Ziele:
  ⭐ Sammle gelbe Münzen (+10 Punkte)
  🌟 Sammle cyan Bonus-Items (+50 Punkte)
  🔴 Vermeide rote Hindernisse (-5 Punkte)
  📊 Erhöhe dein Level alle 10 Münzen

Viel Spaß! 🔥
""")

# Starte die Engine
spawn_coins(20)
spawn_obstacles(15)
spawn_bonuses(5)

app.run()
