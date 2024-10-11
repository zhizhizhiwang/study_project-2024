# from gpt-4o
# 有点参考价值

from typing import *

import cv2
import pytesseract

# 配置Tesseract的路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows路径
# 对于Mac和Linux，确保Tesseract在系统路径中，无需配置

# 读取图像
image = cv2.imread('../../img/text1-onequestion.jpg')

# 图像预处理
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转灰度
blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 提取高斯核
_, binary = cv2.threshold(blur, 165, 255, cv2.THRESH_BINARY_INV)  # 转二值

cv2.imshow("binary", binary)
cv2.waitKey(0)

# 形态学操作连接相邻的文本区域
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

# 检测文本区域
contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

image_ = image.copy()
cv2.drawContours(image_, contours, -1, (255, 255, 255), 5)
cv2.imshow(" ", image_)
cv2.waitKey(0)
# TODO: 描边贴太紧了, 有些划分的块过小或者是一块只有一个字, 识别率难以高

# 初始化文本和公式存储列表
text_blocks = []
formula_blocks = []

text_blocks_pos : List[Tuple[int, int, int, int]] = []


for contour in contours:
    # 计算轮廓的边界框
    x, y, w, h = cv2.boundingRect(contour)

    # print(x, y, w, h)

    # 根据轮廓大小过滤掉小轮廓

    if w > 10 and h > 30:  # 调整大小阈值以适应具体情况
        roi = image[y - 10:y + h + 10, x - 10:x + w + 10]

        # 使用OCR识别文本
        text = pytesseract.image_to_string(roi, lang='chi_sim+eng', config='--psm 6')

        # 简单判断是否是公式（可以改进）
        if any(char.isdigit() for char in text) or any(char in '{}+-*/=()' for char in text):
            formula_blocks.append(text)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 红色框用于公式

        else:
            text_blocks.append(text)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 绿色框用于文本
            text_blocks_pos.append((x, y, w, h))
            cv2.circle(image, (x, y), 5, (0, 0, 0), -1)
            cv2.circle(image, (x + w, y + h), 5, (0, 255, 0), -1)

# 合并
result_text_pos : List[Tuple[int, int, int, int]] = []
assert len(text_blocks_pos) > 1


def my_cmp(_x : tuple[int, int, int, int], _y : tuple[int, int, int, int]):
    if abs(_y[1] - _x[1]) > 100:
        return False
    else:
        return _x[0] < _y[0]


result_text_pos.sort(key=lambda _x : _x[0], reverse=True)
result_text_pos.sort(key=lambda _x : _x[1], reverse=True)

ux, uy, uw, uh = text_blocks_pos[0]
for x, y , w, h in text_blocks_pos[1:]:
    if abs(uy - y) < 300 and abs(uh - h) < 300 and ux + uw > x - w:
        uy = max(uy, y)
        uh = max(uh, h)
        uw += w
    else:
        result_text_pos.append((ux, uy, uw, uh))
        ux, uy, uw, uh = x, y, w, h

for x, y, w, h in result_text_pos:
    cv2.rectangle(image, (x, y), (x + w, y + h), (255 , 255, 255), 2)


# 显示结果图像
cv2.imshow('Detected Text and Formulas', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 输出文本和公式内容
print("文本部分：")
print(" ,".join(text_blocks))

print("公式部分：")
print(" ,".join(formula_blocks))
