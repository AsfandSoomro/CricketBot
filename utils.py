from PIL import Image, ImageDraw


def pitch_image(position=1, speed=None):
  if position < 1 or position > 9:
    raise ValueError("Position not in range [1 - 9]")
  with Image.open("./images/cricket_pitch.jpg") as img:
    img1 = ImageDraw.Draw(img)
    img1.line([(333, 15), (440 - (position * 20), 500)], fill="lime", width=4)
    #img.show()
    return img


#itch_image(position=9)
