
import math
from sprake import style

def rad2deg(rad):
    return (rad / math.pi) * 180

import fpdf
class PDFDrawer:

    def __init__(self, outfile, fontsize):
        self._outfile = outfile
        self._fontsize = fontsize

        # this is a dummy we just use for font size calculations
        # we overwrite it with a correctly sized one afterwards
        self._pdf = fpdf.FPDF('P', 'mm', format = 'A4')
        self._pdf.set_font('Helvetica', size = self._fontsize)

    def create(self, width, height):
        # instead of A4 we can compute the size and have (width, height)
        self._pdf = fpdf.FPDF('P', 'mm',
                              format = (self._conv(width), self._conv(height)))
        self._pdf.add_page()
        self._pdf.set_font('Helvetica', size = self._fontsize)

    def get_font_size(self):
        return self._fontsize

    def get_text_size(self, text):
        'Returns (height, width)'

        # trying to estimate
        height = self._pdf.get_string_width('X')

        return (self._unconv(height), self._unconv(self._pdf.get_string_width(text)))

    # degree: actually in degrees
    def draw_text(self, pos, text, degree = 0, color = style.BLACK):
        if degree > 90 and degree < 270:
            degree = degree - 180

        self._pdf.set_text_color(color.get_red_int(), color.get_green_int(), color.get_blue_int())
        (x, y) = pos
        with self._pdf.rotation(degree, self._conv(x), self._conv(y)):
            # position is to left of text, on baseline
            self._pdf.text(self._conv(x), self._conv(y), text)

    def circle(self, pos, r, color):
        (cx, cy) = pos
        topx = self._conv(cx - r)
        lefty = self._conv(cy - r)
        width = self._conv(2 * r)
        height = self._conv(2 * r)

        self._pdf.set_draw_color(0, 0, 0)
        self._pdf.set_fill_color(color.get_red_int(), color.get_green_int(), color.get_blue_int())
        self._pdf.ellipse(topx, lefty, width, height, 'FD')

    # x,y: center of circle
    # start: start angle in radians
    # end: end angle in radians
    # r: radius
    def circle_segment(self, x, y, start, end, r, color = style.BLACK,
                       stroke = 1, id = None):
        self._pdf.set_draw_color(color.get_red_int(), color.get_green_int(), color.get_blue_int())
        self._pdf.set_line_width(self._conv(stroke))

        leftx = x - r
        topy = y - r

        start = rad2deg(start)
        end = rad2deg(end)
        # x,y: not documented, presumably
        self._pdf.arc(self._conv(leftx), self._conv(topy),
                      a = self._conv(r * 2),
                      start_angle = start, end_angle = end)

    def draw_text_on_path(self, text, dunno, font_size):
        pass

    def line(self, start, end, color = style.BLACK, stroke = 1, dash = False):
        if dash:
            self._pdf.set_dash_pattern(dash = 0.8, gap = 1.2)

        self._pdf.set_draw_color(color.get_red_int(), color.get_green_int(), color.get_blue_int())
        self._pdf.set_line_width(self._conv(stroke))
        self._pdf.line(self._conv(start[0]), self._conv(start[1]),
                       self._conv(end[0]), self._conv(end[1]))
        self._pdf.set_dash_pattern(dash = 0, gap = 0)

    def _conv(self, pixels):
        # FIXME: convert pixels into mm
        return pixels / 20.0

    def _unconv(self, fakeunits):
        # FIXME: convert pixels into mm
        return fakeunits * 20.0

    def save(self):
        self._pdf.output(self._outfile)
