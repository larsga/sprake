
import string
from sprake import style

UPPERCASE = ''.join(chr(i) for i in range(65, 91))
LOWERCASE = ''.join(chr(i) for i in range(97, 123))
DIGITS    = string.digits

class SVGDrawer:

    def __init__(self, outfile, fontsize):
        self._fontsize = fontsize
        self._out = open(outfile, 'w')

    def get_font_size(self):
        return self._fontsize

    def get_text_size(self, text):
        spacer = 0.06
        spaces = max(0, len(text) - 1) * spacer * self._fontsize

        width = 0
        for ch in text:
            if ch in 'O52':
                width += 0.9
            elif ch in 'MCGE-0':
                width += 0.8
            elif ch in 'QBPR_SDA61483 ':
                width += 0.75
            elif ch in '':
                width += 0.6
            elif ch in '9I':
                width += 0.5
            elif ch in UPPERCASE or ch in '#nma' or ch in DIGITS:
                width += 0.38
            elif ch in 'il(),:[]':
                width += 0.2
            elif ch in LOWERCASE:
                width += 0.3
            else:
                width += 0.4

        return (self._fontsize, self._fontsize * width + spaces)

    def create(self, height, width, background_color = None):
        bkg = ''
        if background_color:
            bkg = ' style="background-color: %s"' % background_color.to_html_rgb()
        self._out.write('''
          <svg xmlns="http://www.w3.org/2000/svg"
               width="%s" height="%s" viewBox="0 0 %s %s"%s>
            <style>
              line:hover { stroke-width: 5 }
              path:hover { stroke-width: 5 }
            </style>
        ''' % (width, height, width, height, bkg))

    def circle(self, pos, r, color = style.BLACK, stroke = 1):
        color = color.to_html_rgb()
        (cx, cy) = pos
        self._out.write('''
      <circle cx="%s" cy="%s" r="%s"
              stroke="%s" stroke-width="%s" fill="%s"/>
    ''' % (cx, cy, r, color, stroke, color))

    def line(self, start, end, color = style.BLACK, stroke = 1):
        (x1, y1) = start
        (x2, y2) = end
        self._out.write('''
          <line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"/>
        ''' % (x1, y1, x2, y2, color.to_html_rgb(), stroke))

    def circle_segment(self, start, end, r, color = style.BLACK, stroke = 1,
                       id = None):
        (sx, sy) = start
        (ex, ey) = end

        id = ' id="%s"' % id if id else ''

        # M = moveto
        # A = arc (x-radius y-radius x-rotation large-arc-flag sweep-flag
        #          x y)
        self._out.write('''
      <path d="M %s %s A %s %s 0 0 0 %s %s"
            fill="none" stroke="%s" stroke-width="%s"%s/>
        ''' % (ex, ey, r, r, sx, sy, color.to_html_rgb(), stroke, id))

    def draw_text(self, pos, text, degree = 0, color = style.BLACK):
        degree = degree * -1
        (x, y) = pos
        self._out.write('  <text x="%s" y="%s" transform="rotate(%s %s %s)" style="fill: %s; font-size: %spt">%s</text>\n' %
                        (x, y, degree, x, y, color.to_html_rgb(), self._fontsize, text))

    def draw_text_on_path(self, text, curve_id, fontsize = None):
        self._out.write('''
          <text style="font-size: %spt">
            <textPath href="#%s" side="right" startOffset="40%%">%s</textPath>
          </text>
        ''' % (fontsize, curve_id, text))

    def save(self):
        self._out.write('</svg>\n')
        self._out.close()
