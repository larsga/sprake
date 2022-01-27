
from sprake import style

from PIL import Image, ImageDraw, ImageFont, ImageOps
class PNGDrawer:

    def __init__(self, outfile, fontsize):
        self._font = ImageFont.truetype('Arial.ttf', fontsize)
        self._outfile = outfile

    def get_text_size(self, text):
        '(height, width)'
        return self._font.getsize(text)

    def create(self, height, width):
        self._image = Image.new('RGB', (height, width), (255, 255, 255))
        self._realdraw = ImageDraw.Draw(self._image)

    def draw_text(self, pos, text, degree = 0, color = 'black'):
        size = self.get_text_size(text)
        buffer = Image.new('L', size)
        draw = ImageDraw.Draw(buffer)
        draw.text(
            (0, 0),
            text = text,
            fill = 255,
            font = self._font,
        )

        buffer = buffer.rotate(int(round(degree)), expand = True)
        # FIXME: need to adjust for expansion of rotated image
        self._image.paste(ImageOps.colorize(buffer, (0,0,0), (0,0,0)), map(int, pos), buffer)

    def circle(self, pos, r, color):
        (x, y) = pos
        self._realdraw.ellipse((x - r, y - r, x + r, y + r), fill = color)

    def circle_segment(self, start, end, r, color = 'black', stroke = 1,
                       id = None):
        pass

    def line(self, start, end, color = 'black', stroke = 1):
        self._realdraw.line([start, end], fill = color, width = stroke)

    def save(self):
        self._image.save(self._outfile, 'PNG')
