from email.mime import image
import cv2
import math
import json
import numpy as np
import sympy as sp

dir = 'test-images/'

balls = {}

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
    # K = np.array([[740.0, 0, 700], [0, 700.0, 390], [0, 0, 1]])
    # D = np.array([[0.0], [0.0], [0.0], [0.0]])
    K = np.array([[720.0, 0, 630], [0, 740.0, 390], [0, 0, 1]])
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

def transform_image(img):
    points = eval(open('crop-points.txt', 'r').read())
    src_points = np.array(points, dtype=np.float32)
    dst_points = np.array([[0, 0], [1880, 0], [1880, 910], [0, 910]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    img = cv2.warpPerspective(img, matrix, (1880, 910))
    return img

def color_mask(img, colors):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for c in colors:
        lower = np.array(c)-40
        upper = np.array(c)+40
        color_mask = cv2.inRange(img, lower, upper)
        mask = cv2.bitwise_or(mask, color_mask)
    return mask

def rectagle_mask(img, x1, y1, x2, y2):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return masked_img

def circle_mask(img, xc, yc, r):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (xc, yc), r, 255, -1)
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return masked_img

def get_type(mask, threshold1=500, threshold2=2300):
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(mask_gray, 127, 255, cv2.THRESH_BINARY)
    pixel_count = cv2.countNonZero(threshold)
    type = 'solid' if pixel_count < threshold1 or pixel_count > threshold2 else 'stripe'
    return type

def get_color(img):
    colors = json.loads(open('colors.json', 'r').read())
    color_values = {}
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for c in colors:
        lower = np.array(colors[c])-20
        upper = np.array(colors[c])+20
        color_mask = cv2.inRange(img, lower, upper)
        mask = cv2.bitwise_or(mask, color_mask)
        pixel_count = cv2.countNonZero(color_mask)
        color_values[c] = pixel_count
    print(color_values)
    color = max(color_values, key=color_values.get)
    if color == 'black' and abs(color_values[color] - color_values['purple']) < 200:
        color = 'purple'
    intensity = color_values[color]
    type = 'solid' if intensity > 1000 else 'stripe'
    if intensity < 100:
        color, type = 'white', 'solid'
    return color, type, intensity

def get_label(color, type):
    if color == 'white':
        return 0
    if color == 'black':
        return 8
    colors = ['yellow', 'blue', 'red', 'purple', 'orange', 'green', 'maroon']
    if type == 'solid':
        return colors.index(color) + 1
    return colors.index(color) + 9


def find_circles(img, original):
    balls_list = []
    colors = {}
    edges = cv2.Canny(img, 50, 100, apertureSize=3)
    cv2.imshow('edges', edges)
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 1, param1=100, param2=8, minRadius=25, maxRadius=32)
    if circles is None:
        return None
    processed = [False] * len(circles[0])
    for i in range(len(circles[0])):
        if processed[i]:
            continue
        x1, y1, r1 = circles[0][i]
        xs, ys = [x1], [y1]
        for j in range(i+1, len(circles[0])):
            if processed[j]:
                continue
            x2, y2, r2 = circles[0][j]
            if abs(x1-x2) < 30 and abs(y1-y2) < 30:
                processed[j] = True
                xs.append(circles[0][j][0])
                ys.append(circles[0][j][1])
                continue
        xc, yc = np.mean(xs), np.mean(ys)
        mask = circle_mask(original, int(xc), int(yc), 30)
        # type = get_type(mask)
        color, type, intensity = get_color(mask)
        print(type, color, intensity)
        if color not in colors:
            colors[color] = []
        colors[color].append(intensity)
        balls_list.append({'x': f'{xc:.2f}', 'y': f'{yc:.2f}', 'color': color, 'type': type, 'intensity': intensity})

    for ball in balls_list:
        if len(colors[ball['color']]) == 2:
            if ball['intensity'] == max(colors[ball['color']]):
                ball['type'] = 'solid'
            else: ball['type'] = 'stripe'
        ball['label'] = get_label(ball['color'], ball['type'])
        balls[ball['label']] = ball
    print(balls)
    json.encoder.FLOAT_REPR = lambda o: format(o, '.2f')
    json.dump(balls, open('public/balls.json', 'w'), indent=4)
    colors = json.loads(open('colors.json', 'r').read())
    colors['white'] = [255, 255, 255]
    for ball in balls.values():
        x, y, r, color = int(float(ball['x'])), int(float(ball['y'])), 30, colors[ball['color']]
        cv2.circle(original, (x, y), r, tuple(color), 5 if ball['type'] == 'solid' else 2)
        cv2.circle(original, (x, y), 2, (0, 0, 255), 3)
        # img, sol = intersection(img, 190, 530, 650, 500, x, y, r)
    return original

def find_lines(img, original):
    edges = cv2.Canny(img, 50, 100, apertureSize=3)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    eroded = cv2.erode(img, kernel, iterations=0)
    linesP = cv2.HoughLinesP(eroded, 1, np.pi/180, 120, minLineLength=80, maxLineGap=20)
    lines = cv2.HoughLines(eroded, 1, np.pi/180, 100)
    if lines is None:
        return original
    theta = np.mean(np.array([line[0][1] for line in lines]))
    print(theta)
    xs = []
    if linesP is not None:
        for points in linesP:
            print(points)
            x1, y1, x2, y2 = points[0]
            xs.append((x1+x2)/2)
            cv2.line(original, (x1, y1), (x2, y2), (0, 255, 0), 3)
    if balls.get(0) and np.mean(xs) > float(balls[0]['x']):
        theta += np.pi
    open('public/cue.txt', 'w').write(f'{theta:.3f}')
    return original

def find_contours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    cv2.imshow('threshold', threshold)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    for i, contour in enumerate(contours):
        if i == 0:
            continue
        approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
        print(len(approx))
        cv2.drawContours(img, [contour], 0, (0, 0, 255), 5)
    return img

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, ' ', y)

original = cv2.imread('test-images/test-018.png')
img = undistort(original)
cv2.imwrite('undistorted.png', img)
img = transform_image(img)
masked = color_mask(img, [[70, 121, 61], [51, 84, 39]])
circles = find_circles(masked, img)
cue = color_mask(img, [[161, 217, 242]])
out = find_lines(cue, circles)
cv2.imshow('out', out)
cv2.imwrite('out.png', out)
cv2.setMouseCallback('out', click_event)
cv2.waitKey(0)