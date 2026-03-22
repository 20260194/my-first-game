import pygame
import sys

# 1. 초기화 및 설정
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Wall Collision")

# 2. 색상 및 폰트 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
font = pygame.font.SysFont(None, 30)

# 3. 원의 초기 위치, 속도, 반지름
circle_x = 400
circle_y = 300
speed = 10
radius = 50  # 반지름을 변수로 만들면 벽 계산이 편해요!

clock = pygame.time.Clock()
running = True

# 메인 게임 루프
while running:
    # 1. 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. 키보드 입력 확인
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        circle_x -= speed
    if keys[pygame.K_RIGHT]:
        circle_x += speed
    if keys[pygame.K_UP]:
        circle_y -= speed
    if keys[pygame.K_DOWN]:
        circle_y += speed

    # 3. 벽 충돌 처리 (화면 밖으로 못 나가게 가두기)
    # 가로 벽 체크 (왼쪽, 오른쪽)
    if circle_x < radius:  # 왼쪽 벽
        circle_x = radius
    if circle_x > 800 - radius:  # 오른쪽 벽
        circle_x = 800 - radius

    # 세로 벽 체크 (위쪽, 아래쪽)
    if circle_y < radius:  # 위쪽 벽
        circle_y = radius
    if circle_y > 600 - radius:  # 아래쪽 벽
        circle_y = 600 - radius

    # 4. 화면 그리기
    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (int(circle_x), int(circle_y)), radius)

    # FPS 표시
    fps_text = f"FPS: {int(clock.get_fps())}"
    fps_surface = font.render(fps_text, True, BLACK)
    screen.blit(fps_surface, (10, 10))

    # 5. 화면 업데이트
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()