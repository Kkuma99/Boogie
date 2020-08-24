# https://blog.naver.com/samsjang/220708189400
# https://blog.naver.com/samsjang/220717571305
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time

# 도형에 필요한 변수 선언
## 작은 육면체의 각 꼭짓점
vertices = ((2, 0, 0), (2, 2, 0),
            (0, 2, 0), (0, 0, 0),
            (2, 0, 2), (2, 2, 2),
            (0, 0, 2), (0, 2, 2))
## 큰 육면체의 꼭짓점
vertices2 = ((10, 0, 0), (10, 10, 0),
            (0, 10, 0), (0, 0, 0),
            (10, 0, 10), (10, 10, 10),
            (0, 0, 10), (0, 10, 10))

## 작은 육면체의 면을 칠할 색
### 문제: 4개의 튜플을 모두 같게 하면 두 육면체의 모서리까지 모두 같은색이 되는 이유?
colors = ((1, 1, 0),
          (1, 1, 0),
          (1, 1, 0),
          (1, 1, 1))

## 각 면(꼭짓점끼리의 연결)
surfaces = ((0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6))

## 각 모서리(꼭짓점끼리의 연결)
edges = ((0, 1), (0, 3), (0, 4),
        (2, 1), (2, 3), (2, 7),
        (6, 3), (6, 4), (6, 7),
        (5, 1), (5, 4), (5, 7))



# 기본 세팅
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)  # 투영 양식
glTranslatef(-1, -3, -30)      # 바라보는 위치(좌우, 상하, 전후)



# 육면체를 그림
## 작은 육면체
### 모서리 그리기
glBegin(GL_LINES)       # OpenGL에게 직선을 그릴 것이라는 것을 알려줌
for edge in edges:      # 각 꼭짓점을 직선으로 연결
    for vertex in edge:
        glVertex3fv(vertices[vertex])
glEnd()

### 면 그리기
glBegin(GL_QUADS)       # OpenGL에게 면을 그릴 것이라는 것을 알려줌
for surface in surfaces:
    x = 0
    for vertex in surface:
        glColor3fv(colors[x])
        glVertex3fv(vertices[vertex])
        x += 1
glEnd()


## 큰 육면체
### 모서리 그리기
glBegin(GL_LINES)       # OpenGL에게 직선을 그릴 것이라는 것을 알려줌
for edge in edges:      # 각 꼭짓점을 직선으로 연결
    for vertex in edge:
        glVertex3fv(vertices2[vertex])
glEnd()                 # OpenGL에게 작업이 끝났음을 알려줌



# 화면 표시
pygame.display.flip()       # 화면에 도형을 보여줌
time.sleep(10)       # 1초 기다림



# 자원 해제
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # OpenGL에 쓰인 버퍼를 비움
