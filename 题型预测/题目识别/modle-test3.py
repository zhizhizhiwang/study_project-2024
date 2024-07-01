# from gpt-4o
# 有点参考价值

import cv2
import pytesseract

# 配置Tesseract的路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows路径
# 对于Mac和Linux，确保Tesseract在系统路径中，无需配置

# 读取图像
image = cv2.imread('../../img/text1-onequestion.jpg')

# 图像预处理
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
_, binary = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY_INV)

# 形态学操作连接相邻的文本区域
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

# 检测文本区域
contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 初始化文本和公式存储列表
text_blocks = []
formula_blocks = []

for contour in contours:
    # 计算轮廓的边界框
    x, y, w, h = cv2.boundingRect(contour)

    # 根据轮廓大小过滤掉小轮廓
    if w > 30 and h > 10:  # 调整大小阈值以适应具体情况
        roi = image[y:y + h, x:x + w]

        # 使用OCR识别文本
        text = pytesseract.image_to_string(roi, lang='chi_sim+eng', config='--psm 6')

        # 简单判断是否是公式（可以改进）
        if any(char.isdigit() for char in text) or any(char in '+-*/=()' for char in text):
            formula_blocks.append(text)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 红色框用于公式
        else:
            text_blocks.append(text)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 绿色框用于文本

# 显示结果图像
cv2.imshow('Detected Text and Formulas', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 输出文本和公式内容
print("文本部分：")
print("\n".join(text_blocks))

print("公式部分：")
print("\n".join(formula_blocks))
