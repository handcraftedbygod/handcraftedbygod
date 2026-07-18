#!/usr/bin/env python3
"""Renders one donut frame and drops it into README.md between marker comments."""
import math
import re
import time

WIDTH, HEIGHT = 60, 22
R1, R2, K2 = 1, 2, 5
K1 = WIDTH * K2 * 3 / (8 * (R1 + R2))
LUMINANCE = ".,-~:;=!*#$@"

START, END = "<!--DONUT_START-->", "<!--DONUT_END-->"


def render_frame(A, B):
    output = [" "] * (WIDTH * HEIGHT)
    zbuffer = [0.0] * (WIDTH * HEIGHT)
    cos_A, sin_A = math.cos(A), math.sin(A)
    cos_B, sin_B = math.cos(B), math.sin(B)

    theta = 0.0
    while theta < 2 * math.pi:
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        phi = 0.0
        while phi < 2 * math.pi:
            cos_p, sin_p = math.cos(phi), math.sin(phi)

            circle_x = R2 + R1 * cos_t
            circle_y = R1 * sin_t

            x = circle_x * (cos_B * cos_p + sin_A * sin_B * sin_p) - circle_y * cos_A * sin_B
            y = circle_x * (sin_B * cos_p - sin_A * cos_B * sin_p) + circle_y * cos_A * cos_B
            z = K2 + cos_A * circle_x * sin_p + circle_y * sin_A
            ooz = 1 / z

            xp = int(WIDTH / 2 + K1 * ooz * x)
            yp = int(HEIGHT / 2 - K1 * ooz * y)

            L = (cos_p * cos_t * sin_B - cos_A * cos_t * sin_p - sin_A * sin_t
                 + cos_B * (cos_A * sin_t - cos_t * sin_A * sin_p))

            idx = xp + yp * WIDTH
            if 0 <= xp < WIDTH and 0 <= yp < HEIGHT and ooz > zbuffer[idx]:
                zbuffer[idx] = ooz
                lum_idx = int(L * 8)
                output[idx] = LUMINANCE[lum_idx] if lum_idx > 0 else " "

            phi += 0.02
        theta += 0.07

    return "\n".join("".join(output[r * WIDTH:(r + 1) * WIDTH]) for r in range(HEIGHT))


def main():
    t = time.time()
    frame = render_frame(t * 0.6 % (2 * math.pi), t * 0.3 % (2 * math.pi))
    block = f"{START}\n```\n{frame}\n```\n{END}"

    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

    updated = re.sub(f"{START}.*?{END}", block, readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    main()
