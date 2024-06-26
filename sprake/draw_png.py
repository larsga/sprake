
import platform
from sprake import style

from PIL import Image, ImageDraw, ImageFont, ImageOps
class PNGDrawer:

    def __init__(self, outfile, fontsize):
        self._font = locate_font(fontsize)
        self._outfile = outfile
        self._fontsize = fontsize

    def get_font_size(self):
        return self._fontsize

    def get_text_size(self, text):
        '(height, width)'
        (left, top, right, bottom) = self._font.getbbox(text)
        return (bottom - top, right - left)

    def create(self, height, width):
        self._image = Image.new('RGB', (int(height), int(width)), (255, 255, 255))
        self._realdraw = ImageDraw.Draw(self._image)

    def draw_text(self, pos, text, degree = 0, color = style.BLACK):
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
        self._image.paste(ImageOps.colorize(buffer, (0,0,0), (0,0,0)), tuple(map(int, pos)), buffer)

    def circle(self, pos, r, color):
        (x, y) = pos
        self._realdraw.ellipse((x - r, y - r, x + r, y + r), fill = color.to_rgb_tuple())

    def circle_segment(self, x, y, start, end, r, color = style.BLACK,
                       stroke = 1, id = None):
        pass

    def line(self, start, end, color = 'black', stroke = 1, dash = False):
        self._realdraw.line([start, end], fill = color.to_rgb_tuple(), width = stroke)

    def save(self):
        self._image.save(self._outfile, 'PNG')

def locate_font(fontsize):
    try:
        return ImageFont.truetype('Arial.ttf', fontsize)
    except OSError:
        return ImageFont.truetype('resources/cruft.ttf', fontsize)
