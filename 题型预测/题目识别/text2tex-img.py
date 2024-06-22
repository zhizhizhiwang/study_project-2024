from PIL import Image
from pix2tex.cli import LatexOCR


img = Image.open(r'./img/text1-tex.jpg')
print(img)
model = LatexOCR()
print(model(img))