from PIL import Image
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="file to square")
parser.add_argument("-d", "--dir", help="directory to square")

args = parser.parse_args()

if args.file:
    files = [args.file]
elif args.dir:
    files = [os.path.join(args.dir, f) for f in os.listdir(args.dir)]
else:
    files = [os.path.join(d, f) for d in os.listdir(".") if os.path.isdir(d)
        for f in os.listdir(d)]

for file in files:
    try:
        with Image.open(file) as im:
            if im.width < im.height:
                ystart = (im.height - im.width) // 2
                im_crop = im.crop((0, ystart, im.width, ystart + im.width))
            elif im.width > im.height:
                xstart = (im.width - im.height) // 2
                im_crop = im.crop((xstart, 0, xstart + im.height, im.height))
            im_crop.save(file)
            print(f"Cropped {file} to {min(im.width, im.height)}")
    except Exception as e:
        os.remove(file)
        print(f"Deleted {file} due to {type(e)}: {str(e)}")
            
