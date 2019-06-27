import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QTimer
from math import cos, sin, pi, sqrt
from random import randint
from itertools import product

def perspect(dot, p):
    l = len(dot)
    return [dot[i] * p / dot[-1:][0] for i in range(l)]

class Figure():
    def __init__(self, c, c_c,  dots_and_bindings, max_v, max_a, a_change, bindings_width, connected = []):
        self.dots, self.bindings, self.connected = dots_and_bindings[0], dots_and_bindings[1], connected
        self.c, self.c_c = c, c_c
        self.n = len(self.c)
        self.C = sum([z for z in range(self.n)])
        self.v = [0 for i in range(self.C)]
        self.a = [0 for i in range(self.C)]
        self.max_v, self.max_a, self.a_change = max_v, max_a, a_change
        self.bindings_width = bindings_width
    def rotate(self, angles):
        for dot in self.dots:
            z = 0
            for i in range(self.n):
                for j in range(self.n - i - 1):
                    c, s = cos(angles[z]), sin(angles[z])
                    z += 1
                    dot[i], dot[i + j + 1] = dot[i]*c - dot[i + j + 1]*s, dot[i]*s + dot[i + j + 1]*c
    def draw(self, painter):
        pen = QPen(Qt.white, self.bindings_width, Qt.SolidLine)
        painter.setPen(pen)
        for binding in self.bindings:
            dot1, dot2 = [(self.dots[binding[0]][i] + self.c[i]) for i in range(self.n)], [(self.dots[binding[1]][i] + self.c[i]) for i in range(self.n)]
            if PERSPECT:
                dot1, dot2 = perspect(dot1, 470), perspect(dot2, 470)
            painter.drawLine(dot1[0] + self.c_c[0], dot1[1] + self.c_c[1], dot2[0] + self.c_c[0], dot2[1] + self.c_c[1])
        if self.connected:
            for f in self.connected: f[0].draw(painter)
    def accelerate(self):
        for i in range(self.n):
             if -self.max_v < self.v[i] + self.a[i] < self.max_v: self.v[i] += self.a[i]
    def move(self, recursive):
        for i in range(self.n):
            if randint(0,1) and self.a[i] < self.max_a : self.a[i] += self.a_change
            elif self.a[i] > -self.max_a: self.a[i] -= self.a_change
        self.accelerate()
        self.rotate([self.v[i]*pi/100 for i in range(self.C)])
        if recursive and self.connected:
            for f in self.connected:
                f[0].move(True)
                f[0].c = [self.dots[f[1]][i] + self.c[i] for i in range(self.n)]
    def connect_to_self(self, figure, a0, i, k):
        a0 /= k
        for j in range(len(self.dots)): self.connected.append([Figure([self.dots[j][i] + self.c[i] for i in range(self.n)], [self.c_c[i] for i in range(self.n)], figure(a0, self.n), self.max_v, self.max_a, self.a_change, self.bindings_width/(1.17/(1.8/k)), []), j])
        i -= 1
        if i:
            for f in self.connected: f[0].connect_to_self(figure, a0, i, k)

def Cube(a, n = 3):
    m1, m2 = list(map(list, list(product([-a/2, a/2], repeat = n)))), []
    for i in range(len(m1)):
        for j in range(len(m1) - i):
            d = 0
            for z in range(n):
                if m1[i][z] != m1[j + i][z]: d += 1
                if d == 2: break
            if d == 1: m2.append([i, j + i])
    return [m1, m2]

def Tetrahedron(a, n = 3):
    x0 = (sqrt(2*n)-a)/n
    dc = -(a-x0)/(2*(n+1))
    m1 = [[dc for j in range (i)] + [a + dc] + [dc for j in range(n-i-1)] for i in range(n)] + [[x0+dc for i in range(n)]]
    m2 = [[i, i + j] for i in range(n + 1) for j in range(n + 1 - i)]
    return [m1, m2]

resx, resy = int(input("Horizontal resolution: ")), int(input("Vertical resolution: "))
figure = [Tetrahedron, Cube][int(input('Figure:\n1 - Tetrahedron\n2 - Cube\n')) - 1]
PERSPECT = int(input("Enable perspective (increase understability, decrease perfomance): "))

class drawer(QWidget):
    def __init__(self):
        super().__init__()
        N = int(input("Number of space dimensions: "))
        self.figures = [Figure([0 for i in range(N - 1)] + [-650], [resx / 2, resy / 2] + [0 for i in range(N - 2)], figure(resx/(4 + 1.2*[Tetrahedron, Cube].index(figure)), N), 0.7, 0.9, 0.05, 2)]
        if int(input("Fractalize (0 / 1) ? ")): self.figures[0].connect_to_self(figure, resx/5, int(input("Iterations number (1-2 recommended): ")), 2.5)
        self.initiation()
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_timeout)
        self.timer.start(10)
        self.update()
    def process_timeout(self):
        for figure in self.figures: figure.move(True)
        self.update()
    def initiation(self):
        self.setGeometry(0, 0, 1600, 1400)
        self.setWindowTitle('Test')
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
        self.show()
    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        for figure in self.figures: figure.draw(painter)
        painter.end()
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = drawer()
    sys.exit(app.exec_())
