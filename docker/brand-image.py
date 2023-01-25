from PIL import Image, ImageDraw
import datetime

img = Image.open('img/black-hole-ellipse.png')
d1 = ImageDraw.Draw(img)
now = datetime.datetime.now()
d1.text((28, 460), f"peviewer build on {now}", fill=(128, 128, 128))
img.save('img/black-hole-ellipse.png')
