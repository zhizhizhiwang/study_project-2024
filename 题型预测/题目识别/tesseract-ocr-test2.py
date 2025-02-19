import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pix2tex import cli as latex_ocr
from typing import Tuple, Optional


class ImageToMarkdownConverter:
    def __init__(self):
        """初始化图像处理参数和模型"""
        self.text_ocr_config = r'--oem 3 --psm 6 -l chi_sim+eng'  # Tesseract配置
        self.formula_ocr = latex_ocr.LatexOCR()  # LaTeX OCR模型
        self.min_contour_area = 100  # 最小轮廓面积阈值

    def process_image(self, image_path: str) -> str:
        """
        处理图像的主函数
        :param image_path: 输入图片路径
        :return: 生成的Markdown内容
        """
        # 预处理流程
        img = self._load_image(image_path)
        img = self._auto_adjust(img)
        img = self._enhance_image(img)

        # 分割处理流程
        segments = self._segment_image(img)

        # 识别处理流程
        results = []
        for segment in segments:
            if self._is_likely_formula(segment):
                results.append(self._recognize_formula(segment))
            else:
                results.append(self._recognize_text(segment))

        return "\n\n".join(results)

    def _load_image(self, path: str) -> Image.Image:
        """加载图像并进行基本预处理"""
        img = Image.open(path)
        return img.convert('RGB')

    def _auto_adjust(self, img: Image.Image) -> Image.Image:
        """自动调整图像（透视校正+旋转校正）"""
        cv_img = np.array(img)
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)

        # 透视校正
        corrected = self._perspective_correction(cv_img)
        # 旋转校正
        corrected = self._rotate_correction(corrected)

        return Image.fromarray(cv2.cvtColor(corrected, cv2.COLOR_BGR2RGB))

    def _perspective_correction(self, img: np.ndarray) -> np.ndarray:
        """透视校正"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 200)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return img

        largest = max(contours, key=cv2.contourArea)
        epsilon = 0.02 * cv2.contourArea(largest)
        approx = cv2.approxPolyDP(largest, epsilon, True)

        if len(approx) == 4:
            return self._four_point_transform(img, approx.reshape(4, 2))
        return img

    def _four_point_transform(self, img: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """四点透视变换"""
        rect = self._order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """对坐标点进行排序：左上，右上，右下，左下"""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # 左上
        rect[2] = pts[np.argmax(s)]  # 右下

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # 右上
        rect[3] = pts[np.argmax(diff)]  # 左下
        return rect

    def _rotate_correction(self, img: np.ndarray) -> np.ndarray:
        """旋转校正"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100,
                                minLineLength=100, maxLineGap=10)

        if lines is not None:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                if abs(angle) < 45:  # 忽略接近垂直的线
                    angles.append(angle)

            if angles:
                median_angle = np.median(angles)
                (h, w) = img.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                return cv2.warpAffine(img, M, (w, h),
                                      flags=cv2.INTER_CUBIC,
                                      borderMode=cv2.BORDER_REPLICATE)
        return img

    def _enhance_image(self, img: Image.Image) -> Image.Image:
        """图像增强处理"""
        # 对比度增强
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        # 锐化处理
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        return img

    def _segment_image(self, img: Image.Image) -> list:
        """图像分割为多个区域"""
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255,
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        segments = []
        for cnt in contours:
            if cv2.contourArea(cnt) < self.min_contour_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            segment = img.crop((x, y, x + w, y + h))
            segments.append((segment, (x, y)))

        # 按从上到下，从左到右排序
        segments.sort(key=lambda x: (x[1][1], x[1][0]))
        return [s[0] for s in segments]

    def _is_likely_formula(self, img: Image.Image) -> bool:
        """启发式判断是否是公式区域"""
        # 基于宽高比的简单判断
        w, h = img.size
        if w / h > 5:  # 宽高比大的更可能是文本
            return False
        return True

    def _recognize_text(self, img: Image.Image) -> str:
        """识别文本内容"""
        return pytesseract.image_to_string(img, config=self.text_ocr_config).strip()

    def _recognize_formula(self, img: Image.Image) -> str:
        """识别数学公式"""
        return f"$${self.formula_ocr(img)}$$"


if __name__ == "__main__":
    converter = ImageToMarkdownConverter()

    # 示例用法
    markdown_output = converter.process_image(r"../../img/text1-onequestion.jpg")
    print("生成结果：")
    print(markdown_output)
