import pygame
import math

# 1. 초기화 및 창 설정
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Collision Comparison: Circle vs AABB vs OBB")
clock = pygame.time.Clock()

# 폰트 설정 (UI용)
font = pygame.font.SysFont("arial", 24, bold=True)

# 색상 정의
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def get_obb_vertices(center, size, angle):
    w, h = size[0] / 2, size[1] / 2
    angle_rad = math.radians(-angle)
    vertices = []
    for dx, dy in [(-w, -h), (w, -h), (w, h), (-w, h)]:
        rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        vertices.append(pygame.Vector2(center.x + rx, center.y + ry))
    return vertices

def sat_collision(poly1, poly2):
    polygons = [poly1, poly2]
    for i in range(len(polygons)):
        poly = polygons[i]
        for j in range(len(poly)):
            p1, p2 = poly[j], poly[(j + 1) % len(poly)]
            edge = p2 - p1
            normal = pygame.Vector2(-edge.y, edge.x).normalize()
            
            min1 = max1 = poly1[0].dot(normal)
            for p in poly1[1:]:
                proj = p.dot(normal)
                min1, max1 = min(min1, proj), max(max1, proj)
            
            min2 = max2 = poly2[0].dot(normal)
            for p in poly2[1:]:
                proj = p.dot(normal)
                min2, max2 = min(min2, proj), max(max2, proj)
                
            if max1 < min2 or max2 < min1:
                return False
    return True

# 오브젝트 설정
static_size = (120, 120)
static_surface = pygame.Surface(static_size, pygame.SRCALPHA)
static_surface.fill(GRAY)
static_pos = pygame.Vector2(400, 300)
static_angle = 0

moving_size = (80, 80)
moving_rect = pygame.Rect(100, 100, *moving_size)
move_speed = 5

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 로직: 이동 및 회전
    keys = pygame.key.get_pressed()
    rotation_speed = 7 if keys[pygame.K_z] else 1.5
    static_angle += rotation_speed

    if keys[pygame.K_LEFT]:  moving_rect.x -= move_speed
    if keys[pygame.K_RIGHT]: moving_rect.x += move_speed
    if keys[pygame.K_UP]:    moving_rect.y -= move_speed
    if keys[pygame.K_DOWN]:  moving_rect.y += move_speed

    # --- 충돌 계산 ---
    # 1. 원형 충돌 (Circle)
    dist = static_pos.distance_to(pygame.Vector2(moving_rect.center))
    circle_hit = dist < (static_size[0]//2 + moving_rect.width//2)

    # 2. OBB 계산 및 SAT 충돌
    static_poly = get_obb_vertices(static_pos, static_size, static_angle)
    moving_poly = get_obb_vertices(pygame.Vector2(moving_rect.center), moving_size, 0)
    obb_hit = sat_collision(static_poly, moving_poly)

    # 3. AABB 충돌 (Pygame 기본 제공 기능 활용)
    # 회전된 사각형을 감싸는 빨간 사각형(new_rect)을 미리 구함
    rotated_image = pygame.transform.rotate(static_surface, static_angle)
    static_aabb = rotated_image.get_rect(center=static_pos)
    aabb_hit = static_aabb.colliderect(moving_rect)

    # --- 그리기 ---
    screen.fill(WHITE)

    # 오브젝트 본체
    screen.blit(rotated_image, static_aabb.topleft)
    pygame.draw.rect(screen, GRAY, moving_rect)

    # 경계 상자 시각화
    pygame.draw.circle(screen, BLUE, static_pos, static_size[0]//2, 2) # 원형 (파란색)
    pygame.draw.circle(screen, BLUE, moving_rect.center, moving_rect.width//2, 2)
    
    pygame.draw.rect(screen, RED, static_aabb, 2) # AABB (빨간색)
    pygame.draw.rect(screen, RED, moving_rect, 2)
    
    pygame.draw.polygon(screen, GREEN, static_poly, 2) # OBB (초록색)
    pygame.draw.polygon(screen, GREEN, moving_poly, 2)

    # --- UI 표시 (왼쪽 상단) ---
    texts = [
        (f"Circle: {'HIT' if circle_hit else 'SAFE'}", BLUE),
        (f"AABB: {'HIT' if aabb_hit else 'SAFE'}", RED),
        (f"OBB: {'HIT' if obb_hit else 'SAFE'}", GREEN)
    ]
    
    for i, (text, color) in enumerate(texts):
        surf = font.render(text, True, color)
        screen.blit(surf, (20, 20 + i * 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()