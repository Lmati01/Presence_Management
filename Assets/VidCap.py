import cv2

cap = cv2.VideoCapture('VidTest.mp4')
cap.set(3,640)
cap.set(4,480)
cap.set(10,100)
while True:
    success, img = cap.read()
    cv2.imshow("MyVideo",img)
    if cv2.waitKey(1) == ord('q'):
        break