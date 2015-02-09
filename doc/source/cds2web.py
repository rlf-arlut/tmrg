#!/usr/bin/env python
import Image
import sys
img=Image.open(sys.argv[1])
pixels = img.load()
transform={}
transform[(0,0,0)]=(255,255,255)
#for i in range(img.size[0]):    # for every pixel:
#  for j in range(img.size[1]):
#    if pixels [i,j] in transform: 
#      pixels[i,j]=transform[pixels [i,j]]
#    print pixels [i,j]

new_pixels = []
pixels=list(img.getdata())
for pixel in pixels:
        if pixel==(0,0,0):pixel=(255,255,255)
        elif pixel==(193,255,193):pixel=(53,155,53)
        elif pixel==(255, 160, 122):pixel=(105,60,22)
        elif pixel==(255, 255, 0):pixel=(105,105,0)
        elif pixel==(0, 255, 255):pixel=(0,105,105)
        elif pixel==(0, 255, 0):pixel=(0,205,0)
        else:
          print pixel
        new_pixels.append(pixel)
        
#imagedata = []
#for i in range(img.width):
#   for j in range(img.height):
#     imagedata.append(self.intToRGB(img.data[i*self.height + j]))
newimage = Image.new("RGB",img.size)
newimage.putdata(new_pixels)
newimage.save("web_%s"%sys.argv[1])
