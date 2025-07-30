import cv2
import numpy as np
import sympy as sp

dir = 'test-images/'

def intersection(img, x1, y1, x2, y2, xc, yc, r):
    x, y = sp.symbols('x y')
    eq1 = sp.Eq(((y2-y1)/(x2-x1))*(x-x1) + y1, y)
    eq2 = sp.Eq((x-xc)**2 + (y-yc)**2, r**2)
    sol = sp.solve((eq1, eq2), (x, y))
    for (i, j) in sol:
        if not i.is_real or not j.is_real:
            continue
        if i >= x1 and i <= x2:
            cv2.circle(img, (int(i), int(j)), 2, (0, 255, 0), 3)
    return img, sol

def undistort(img):
    # K = np.array([[740.0, 0, 630], [0, 740.0, 390], [0, 0, 1]])
    # D = np.array([[0.0], [0.0], [0.0], [0.0]])
    K = np.array([[740.0, 0, 700], [0, 700.0, 390], [0, 0, 1]])
    D = np.array([[0.0], [0.0], [0.0], [0.0]])

    img = cv2.copyMakeBorder(img, 40, 40, 40, 160, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    width = img.shape[1]
    height = img.shape[0]
    img = cv2.fisheye.undistortImage(img, K, D, Knew=K)
    return img

def crop_image(img, x1, y1, x2, y2):
    h, w = img.shape[:2]
    if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
        raise ValueError("Crop coordinates are out of bounds")
    return img[y1:y2, x1:x2]

def rectagle_mask(img, x1, y1, x2, y2):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return masked_img

def find_circles(img):
    img = cv2.medianBlur(img, 5)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=120, param2=20, minRadius=16, maxRadius=23)
    if circles is None:
        return None
    circles = np.uint16(np.around(circles[0, :]))
    with open('public/coordinates.txt', 'w') as f:
        for (x, y, r) in circles:
            print(r, end=' ')
            cv2.circle(img, (x, y), r, (255, 255, 0), 2)
            cv2.circle(img, (x, y), 2, (0, 0, 255), 3)
            img, sol = intersection(img, 190, 530, 650, 500, x, y, r)
            f.write(f'{x} {y}\n')
    return img

def find_lines(img):
    img = cv2.medianBlur(img, 3)
    # img = crop_image(img, 80, 90, img.shape[1]-80, img.shape[0] - 70)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 120, apertureSize=3)
    _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edges, kernel, iterations=5)
    cv2.imshow('edges', dilated)
    lines = cv2.HoughLinesP(dilated, 1, np.pi/180, 100, minLineLength=50, maxLineGap=20)
    blank = np.zeros_like(edges)
    if lines is not None:
        for points in lines:
            x1, y1, x2, y2 = points[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(blank, (x1, y1), 2, (255, 255, 255), 2)
            cv2.circle(blank, (x2, y2), 2, (255, 255, 255), 2)
    return img, blank

def find_contours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    cv2.imshow('threshold', threshold)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i, contour in enumerate(contours):
        if i == 0:
            continue
        approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
        print(len(approx))
        cv2.drawContours(img, [contour], 0, (0, 0, 255), 5)
    return img

for i in range(45, 46):
    # img = cv2.imread(dir + 'frame_' + str(i).zfill(6) + '.png')
    img = cv2.imread('test-images/frame_001211.png')
    img = undistort(img)
    img = crop_image(img, 80, 90, img.shape[1]-80, img.shape[0] - 70)
    circles = find_circles(img)
    lines_img, points_img = find_lines(img)
    cv2.imshow('points', points_img)
    lines = cv2.HoughLinesP(points_img, 1, np.pi/180, 70, minLineLength=20, maxLineGap=0)
    if lines is not None:
        for points in lines:
            x1, y1, x2, y2 = points[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
    # contours = find_contours(img)
    # cv2.imshow('contours', contours)

    # cv2.imshow('circles', circles)
    cv2.imshow('lines', lines_img)
    cv2.imshow('img', img)
    cv2.imwrite('out.png', img)
    cv2.waitKey(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break