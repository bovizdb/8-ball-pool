import numpy as np
import cv2

points = []

img = cv2.imread('undistorted.png')
cv2.imshow('img', img)

def select_points(event, x, y, flags, params):
    if len(points) < 4:
        if event == cv2.EVENT_LBUTTONDOWN:
            print(x, ' ', y)
            points.append((x, y))
            cv2.circle(img, (x, y), 3, (0, 0, 255), -1)
            cv2.imshow('img', img)
    if len(points) == 4:
        open('crop-points.txt', 'w').write(str(points))
        dst_points = np.array([[0, 0], [1880, 0], [1880, 910], [0, 910]], dtype=np.float32)
        src_points = np.array(points, dtype=np.float32)
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        result = cv2.warpPerspective(img, matrix, (1880, 910))
        cv2.imshow('result', result)


cv2.setMouseCallback('img', select_points)
cv2.waitKey(0)
cv2.destroyAllWindows()