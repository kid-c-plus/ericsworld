import png

width = 300
height = 300
margin = (15, 25, 35, 25)
iterator = 50
ul_location = 49
#color = (128, 128, 128, 150)
color = (245, 36, 36, 150)
bg = (0, 0, 0, 0)

ofile = "underline.png"

img = []
for _ in range(margin[0]):
    img.append(bg * width)

for y in range(height - (margin[0] + margin[2])):
    if y % iterator == ul_location:
        img.append((bg * margin[1]) + (color * (width - (margin[1] + margin[3]))) + (bg * margin[3]))
    else:
        img.append(bg * width) 

for _ in range(margin[2]):
    img.append(bg * width)

with open(ofile, "wb") as f:
    w = png.Writer(width, height, greyscale=False, alpha=True)
    w.write(f, img)

