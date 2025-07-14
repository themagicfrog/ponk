import time
import board
import analogio
import displayio
import busio
import fourwire
from adafruit_st7735r import ST7735R
import random

slider1 = analogio.AnalogIn(board.GP26)
slider2 = analogio.AnalogIn(board.GP27)

displayio.release_displays()
time.sleep(1)

spi = busio.SPI(clock=board.GP18, MOSI=board.GP19)
display_bus = fourwire.FourWire(
    spi,
    command=board.GP20,
    chip_select=board.GP17,
    reset=board.GP7
)

display = ST7735R(
    display_bus,
    width=128,
    height=160,
    colstart=0,
    rowstart=0,
    rotation=0,
    invert=False,
    bgr=True
)

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160
PADDLE_WIDTH = 3
PADDLE_HEIGHT = 20
BALL_SIZE = 3
PADDLE_SPEED = 2

ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_dx = 2
ball_dy = 1
left_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
right_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
score_left = 0
score_right = 0

def create_game_display():
    main_group = displayio.Group()
    bg_bitmap = displayio.Bitmap(SCREEN_WIDTH, SCREEN_HEIGHT, 256)
    bg_palette = displayio.Palette(256)
    for i in range(256):
        blue_val = i
        purple_val = 255 - i
        bg_palette[i] = (purple_val // 4, 0, blue_val // 4)
    for y in range(SCREEN_HEIGHT):
        color_index = (y * 255) // SCREEN_HEIGHT
        for x in range(SCREEN_WIDTH):
            bg_bitmap[x, y] = color_index
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
    main_group.append(bg_sprite)
    paddle_bitmap = displayio.Bitmap(PADDLE_WIDTH, PADDLE_HEIGHT, 1)
    paddle_palette = displayio.Palette(1)
    paddle_palette[0] = 0xFFFFFF
    for x in range(PADDLE_WIDTH):
        for y in range(PADDLE_HEIGHT):
            paddle_bitmap[x, y] = 0
    left_paddle_sprite = displayio.TileGrid(paddle_bitmap, pixel_shader=paddle_palette, x=5, y=left_paddle_y)
    main_group.append(left_paddle_sprite)
    right_paddle_sprite = displayio.TileGrid(paddle_bitmap, pixel_shader=paddle_palette, x=SCREEN_WIDTH - 5 - PADDLE_WIDTH, y=right_paddle_y)
    main_group.append(right_paddle_sprite)
    ball_bitmap = displayio.Bitmap(BALL_SIZE, BALL_SIZE, 1)
    ball_palette = displayio.Palette(1)
    ball_palette[0] = 0xFF0000
    for x in range(BALL_SIZE):
        for y in range(BALL_SIZE):
            ball_bitmap[x, y] = 0
    ball_sprite = displayio.TileGrid(ball_bitmap, pixel_shader=ball_palette, x=ball_x, y=ball_y)
    main_group.append(ball_sprite)
    line_bitmap = displayio.Bitmap(1, SCREEN_HEIGHT, 1)
    line_palette = displayio.Palette(1)
    line_palette[0] = 0x808080
    for y in range(0, SCREEN_HEIGHT, 4):
        if y < SCREEN_HEIGHT:
            line_bitmap[0, y] = 0
    line_sprite = displayio.TileGrid(line_bitmap, pixel_shader=line_palette, x=SCREEN_WIDTH // 2, y=0)
    main_group.append(line_sprite)
    return main_group, left_paddle_sprite, right_paddle_sprite, ball_sprite

game_group, left_paddle_sprite, right_paddle_sprite, ball_sprite = create_game_display()
display.root_group = game_group

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2
    ball_dx = random.choice([-2, 2])
    ball_dy = random.choice([-1, 1])
    ball_sprite.x = ball_x
    ball_sprite.y = ball_y

def update_paddles():
    global left_paddle_y, right_paddle_y
    left_val = slider1.value
    right_val = slider2.value
    left_paddle_y = int((left_val / 65535.0) * (SCREEN_HEIGHT - PADDLE_HEIGHT))
    right_paddle_y = int((right_val / 65535.0) * (SCREEN_HEIGHT - PADDLE_HEIGHT))
    left_paddle_sprite.y = left_paddle_y
    right_paddle_sprite.y = right_paddle_y

def update_ball():
    global ball_x, ball_y, ball_dx, ball_dy, score_left, score_right
    ball_x += ball_dx
    ball_y += ball_dy
    if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        ball_dy = -ball_dy
    if (ball_x <= 5 + PADDLE_WIDTH and
        ball_x + BALL_SIZE >= 5 and
        ball_y + BALL_SIZE >= left_paddle_y and
        ball_y <= left_paddle_y + PADDLE_HEIGHT):
        ball_dx = abs(ball_dx)
        ball_dy += random.choice([-1, 0, 1])
        if ball_dy > 3:
            ball_dy = 3
        elif ball_dy < -3:
            ball_dy = -3
    elif (ball_x + BALL_SIZE >= SCREEN_WIDTH - 5 - PADDLE_WIDTH and
          ball_x <= SCREEN_WIDTH - 5 and
          ball_y + BALL_SIZE >= right_paddle_y and
          ball_y <= right_paddle_y + PADDLE_HEIGHT):
        ball_dx = -abs(ball_dx)
        ball_dy += random.choice([-1, 0, 1])
        if ball_dy > 3:
            ball_dy = 3
        elif ball_dy < -3:
            ball_dy = -3
    if ball_x < 0:
        score_right += 1
        print(f"Right player scores! Score: {score_left} - {score_right}")
        reset_ball()
        time.sleep(1)
    elif ball_x > SCREEN_WIDTH:
        score_left += 1
        print(f"Left player scores! Score: {score_left} - {score_right}")
        reset_ball()
        time.sleep(1)
    ball_sprite.x = ball_x
    ball_sprite.y = ball_y

print("Starting Pong game!")
print("Left player uses first slider, right player uses second slider")
print("Score: Left - Right")

while True:
    update_paddles()
    update_ball()
    time.sleep(0.05)
