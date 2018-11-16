'''ASCII Art generator

Command line usage: asciigen.py [-h] [--width WIDTH] [--contrast RATIO]
                                [--brightness RATIO]
                                image

positional arguments:
  image                 Image file to read.

optional arguments:
  -h, --help            show this help message and exit
  --width WIDTH, -w WIDTH
                        Width of output text. (Default: width of image)
  --contrast RATIO, -c RATIO
                        Contrast ratio to apply to image. (1.0 is original
                        image, > 1.0 is high contrast)
  --brightness RATIO, -b RATIO
                        Brightness ratio to apply to image. (1.0 is original
                        image, > 1.0 is high brightness)
                        
                        

Module usage:
>>> import asciigen
>>> asciigen.from_filename('./python-logo.png', width=40, contrast=1.8)

                       ......          .....
                     .        .-~~~~,        ..
                    . :!L1MZ9DN8p000bND@GMn{-  .
                    'XhHHHHHHHHHHHHHHHHHHHHHpl" .
                    ZHH$Mwou$$$HHHHHH$$$$$$$HH0c .
                 . !HgHC .. YH$HHHHHHHHHHHHHHdHb-
                 . vHdHa'  -ZH$HHHHHHHHHHHHHHH$$) .
                 . vH$HHpEEpHHHHHHHHHHHHHHHHHHH$) .
         ....    . vH$HHHHHHHHHHHHHHHHHHHHHHHHHH) .
       ..          '<>>>>**>>>><*vqHHHHHHHHHHHHH) .
      .  |F%O5QUUUQ5@@@99996999996$HHHHHHHHHHHHH)`|;;;;;;~,.
     . /4gHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH?:^||||||||",
    . rgHH$$$$$$$$$$$$$$$$$$$$$$$$HHHHHHHHHHHHHH?:^||||||||||,
   . /qHdHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH$H!:^||||||||||".
   . %HdHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH$dHD:,||||||||||||-
    ~8HHHHHHHHHHHHHHHHH$$$$$$$$$$$$$$$$$$$$HHHp)."||||||||||||".
  . vH$HHHHHHHHHHHHHH$HHHHHHHHHHHHHHHHHHHHHH8x_:"||||||||||||||:
  . mH$HHHHHHHHHHHH$HHd6Pn7C777777777777CCT?-:_||||||||||||||||'
  . FH$HHHHHHHHHHH$H8s^`,-----------------~_"^|||||||||||||||||-
  . ?HHHHHHHHHHHHHHM-:_|^^^^^^^^^^^^^^^^^^^^|||||||||||||||||||:
    :NHHHHHHHHHH$Ha -^||||||||||||||||||||||||||||||||||||||||".
   . 1HdHHHHHHHHHH*.^|||||||||||||||||||||||||||||||||||||||||-
     "8HdHHHHHHHHp-:|||||||||||||||||||||||||||||||||||||||||;.
    . }qH$$$$$$$HR-:||||||||||||||||||||||||||||||||||||||||"`
     . /OHHHHHHHHp-:|||||||||||||||||||||||||||||||||||||||_`
      .  /otPMMMfS,:||||||||||||||~~~~~~~~~~~~~~________~-:
       ..          :|||||||||||||"',,,,,,,,,,,,,.
         ......... :||||||||||||||||||||||||||||:
                   :||||||||||||||||||||;-~;||||:
                   :|||||||||||||||||||-    ~|||:
                   ."||||||||||||||||||-    ~||;
                    `_||||||||||||||||||_--;||_`
                      :~"||||||||||||||||||"~:
                        .`,-~_;""""";;_~-,`
                                ....
'''

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageEnhance
import string
import collections

font = ImageFont.load_default()

def char_density(c, font=font):
    '''Count the number of black pixels in a rendered character.'''
    image = Image.new('1', font.getsize(c), color=255)
    
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), c, font=font)
    
    return collections.Counter(image.getdata())[0] #0 is black

# Sort printable characters according to the number of black pixels present.
# Don't use string.printable, since we don't want any whitespace except spaces.
chars = list(sorted(string.ascii_letters + string.digits + string.punctuation + ' ', key=char_density, reverse=True))

char_width, char_height = ImageFont.load_default().getsize('X')


def generate_art(image, width=None, height=None):
    '''Return an iterator that produces the ascii art.'''
    
    width = width or image.size[0]
    # Characters aren't square, so scale the output by the aspect ratio of a charater
    height = int((height or image.size[1]) * char_width / float(char_height))
    
    image = image.resize((width, height), Image.ANTIALIAS).convert('L')

    pix = image.load()
    for y in range(height):
        for x in range(width):
            yield chars[int(pix[x, y] / 255. * (len(chars) - 1) + 0.5)]
        yield '\n'
        
        
def from_filename(name, width=None, brightness=None, contrast=None):
    '''Open an image file and return a string of its ASCII Art.'''
    
    image = Image.open(name)
    if width is not None:
        scale = float(width) / image.size[0]
    else:
        scale = 1
        
    if contrast is not None:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness is not None:
        image = ImageEnhance.Brightness(image).enhance(brightness)
        
    return ''.join(generate_art(image, int(image.size[0] * scale), int(image.size[1] * scale)))

    
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ascii art from an image file.')
    parser.add_argument('image', help='Image file to read.')
    parser.add_argument('--width', '-w', type=int,
                        help='Width of output text. (Default: width of image)')
    parser.add_argument('--contrast', '-c', metavar='RATIO', type=float,
                        help='Contrast ratio to apply to image. (1.0 is original image, > 1.0 is high contrast)')
    parser.add_argument('--brightness', '-b', metavar='RATIO', type=float,
                        help='Brightness ratio to apply to image. (1.0 is original image, > 1.0 is high brightness)')
    
    args = parser.parse_args()
    print(from_filename(args.image, args.width, args.brightness, args.contrast))

