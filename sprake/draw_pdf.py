
from sprake import style

import fpdf
class PDFDrawer:

    def __init__(self, outfile, fontsize):
        self._outfile = outfile
        self._pdf = fpdf.FPDF('P', 'mm', 'A4')
        self._pdf.add_page()

    def get_text_size(self, text):
        # FIXME: implement!
        return (10, 10)

    def create(self, height, width):
        pass

    def draw_text(self, pos, text, degree = 0, color = style.BLACK):
        # FIXME: implement!
        pass

    def circle(self, pos, r, color):
        (cx, cy) = pos
        topx = self._conv(cx - r)
        lefty = self._conv(cy - r)
        width = self._conv(2 * r)
        height = self._conv(2 * r)

        self._pdf.set_fill_color(color.get_red_int(), color.get_green_int(), color.get_blue_int())
        self._pdf.ellipse(topx, lefty, width, height, 'F')

    def circle_segment(self, start, end, r, color = style.BLACK, stroke = 1,
                       id = None):
        self._pdf.set_draw_color(color.get_red_int(), color.get_green_int(), color.get_blue_int())
        # FIXME: start/end: this doesn't work

    def line(self, start, end, color = style.BLACK, stroke = 1):
        self._pdf.set_draw_color(color.get_red_int(), color.get_green_int(), color.get_blue_int())
        self._pdf.set_line_width(0.2)
        self._pdf.line(self._conv(start[0]), self._conv(start[1]),
                       self._conv(end[0]), self._conv(end[1]))

    def _conv(self, pixels):
        # FIXME: convert pixels into mm
        return pixels / 20.0

    def save(self):
        self._pdf.output(self._outfile, 'F')
