import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows路径

image = cv2.imread('../../img/text1-tex.jpg')

# 图像预处理
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转灰度
blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 提取高斯核
_, binary = cv2.threshold(blur, 160, 255, cv2.THRESH_BINARY_INV)  # 转二值

cv2.imshow("binary", binary)
cv2.waitKey(0)

text = pytesseract.image_to_string(image, lang='chi_sim+eng', config='--psm 6')

print(text)


