import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)  # Camara web
cap.set(3, 1280)  # Ancho de la camara
cap.set(4, 720)  # Alto de la camara

detector = HandDetector(detectionCon=0.8, maxHands=1)  # Detector de manos


class SnakeGameClass:
    # Inicializar la serpiente
    def __init__(self, pathFood):  # Constructor
        self.points = []  # Todos los puntos de la serpiente
        self.lengths = []  # Distancia entre cada punto
        self. currentLength = 0  # Longitud total de la serpiente
        self.allowedLength = 150  # Longitud total permitida
        self.previousHead = 0, 0  # Punto de la cabeza anterior

        self.imgFood = cv2.imread(
            pathFood, cv2.IMREAD_UNCHANGED)  # Imagen de la comida
        self.hFood, self.wFood, _ = self.imgFood.shape  # Dimensiones de la comida
        self.foodPoint = 0, 0  # Punto de la comida
        self.randomFoodLocation()  # Ubicación aleatoria de la comida

        self.score = 0  # Puntuación
        self.gameOver = False  # Estado del juego

    # Generar una ubicación aleatoria para la comida
    def randomFoodLocation(self):
        self.foodPoint = random.randint(
            100, 1000), random.randint(100, 600)  # Punto aleatorio

    # Actualizar la serpiente
    def update(self, imgMain, currentHead):

        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300, 400],
                               scale=7, thickness=5, offset=20)  # Texto de Game Over
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [300, 550],
                               scale=7, thickness=5, offset=20)  # Puntuación

        else:
            px, py = self.previousHead  # Punto de la cabeza anterior
            cx, cy = currentHead  # Punto de la cabeza actual

            self.points.append([cx, cy])  # Agregar punto a la serpiente
            distance = math.hypot(cx - px, cy - py)  # Distancia entre puntos
            self.lengths.append(distance)  # Agregar distancia a la serpiente
            self.currentLength += distance  # Longitud total de la serpiente
            self.previousHead = cx, cy  # Actualizar punto de la cabeza anterior

            # Reduccion de la longitud de la serpiente
            if self.currentLength > self.allowedLength:  # Si la longitud total es mayor a la longitud permitida
                # Recorrer la lista de distancias
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length  # Restar la distancia a la longitud total
                    self.lengths.pop(i)  # Eliminar la distancia de la lista
                    self.points.pop(i)  # Eliminar el punto de la serpiente
                    if self.currentLength < self.allowedLength:  # Si la longitud total es menor a la longitud permitida
                        break  # Salir del bucle

            # Comprobar si la serpiente ha comido la comida
            rx, ry = self.foodPoint  # Punto de la comida
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:  # Si la cabeza de la serpiente esta en la comida
                self.randomFoodLocation()  # Ubicación aleatoria de la comida
                self.allowedLength += 50  # Aumentar la longitud permitida
                self.score += 1  # Aumentar la puntuación
                print(self.score)  # Imprimir la puntuación

            # Dibujar serpiente
            if self.points:  # Si hay puntos en la serpiente
                for i, point in enumerate(self.points):  # Recorrer los puntos
                    if i != 0:  # Si no es el primer punto
                        cv2.line(
                            imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)  # Dibujar la serpiente
                cv2.circle(imgMain, self.points[-1],
                           20, (0, 255, 0), cv2.FILLED)  # Dibujar la cabeza de la serpiente

            # Dibujar comida
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

            cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 80],
                               scale=3, thickness=3, offset=10)

            # Comprobar colisiones
            # Puntos de la serpiente
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))  # Redimensionar los puntos
            # Dibujar la serpiente
            cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
            minDist = cv2.pointPolygonTest(
                pts, (cx, cy), True)  # Distancia entre puntos

            if -1 <= minDist <= 1: # Si la distancia es menor o igual a 1
                print("Hit")
                self.gameOver = True # Game Over
                self.points = []  # all points of the snake
                self.lengths = []  # distance between each point
                self.currentLength = 0  # total length of the snake
                self.allowedLength = 150  # total allowed Length
                self.previousHead = 0, 0  # previous head point
                self.randomFoodLocation() # random food location

        return imgMain # Devolver la imagen


game = SnakeGameClass("Donut.png")  # Instancia de la clase SnakeGameClass

while True:
    success, img = cap.read() # Leer la imagen de la camara
    img = cv2.flip(img, 1) # Voltear la imagen
    hands, img = detector.findHands(img, flipType=False) # Detectar manos

    if hands: # Si hay manos
        lmList = hands[0]['lmList'] # Lista de puntos de la mano
        pointIndex = lmList[8][0:2] # Punto de la punta del dedo indice
        img = game.update(img, pointIndex) # Actualizar el juego
    cv2.imshow("Image", img) # Mostrar la imagen
    key = cv2.waitKey(1) # Esperar una tecla
    if key == ord('r'): # Si se presiona la tecla 'r'
        game.gameOver = False # Reiniciar el juego
