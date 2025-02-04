import pygame
import sqlite3
import random
import os

pygame.init()

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Кооперативная арена")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 36)

# --- Классы игры ---

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Попытка загрузить изображение текстуры разрушенных домов
        try:
            image = pygame.image.load("block.jpg").convert_alpha()
            self.image = pygame.transform.scale(image, (width, height))
        except Exception as e:
            print("Ошибка загрузки текстуры блоков, используется заливка:", e)
            self.image = pygame.Surface((width, height))
            self.image.fill((128, 128, 128))
        self.rect = self.image.get_rect(topleft=(x, y))

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, image_file, fallback_color, controls):
        super().__init__()
        # Пытаемся загрузить изображение персонажа
        try:
            image = pygame.image.load(image_file).convert_alpha()
            self.image = pygame.transform.scale(image, (50, 50))
        except Exception as e:
            print(f"Ошибка загрузки изображения {image_file}, используется заливка:", e)
            self.image = pygame.Surface((50, 50))
            self.image.fill(fallback_color)
        self.rect = self.image.get_rect()
        self.health = 100
        self.resources = 5
        self.controls = controls
        self.kills = 0  # Счётчик убийств игрока

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[self.controls['UP']]:
            dy = -5
        if keys[self.controls['DOWN']]:
            dy = 5
        if keys[self.controls['LEFT']]:
            dx = -5
        if keys[self.controls['RIGHT']]:
            dx = 5

        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, blocks):
            self.rect.x -= dx
        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, blocks):
            self.rect.y -= dy

    def shoot(self):
        projectile = Projectile(self.rect.centerx, self.rect.top, self)
        all_sprites.add(projectile)
        projectiles.add(projectile)

    def draw_health(self):
        if self.health > 0:
            health_ratio = self.health / 100
            pygame.draw.rect(screen, (255, 0, 0), (self.rect.centerx - 25, self.rect.top - 10, 50, 5))
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.centerx - 25, self.rect.top - 10, 50 * health_ratio, 5))

    def is_alive(self):
        return self.health > 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Пытаемся загрузить изображение врага
        try:
            image = pygame.image.load("2025-02-04_00-51-13.png").convert_alpha()
            self.image = pygame.transform.scale(image, (40, 40))
        except Exception as e:
            print("Ошибка загрузки изображения enemy.png, используется заливка:", e)
            self.image = pygame.Surface((40, 40))
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 40)
        self.rect.y = random.randint(-100, 0)
        self.health = 50
        self.last_attack_time = pygame.time.get_ticks()

    def update(self):
        def distance_squared(rect1, rect2):
            dx = rect1.centerx - rect2.centerx
            dy = rect1.centery - rect2.centery
            return dx ** 2 + dy ** 2

        target = min(
            (player1, player2),
            key=lambda p: distance_squared(self.rect, p.rect) if p.is_alive() else float('inf')
        )

        if target.is_alive():
            if self.rect.x < target.rect.x:
                self.rect.x += 2
            elif self.rect.x > target.rect.x:
                self.rect.x -= 2
            if self.rect.y < target.rect.y:
                self.rect.y += 2
            elif self.rect.y > target.rect.y:
                self.rect.y -= 2
        if pygame.sprite.spritecollideany(self, blocks):
            self.rect.x -= 2
            self.rect.y -= 2
        if pygame.sprite.collide_rect(self, target):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > 1000:
                target.health -= 10
                self.last_attack_time = current_time

class Boss(Enemy):
    def __init__(self):
        # Вызываем родительский конструктор, затем переопределяем изображение
        super().__init__()
        try:
            image = pygame.image.load("k.png").convert_alpha()
            self.image = pygame.transform.scale(image, (80, 80))
        except Exception as e:
            print("Ошибка загрузки изображения boss.png, используется заливка:", e)
            self.image = pygame.Surface((80, 80))
            self.image.fill((255, 128, 0))
        self.health = 300
        self.last_attack_time = pygame.time.get_ticks()

    def draw_health(self):
        health_ratio = self.health / 300
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH // 2 - 150, 20, 300, 20))
        pygame.draw.rect(screen, (0, 255, 0), (WIDTH // 2 - 150, 20, 300 * health_ratio, 20))

    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > 2000:
            target = random.choice([player1, player2])
            if target.is_alive():
                target.health -= 20
            self.last_attack_time = current_time

class BlackHole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill((0, 0, 0))
        pygame.draw.circle(self.image, (50, 0, 50), (50, 50), 50)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        for player in [player1, player2]:
            if player.is_alive() and pygame.sprite.collide_rect(self, player):
                player.kill()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, shooter):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.shooter = shooter  # Хранит ссылку на игрока, который сделал выстрел

    def update(self):
        self.rect.y -= 7
        if self.rect.bottom < 0 or pygame.sprite.spritecollideany(self, blocks):
            self.kill()

# --- Функции игры и меню ---

def game():
    global all_sprites, projectiles, blocks, player1, player2, portal, wave, enemies, boss
    wave = 1
    portal = None
    boss = None

    # Загружаем фоновое изображение для игры
    try:
        game_bg = pygame.image.load("о.jpg").convert()
        game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))
    except Exception as e:
        print("Фоновое изображение игры не найдено, используется plain background.", e)
        game_bg = None

    # Управление игроков
    player1_controls = {'UP': pygame.K_w, 'DOWN': pygame.K_s, 'LEFT': pygame.K_a, 'RIGHT': pygame.K_d, 'SHOOT': pygame.K_SPACE}
    player2_controls = {'UP': pygame.K_UP, 'DOWN': pygame.K_DOWN, 'LEFT': pygame.K_LEFT, 'RIGHT': pygame.K_RIGHT, 'SHOOT': pygame.K_RETURN}

    def setup_wave(wave):
        global all_sprites, blocks, player1, player2
        all_sprites = pygame.sprite.Group()
        blocks = pygame.sprite.Group()
        # Передаем имя файла изображения и запасной цвет на случай ошибки
        player1 = Player("player1.png", (0, 255, 0), player1_controls)
        player2 = Player("player2.png", (0, 0, 255), player2_controls)
        # Устанавливаем стартовые позиции игроков
        player1.rect.center = (WIDTH // 4, HEIGHT - 100)
        player2.rect.center = (WIDTH * 3 // 4, HEIGHT - 100)
        all_sprites.add(player1, player2)
        enemies_group = pygame.sprite.Group()
        for _ in range(wave * 5):
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies_group.add(enemy)
        for i in range(5):
            block = Block(random.randint(0, WIDTH - 100), random.randint(0, HEIGHT - 100), 100, 50)
            blocks.add(block)
            all_sprites.add(block)
        return enemies_group

    enemies = setup_wave(wave)
    projectiles = pygame.sprite.Group()
    running = True
    restart_game = False
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if not game_over:
            all_sprites.update()
            keys = pygame.key.get_pressed()
            if keys[player1.controls['SHOOT']]:
                player1.shoot()
            if keys[player2.controls['SHOOT']]:
                player2.shoot()

            # Обработка столкновений снарядов с врагами
            for projectile in projectiles:
                hit_enemies = pygame.sprite.spritecollide(projectile, enemies, False)
                for enemy in hit_enemies:
                    enemy.health -= 10
                    projectile.kill()
                    if enemy.health <= 0:
                        enemy.kill()
                        projectile.shooter.kills += 1

            if not player1.is_alive():
                player1.kill()
            if not player2.is_alive():
                player2.kill()
            if not player1.is_alive() and not player2.is_alive():
                game_over = True

            # Если враги побеждены – создаём портал или вызываем босса
            if len(enemies) == 0:
                if wave < 5 and portal is None:
                    portal = Portal(WIDTH // 2, HEIGHT // 2)
                    all_sprites.add(portal)
                elif wave == 5 and boss is None:
                    boss = Boss()
                    all_sprites.add(boss)
                    enemies.add(boss)

            if portal and (pygame.sprite.collide_rect(player1, portal) or pygame.sprite.collide_rect(player2, portal)):
                portal.kill()
                portal = None
                wave += 1
                enemies = setup_wave(wave)

            # Отрисовка: сначала фон, затем все игровые объекты
            if game_bg:
                screen.blit(game_bg, (0, 0))
            else:
                screen.fill((0, 0, 0))
            all_sprites.draw(screen)
            if player1.is_alive():
                player1.draw_health()
            if player2.is_alive():
                player2.draw_health()
            if boss and boss.alive():
                boss.draw_health()

            pygame.display.flip()
            clock.tick(60)

        else:
            # Экран Game Over
            screen.fill((0, 0, 0))
            game_over_text = font.render("Game Over", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20))
            screen.blit(game_over_text, text_rect)

            restart_text = button_font.render("Нажмите 'R', чтобы играть заново", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 30))
            screen.blit(restart_text, restart_rect)

            pygame.display.flip()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                restart_game = True
                running = False

    # Сохранение результата в базу данных
    try:
        conn = sqlite3.connect("highscores.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, wave INTEGER, kills1 INTEGER, kills2 INTEGER)")
        current_wave = wave - 1
        p1_kills = getattr(player1, 'kills', 0)
        p2_kills = getattr(player2, 'kills', 0)
        c.execute("INSERT INTO scores (wave, kills1, kills2) VALUES (?, ?, ?)", (current_wave, p1_kills, p2_kills))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error saving score:", e)

    if restart_game:
        game()
    else:
        main_menu()

def show_best_score():
    try:
        conn = sqlite3.connect("highscores.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, wave INTEGER, kills1 INTEGER, kills2 INTEGER)")
        c.execute("SELECT wave, kills1, kills2 FROM scores ORDER BY wave DESC, (kills1 + kills2) DESC LIMIT 1")
        result = c.fetchone()
        conn.close()
    except Exception as e:
        print("Error loading score:", e)
        result = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    running = False

        screen.fill((0, 0, 0))
        title = font.render("Лучший счёт", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title, title_rect)

        if result:
            wave_score, kills1, kills2 = result
            score_text = button_font.render(f"Волны: {wave_score}, Убийств P1: {kills1}, Убийств P2: {kills2}", True, (255, 255, 255))
        else:
            score_text = button_font.render("Нет записей", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(score_text, score_rect)

        instruction_text = button_font.render("Нажмите Enter или Esc, чтобы вернуться", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(instruction_text, instruction_rect)

        pygame.display.flip()
        clock.tick(60)

def battlefield_description():
    """
    Экран с описанием поля битвы, где сообщается, что действие происходит
    на заброшенной территории с остатками разрушенных домов.
    """
    running = True
    description_lines = [
        "Битва проходит на заброшенной территории,",
        "где остатки старых разрушенных домов",
        "создают укрытия для бойцов.",
        "Осторожно – за каждым углом может скрываться опасность!",
    ]
    start_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 150, 300, 50)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button_rect.collidepoint(mouse_pos):
                    running = False

        screen.fill((20, 20, 20))
        title = font.render("Поле битвы", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title, title_rect)

        for i, line in enumerate(description_lines):
            line_surf = button_font.render(line, True, (200, 200, 200))
            line_rect = line_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50 + i * 40))
            screen.blit(line_surf, line_rect)

        pygame.draw.rect(screen, (255, 255, 255), start_button_rect)
        button_text = button_font.render("Начать битву", True, (0, 0, 0))
        button_text_rect = button_text.get_rect(center=start_button_rect.center)
        screen.blit(button_text, button_text_rect)

        pygame.display.flip()
        clock.tick(60)

def main_menu():
    try:
        bg = pygame.image.load("fon.jpg")
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except Exception as e:
        print("Background image not found, using plain background.", e)
        bg = None

    running = True
    while running:
        play_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
        score_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        exit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if play_button_rect.collidepoint(mouse_pos):
                    battlefield_description()
                    game()
                elif score_button_rect.collidepoint(mouse_pos):
                    show_best_score()
                elif exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    return

        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((0, 0, 0))

        title_text = font.render("Кооперативная арена", True, (000, 000, 000))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_text, title_rect)

        pygame.draw.rect(screen, (255, 255, 255), play_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), score_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), exit_button_rect)

        play_text = button_font.render("Играть", True, (0, 0, 0))
        score_text = button_font.render("Лучший счёт", True, (0, 0, 0))
        exit_text = button_font.render("Выйти", True, (0, 0, 0))
        screen.blit(play_text, play_text.get_rect(center=play_button_rect.center))
        screen.blit(score_text, score_text.get_rect(center=score_button_rect.center))
        screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()