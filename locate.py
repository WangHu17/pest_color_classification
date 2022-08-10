import os

import cv2
import numpy as np
import sobel

# 设置最小框的面积
THRESHHOLD = 30


# 通过聚类获取黑色背景的害虫二值图
def get_thresh_by_kmeans(img):
    img = cv2.medianBlur(img, 11)
    # cv2.imshow("模糊", img)
    # 构建图像数据
    data = img.reshape((-1, 3))
    data = np.float32(data)
    # 图像聚类
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    num_clusters = 2
    ret, label, center = cv2.kmeans(data, num_clusters, None, criteria, num_clusters, cv2.KMEANS_RANDOM_CENTERS)
    center = center.astype(int)
    center1 = np.mean(center[0]).astype(int)
    center2 = np.mean(center[1]).astype(int)
    max = center1 if center1 > center2 else center2
    # print("center", center1, center2)
    # 显示聚类后的图像
    center = np.uint8(center)
    res = center[label.flatten()]
    dst = res.reshape(img.shape)
    dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("dst", dst)
    th, thres = cv2.threshold(dst, max-10, 255, cv2.THRESH_BINARY)
    # cv2.imshow("thres", thres)
    # thres = sobel.baweraopen(thres, 300)
    return thres


# 通过聚类获取害虫轮廓
def get_contour(img):
    image = get_thresh_by_kmeans(img)
    h, w = image.shape
    row1 = int(h - h * 0.02)
    col1 = int(w * 0.02)
    row2 = int(h - h * 0.02)
    col2 = int(w - w * 0.02)
    v1 = image[row1, col1]
    v2 = image[row2, col2]
    if v1 == 255 and v2 == 255:
        cv2.bitwise_not(image, image)
    thresh = cv2.GaussianBlur(image, (5, 5), 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contour = cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    # 获取轮廓索引
    max_area = 0
    maxI = 0
    if len(contours) == 0:
        return None
    for index in range(len(contours)):
        area = cv2.contourArea(contours[index])
        if area > max_area:
            max_area = area
            maxI = index
    return contours[maxI]


# 获取害虫轮廓
def get_contour1(img, i):
    # img为原图,image为二值化之后的黑白图片。
    img, image = sobel.sobel_cal(img, THRESHHOLD)
    # cv2.imshow("image", image)
    h, w = image.shape
    # print(h, w)
    row1 = int(h-h*0.02)
    col1 = int(w*0.02)
    row2 = int(h-h*0.02)
    col2 = int(w-w*0.02)
    v1 = image[row1, col1]
    v2 = image[row2, col2]
    # print(v1, v2)
    if v1 == 255 and v2 == 255:
        image = get_thresh_by_kmeans(img)
        v1 = image[row1, col1]
        v2 = image[row2, col2]
        if v1 == 255 and v2 == 255:
            cv2.bitwise_not(image, image)

    thresh = cv2.GaussianBlur(image, (5, 5), 0)
    # cv2.imshow("thresh ", thresh)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    cv2.imshow(i, contour)

    # 获取轮廓索引
    max_area = 0
    maxI = 0
    if len(contours) == 0:
        return None
    for index in range(len(contours)):
        area = cv2.contourArea(contours[index])
        if area > max_area:
            max_area = area
            maxI = index
    return contours[maxI]


# 获取害虫子图像
def get_pest_img(img):
    # 获取图像轮廓
    contour = get_contour(img)
    if contour is None:
        print("轮廓获取失败")
        return None
    # 截取图片
    x, y, w, h = cv2.boundingRect(contour)
    # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    img = img[y:y + h, x:x + w]
    return img


# 返回替换背景后的害虫图像
def replace_bg(img):
    # 获取图像轮廓
    contour = get_contour(img)
    if contour is None:
        print("轮廓获取失败")
        return None
    # 替换轮廓外的背景色
    fill_color = [0, 255, 0]
    mask_value = 255
    mask = np.zeros(img.shape[:-1]).astype(np.uint8)
    cv2.fillPoly(mask, [contour], mask_value)
    sel = mask != mask_value
    img[sel] = fill_color

    # 截取图片
    x, y, w, h = cv2.boundingRect(contour)
    # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    img = img[y:y+h, x:x+w]

    return img


if __name__ == '__main__':
    path = r"F:\DataSet\svm_training_imgs\9"
    for i in os.listdir(path):
        img = cv2.imread(os.path.join(path, i))
        img = cv2.resize(img, (400, 400))
        contour = get_contour(img)
        contourImg = cv2.drawContours(img, contour, -1, (0, 255, 0), 2)
        cv2.imshow(i, contourImg)
    # img = cv2.imread(path)
    # img = cv2.resize(img, (400, 400))
    # out = get_contour(img)
    # cv2.imshow("img", out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()