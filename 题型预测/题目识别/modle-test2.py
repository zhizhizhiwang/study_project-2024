# from gpt-4o
# 这个不能用

import cv2
import pytesseract

# 对本地pytesseract进行mixin，修改了寻找tesseract的文件路径 ->
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 读取图像
image = cv2.imread(r'../../img/text1-onequestion.jpg')

# 图像预处理
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

# 检测文本区域
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 初始化文本和公式存储列表
text_blocks = []
formula_blocks = []

for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    roi = image[y:y + h, x:x + w]

    # 使用OCR识别文本
    text = pytesseract.image_to_string(roi, config='--psm 6', lang='chi_sim+eng')

    print(text, end=' ')

    # 简单判断是否是公式（可以改进）
    if any(char.isdigit() for char in text) or any(char in '_{}+-*/=()' for char in text):
        formula_blocks.append(text)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 红色框用于公式
    else:
        text_blocks.append(text)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 绿色框用于文本

cv2.imshow('Detected Text and Formulas', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 输出结果
print("文本部分：")
print(" ".join(text_blocks))

print("公式部分：")
print(" ".join(formula_blocks))
