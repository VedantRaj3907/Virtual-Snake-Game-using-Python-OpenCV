######################################################################################
# Importing Required Libraries(cvzone,cv2,numpy)
import math
import random
import cvzone as cvz
import cv2 as cv
import numpy as np
from cvzone.HandTrackingModule import HandDetector

######################################################################################
#Capturing Video
cap = cv.VideoCapture(0)
cap.set(3, 1280)  # Setting the Size of Screen
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)  # For setting Maximum Hands

######################################################################################
class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # All points of snake
        self.lengths = []  # Distance between each points
        self.currentLength = 0  # Total length off Snake
        self.allowedLength = 300  # Total allowed Length
        self.previousHead = 0, 0  # previous Head Point

        self.imgFood = cv.imread(pathFood, cv.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()
        self.score = 0
        self.gameOver = False

    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, imgMain, currentHead):

        if self.gameOver:
            cvz.putTextRect(imgMain, "Game Over", [300, 400], scale=7, thickness=5, offset=20)
            cvz.putTextRect(imgMain, f'Your Score: {self.score}', [300, 550], scale=7, thickness=5, offset=20)

        else:
            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # Length Reduction
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # Check if snake ate the Food
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and ry - self.wFood < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                print(self.score)

            # Draw Snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                cv.circle(imgMain, self.points[-1], 20, (200, 0, 200), cv.FILLED)

            # Draw Food

            imgMain = cvz.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))

            cvz.putTextRect(imgMain, f'Score: {self.score}', [50, 80], scale=3, thickness=3, offset=10)

            # Check the Collision
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv.polylines(imgMain, [pts], False, (0, 200, 0), 3)
            minDist = cv.pointPolygonTest(pts, (cx, cy), True)

            if -3 <= minDist <= 3:
                print("Hit")
                self.gameOver = True
                self.points = []  # All points of snake
                self.lengths = []  # Distance between each points
                self.currentLength = 0  # Total length off Snake
                self.allowedLength = 300  # Total allowed Length
                self.previousHead = 0, 0  # previous Head Point
                self.randomFoodLocation()

        return imgMain


game = SnakeGameClass("E:/Extra Codes/Python/Python Projects/Virtual FunHub (Games)/snakegame/Donut.png")

######################################################################################
#Main Loop
while True:  # for VideoCam
    success, img = cap.read()
    img = cv.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)  # For Flipping the side

    if hands:  # for finding Landmark or index of the finger
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)

    cv.imshow("Image", img)
    key = cv.waitKey(1)
    if key == ord('r'):
        game.gameOver = False
        game.score = 0
######################################################################################