import pygame
import psycopg2
import random
from datetime import datetime
conn = psycopg2.connect(
    dbname="snake_db",
    user="postgres",
    password="KBTU_naz2024",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users '
'(id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL);'
)
cursor.execute('CREATE TABLE IF NOT EXISTS user_scores '
'(id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), ' 
'level INTEGER, score INTEGER, saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'
)
conn.commit()

def get_or_create_user(username):
    cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    if user:
        user_id = user[0]
    else:
        cursor.execute('INSERT INTO users (username) VALUES (%s) RETURNING id', (username,))
        user_id = cursor.fetchone()[0]
        conn.commit()
    cursor.execute('SELECT MAX(level), MAX(score) FROM user_scores WHERE user_id = %s', (user_id,))
    level, score = cursor.fetchone()
    return user_id, level or 1, score or 0

def save_score(user_id, level, score):
    cursor.execute('INSERT INTO user_scores (user_id, level, score) VALUES (%s, %s, %s)', (user_id, level, score))
    conn.commit()
pygame.init()
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

username = input("Input username")
user_id, level, previous_score = get_or_create_user(username)
print(f"Hello, {username}! Current level: {level}, Previous score: {previous_score}")

levels = {
    1: {"speed": 10, "walls": []},
    2: {"speed": 15, "walls": [(200, 200, 200, 10), (100, 100, 10, 200)]},
    3: {"speed": 20, "walls": [(150, 150, 300, 10), (150, 250, 300, 10)]},
}

speed = levels[level]["speed"]
walls = levels[level]["walls"]
snake = [(100, 50)]
direction = (10, 0)
food = (random.randint(0, WIDTH // 10 - 1) * 10, random.randint(0, HEIGHT // 10 - 1) * 10)
score = 0
running = True

while running:
    clock.tick(speed)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_score(user_id, level, score)
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, 10):
                direction = (0, -10)
            elif event.key == pygame.K_DOWN and direction != (0, -10):
                direction = (0, 10)
            elif event.key == pygame.K_LEFT and direction != (10, 0):
                direction = (-10, 0)
            elif event.key == pygame.K_RIGHT and direction != (-10, 0):
                direction = (10, 0)
            elif event.key == pygame.K_p:
                print("Game is on pause. Saved.")
                save_score(user_id, level, score)
                running = False

    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    snake.insert(0, head)

    if head == food:
        score += 10
        food = (random.randint(0, WIDTH // 10 - 1) * 10, random.randint(0, HEIGHT // 10 - 1) * 10)
        if score % 50 == 0 and level < max(levels):
            level += 1
            speed = levels[level]["speed"]
            walls = levels[level]["walls"]
    else:
        snake.pop()

    if head in snake[1:] or head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        print("Game Over!")
        save_score(user_id, level, score)
        break

    for wall in walls:
        if pygame.Rect(*wall).collidepoint(head):
            print("Hit the wall!")
            save_score(user_id, level, score)
            running = False
            break

    win.fill((0, 0, 0))
    for seg in snake:
        pygame.draw.rect(win, (0, 255, 0), (*seg, 10, 10))
    pygame.draw.rect(win, (255, 0, 0), (*food, 10, 10))
    for wall in walls:
        pygame.draw.rect(win, (100, 100, 100), wall)

    score_text = font.render(f"Score: {score}  Level: {level}", True, (255, 255, 255))
    win.blit(score_text, (10, 10))
    pygame.display.update()

pygame.quit()
cursor.close()
conn.close()
