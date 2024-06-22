from PIL import Image
from pix2tex.cli import LatexOCR


img = Image.open(r'./img/text1-tex.jpg')



im = img.convert("L")

threshold  = 150
table  =  []
for  i  in  range( 256 ):
     if  i  <  threshold:
        table.append(0)
     else :
        table.append(1)
 #  convert to binary image by the table 
bim  =  im.point(table,"1" )
bim.show()

# new_img = img.point(lambda x : 0 if x < 200 else 1, "1")
# new_img.show()
model = LatexOCR()
print(model(bim))

