from PIL import Image

import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

text = pytesseract.image_to_string(Image.open('image.jpg'))

print(text)