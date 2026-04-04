import pygame
import random
import sys
import math

# --- 초기화 ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - Mission Clear")
clock = pygame.time.Clock()

# --- 색상 ---
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (20, 20, 40)
BLUE, RED, YELLOW, GREEN = (50, 150, 255), (220, 50, 50), (240, 220, 0), (50, 220, 80)
PURPLE, ORANGE, CYAN = (150, 50, 255), (255, 165, 0), (0, 255, 255)

font = pygame.font.SysFont("malgungothic", 25)
font_big = pygame.font.SysFont("malgungothic", 70)
font_mid = pygame.font.SysFont("malgungothic", 40)

particles = [] 
def create_explosion(x, y, color, count=15):
    for _ in range(count):
        particles.append([x, y, random.uniform(-5, 5), random.uniform(-5, 5), random.randint(15, 35), color])

def show_end_screen(text, color, score):
    """게임 오버 또는 클리어 시 선택 화면을 보여주는 함수"""
    while True:
        screen.fill(BLACK)
        title = font_big.render(text, True, color)
        score_label = font_mid.render(f"Final Score: {score}", True, WHITE)
        retry_label = font.render("Press 'R' to Restart", True, GREEN)
        quit_label = font.render("Press 'Q' to Quit", True, RED)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        screen.blit(score_label, (WIDTH//2 - score_label.get_width()//2, HEIGHT//2 - 20))
        screen.blit(retry_label, (WIDTH//2 - retry_label.get_width()//2, HEIGHT//2 + 60))
        screen.blit(quit_label, (WIDTH//2 - quit_label.get_width()//2, HEIGHT//2 + 100))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # 다시 시작
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()

def main():
    player = pygame.Rect(WIDTH//2 - 20, HEIGHT - 70, 40, 40)
    bullets, enemy_bullets, enemies, items = [], [], [], []
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)] for _ in range(60)]
    
    score, lives, power = 0, 3, 1
    shoot_cd, spawn_timer, invincible = 0, 0, 0
    
    boss_active, boss_hp, boss_max_hp = False, 500, 500
    boss_rect = pygame.Rect(WIDTH//2 - 75, 70, 150, 80)
    boss_speed, boss_timer, laser_timer = 2, 0, 0

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= 7
        if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += 7
        if keys[pygame.K_UP] and player.top > 0: player.y -= 7
        if keys[pygame.K_DOWN] and player.bottom < HEIGHT: player.y += 7

        shoot_cd -= 1
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            angle_step = 5
            start_angle = -(power - 1) * angle_step / 2
            for i in range(power):
                angle = start_angle + (i * angle_step)
                rad = math.radians(angle - 90)
                bullets.append([pygame.Rect(player.centerx-3, player.top, 6, 14), math.cos(rad)*12, math.sin(rad)*12])
            shoot_cd = 12

        # 보스 등장 조건
        if score >= 1000 and not boss_active and boss_hp > 0:
            boss_active = True
            enemies.clear()

        # 무적 및 충돌 판정
        if invincible > 0: invincible -= 1
        else:
            hit = False
            for en in enemies:
                if player.colliderect(en[0]): hit = True; enemies.remove(en); break
            if not hit and boss_active and player.colliderect(boss_rect): hit = True
            for eb in enemy_bullets[:]:
                if player.colliderect(eb[0]): hit = True; enemy_bullets.remove(eb); break
            if not hit and boss_active and 0 < laser_timer < 30:
                if player.colliderect(pygame.Rect(boss_rect.centerx - 25, boss_rect.bottom, 50, HEIGHT)): hit = True

            if hit:
                lives -= 1
                power = max(1, power - 1)
                invincible = 90
                create_explosion(player.centerx, player.centery, RED, 30)
                if lives <= 0:
                    if show_end_screen("GAME OVER", RED, score): return # 다시 시작
                    else: pygame.quit(); sys.exit()

        # 적/보스 로직
        if not boss_active:
            spawn_timer += 1
            if spawn_timer >= 45:
                spawn_timer = 0
                hp_lvl = 1 + (score // 500)
                if random.random() < 0.03: enemies.append([pygame.Rect(random.randint(50, WIDTH-100), -50, 50, 50), hp_lvl*8, 'elite', 0])
                else: enemies.append([pygame.Rect(random.randint(0, WIDTH-36), -36, 36, 36), hp_lvl, 'normal', 0])
        else:
            boss_timer += 1
            if laser_timer > 0: laser_timer -= 1
            elif boss_timer % 300 == 0: laser_timer = 90
            
            boss_rect.x += boss_speed
            if boss_rect.right >= WIDTH or boss_rect.left <= 0: boss_speed *= -1
            if boss_timer % 180 == 0: enemy_bullets.append([pygame.Rect(boss_rect.centerx-15, boss_rect.bottom, 30, 30), 0, 3, ORANGE, 'big'])
            if boss_timer % 60 == 0:
                dist = math.hypot(player.centerx-boss_rect.centerx, player.centery-boss_rect.centery)
                if dist != 0: enemy_bullets.append([pygame.Rect(boss_rect.centerx-5, boss_rect.bottom, 12, 12), (player.centerx-boss_rect.centerx)/dist*6, (player.centery-boss_rect.centery)/dist*6, PURPLE, 'normal'])

        # 이동 및 총알 로직
        for en in enemies[:]:
            if en[2] == 'elite':
                en[3] += 1
                if en[3] % 100 == 0:
                    create_explosion(en[0].centerx, en[0].centery, CYAN, 20)
                    en[0].x, en[0].y = random.randint(50, WIDTH-100), random.randint(50, 250)
                    for a in range(0, 360, 60):
                        rad = math.radians(a)
                        enemy_bullets.append([pygame.Rect(en[0].centerx, en[0].centery, 8, 8), math.cos(rad)*4, math.sin(rad)*4, CYAN, 'normal'])
            else: en[0].y += 3.5
            if en[0].top > HEIGHT: enemies.remove(en)

        for eb in enemy_bullets[:]:
            eb[0].x += eb[1]; eb[0].y += eb[2]
            if eb[4] == 'big' and eb[0].centery > HEIGHT // 2:
                for a in range(0, 360, 45):
                    rad = math.radians(a)
                    enemy_bullets.append([pygame.Rect(eb[0].centerx, eb[0].centery, 10, 10), math.cos(rad)*5, math.sin(rad)*5, YELLOW, 'normal'])
                enemy_bullets.remove(eb); continue
            if not screen.get_rect().colliderect(eb[0]): enemy_bullets.remove(eb)

        for b in bullets[:]:
            b[0].x += b[1]; b[0].y += b[2]
            if not screen.get_rect().colliderect(b[0]): bullets.remove(b)
            else:
                for en in enemies[:]:
                    if b[0].colliderect(en[0]):
                        en[1] -= 1
                        if b in bullets: bullets.remove(b)
                        if en[1] <= 0:
                            create_explosion(en[0].centerx, en[0].centery, CYAN if en[2]=='elite' else RED)
                            if en[2] == 'elite' or random.random() < 0.15: items.append(pygame.Rect(en[0].centerx-12, en[0].centery-12, 24, 24))
                            score += 200 if en[2] == 'elite' else 10; enemies.remove(en)
                        break
                if boss_active and b in bullets and b[0].colliderect(boss_rect):
                    bullets.remove(b); boss_hp -= 1
                    if boss_hp <= 0:
                        create_explosion(boss_rect.centerx, boss_rect.centery, PURPLE, 100)
                        if show_end_screen("MISSION CLEAR", CYAN, score + 5000): return
                        else: pygame.quit(); sys.exit()

        for it in items[:]:
            it.y += 3
            if it.colliderect(player): power = min(power + 1, 5); create_explosion(it.centerx, it.centery, GREEN, 20); items.remove(it)
            elif it.top > HEIGHT: items.remove(it)

        # 5. 그리기
        screen.fill(GRAY)
        for s in stars: pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2]); s[1] = (s[1] + 1.5) % HEIGHT
        if boss_active and laser_timer > 0:
            if laser_timer >= 30: pygame.draw.rect(screen, (80, 0, 0), (boss_rect.centerx-2, boss_rect.bottom, 4, HEIGHT))
            else: 
                pygame.draw.rect(screen, RED, (boss_rect.centerx-25, boss_rect.bottom, 50, HEIGHT))
                pygame.draw.rect(screen, WHITE, (boss_rect.centerx-12, boss_rect.bottom, 24, HEIGHT))

        for b in bullets: pygame.draw.rect(screen, YELLOW, b[0])
        for eb in enemy_bullets: pygame.draw.ellipse(screen, eb[3], eb[0])
        for en in enemies:
            if en[2] == 'elite': pygame.draw.rect(screen, CYAN, en[0], border_radius=8)
            else: pygame.draw.polygon(screen, RED, [(en[0].centerx, en[0].bottom), (en[0].left, en[0].top), (en[0].right, en[0].top)])
        for it in items: pygame.draw.circle(screen, GREEN, it.center, 12)
        if boss_active:
            pygame.draw.rect(screen, PURPLE, boss_rect, border_radius=15)
            pygame.draw.rect(screen, BLACK, (100, 30, 600, 10))
            pygame.draw.rect(screen, RED, (100, 30, 600 * (max(0, boss_hp)/boss_max_hp), 10))

        for p in particles[:]:
            p[0]+=p[2]; p[1]+=p[3]; p[4]-=1; pygame.draw.circle(screen, p[5], (int(p[0]), int(p[1])), max(1, int(p[4]/6)))
            if p[4]<=0: particles.remove(p)

        if (invincible // 10) % 2 == 0:
            pygame.draw.polygon(screen, BLUE, [(player.centerx, player.top), (player.left, player.bottom), (player.right, player.bottom)])

        screen.blit(font.render(f"Score: {score}  Lives: {lives}  Power: {power}", True, WHITE), (10, 10))
        pygame.display.flip()

if __name__ == "__main__":
    while True: main()