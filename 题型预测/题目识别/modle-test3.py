# from gpt-4o
# 有点参考价值

from typing import *

import cv2
import pytesseract
import unicodedata
from PIL import Image, ImageDraw, ImageFont

# 配置Tesseract的路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows路径
# 对于Mac和Linux，确保Tesseract在系统路径中，无需配置

font_path = "../../font/unifont-15.1.05.otf"  # 指定你的中文字体路径
font_size = 50
pil_font = ImageFont.truetype(font_path, font_size)


def is_chinese(char: str):
    # 检查是否是中文
    return any([unicodedata.category(_x) == 'Lo' and "CJK" in unicodedata.name(_x) for _x in list(char)])
    # 此处为短路逻辑, 一些控制字符会导致识别出错先一步返回false


# 读取图像
image = cv2.imread('../../img/text1-onequestion.jpg')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pil_image = Image.fromarray(image_rgb)
pil_draw = ImageDraw.Draw(pil_image)

# 图像预处理
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转灰度
blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 提取高斯核
_, binary = cv2.threshold(blur, 165, 255, cv2.THRESH_BINARY_INV)  # 转二值

# cv2.imshow("binary", binary)
cv2.waitKey(0)

# 形态学操作连接相邻的文本区域
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

# 检测文本区域
contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# TODO: 描边贴太紧了, 有些划分的块过小或者是一块只有一个字, 识别率难以高

# 初始化文本和公式存储列表
text_blocks = []
formula_blocks = []

text_blocks_pos: List[Tuple[int, int, int, int]] = []
result_text_pos: List[Tuple[int, int, int, int]] = []

for contour in contours:
    # 计算轮廓的边界框
    x, y, w, h = cv2.boundingRect(contour)

    # print(x, y, w, h)

    # 根据轮廓大小过滤掉小轮廓

    if w > 10 and h > 30:  # 调整大小阈值以适应具体情况

        y = y - 10
        h = h + 20
        x = x - 10
        w = w + 10

        roi = image[y:y + h, x:x + w]

        # 使用OCR识别文本
        text = pytesseract.image_to_string(roi, lang='chi_sim+eng', config='--psm 6')

        pil_draw.text((x, y + h), text, font=pil_font, fill=(0, 0, 0))

        # 简单判断是否是公式（可以改进）
        if is_chinese(text):
            text_blocks.append(text)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 红色框用于文本
            text_blocks_pos.append((x, y, w, h))
        else:
            formula_blocks.append(text)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 绿色框用于公式
            cv2.circle(image, (x, y), 5, (0, 0, 0), -1)
            cv2.circle(image, (x + w, y + h), 5, (0, 255, 0), -1)


# 合并
def merge_rectangles(rectangles, y_tolerance=20, h_tolerance=50):
    # 按 y 坐标和 x 坐标排序
    rectangles.sort(key=lambda rect: (rect[1], rect[0]))

    merged = []

    for rect in rectangles:
        if not merged:
            merged.append(rect)
        else:
            last = merged[-1]
            # 检查 y 坐标和高度是否相近
            if (abs(last[1] - rect[1]) <= y_tolerance) and \
                    (abs(last[3] - rect[3]) <= h_tolerance) and \
                    (last[0] <= rect[0] - rect[2] <= last[0] + last[2] or rect[0] <= last[0] <= rect[0] + rect[2]):
                # 合并
                new_x = min(last[0], rect[0])
                new_y = last[1]
                new_w = max(last[0] + last[2], rect[0] + rect[2]) - new_x
                new_h = max(last[3], rect[3])  # 高度取较大值
                merged[-1] = (new_x, new_y, new_w, new_h)
            else:
                merged.append(rect)

    return merged


assert len(text_blocks_pos) > 1

result_text_pos = merge_rectangles(text_blocks_pos)

for x, y, w, h in result_text_pos:
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), 2)

# 显示结果图像
cv2.imshow('Detected Text and Formulas', image)
pil_image.show()
cv2.waitKey(0)
cv2.destroyAllWindows()

# 输出文本和公式内容
print("文本部分：")
print(" ,".join(text_blocks))

print("公式部分：")
print(" ,".join(formula_blocks))
