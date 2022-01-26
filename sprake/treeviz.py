
import sys, math, string
from sprake import newick, style

SCALE_FACTOR        = 0.35
FONT_SIZE           = 12
MIN_CIRCUMFERENCE   = 300
EMPTY_CENTER_FACTOR = 0.25
TEXT_SPACING_FACTOR = 0.1

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

import fpdf
class PDFDrawer:

    def __init__(self, outfile, fontsize):
        self._outfile = outfile
        self._pdf = fpdf.FPDF('P', 'mm', 'A4')
        self._pdf.add_page()

    def get_text_size(self, text):
        return (10, 10)

    def create(self, height, width):
        pass

    def draw_text(self, pos, text, degree = 0, color = style.BLACK):
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
        # start/end: this doesn't work

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

def get_circle_point(cx, cy, deg, r):
    return (int(round(cx + math.cos(deg) * r)),
            int(round(cy + math.sin(deg) * r)))

class DrawingContext:

    def __init__(self, radius, center, drawer):
        self.radius = radius
        self.center = center
        self.drawer = drawer

    def get_circle_point(self, deg, r):
        return get_circle_point(self.center, self.center, deg, r)

def render_tree(outfile, tree, dot_legend = None, text_legend = None,
                format = 'SVG'):
    leaves = tree.get_leaves()

    if format == 'SVG':
        drawer = SVGDrawer(outfile, FONT_SIZE)
    elif format == 'PNG':
        drawer = PNGDrawer(outfile, FONT_SIZE)
    elif format == 'PDF':
        drawer = PDFDrawer(outfile, FONT_SIZE)
    else:
        assert False

    (text_height, text_width) = drawer.get_text_size('A')

    for node in tree.get_leaves():
        text_width = max(text_width, drawer.get_text_size(node.get_label())[1])
    text_width = max(text_width, 200) # ensure room for legend

    gap = text_height * TEXT_SPACING_FACTOR

    circumference = len(leaves) * (text_height + gap) * SCALE_FACTOR
    circumference = max(MIN_CIRCUMFERENCE, circumference)

    diameter = circumference / math.pi
    width = int(circumference + (text_width * 2) + gap * 2) + 1
    drawer.create(width, width)

    center = width / 2
    radius = circumference / 2
    deg_step = (math.pi * 2) / len(leaves)
    ctx = DrawingContext(radius, center, drawer)

    # degrees to step further from node to center text on node
    text_step = ((math.pi * text_height) / circumference) * 0.3

    for ix in range(len(leaves)):
        deg = (deg_step * ix)

        node = leaves[ix]
        (x, y) = ctx.get_circle_point(deg, radius)
        node.x = x
        node.y = y
        (textx, texty) = ctx.get_circle_point(deg + text_step, radius + node.dotsize + 2)

        degree = 360 - (deg / (math.pi*2)) * 360
        node.degrees = degree
        node.radians = deg
        if degree > 90 and degree < 270:
            degree = degree - 180
            width = drawer.get_text_size(node.get_label())[1]
            (textx, texty) = ctx.get_circle_point(deg - (text_step * 0.5), radius + width + node.dotsize + 2)

        drawer.draw_text((textx, texty), node.get_label(), degree,
                         node.textcolor)
        drawer.circle((x, y), node.dotsize, node.dotcolour)

    # draw the tree
    empty_part = radius * EMPTY_CENTER_FACTOR
    step = (radius - empty_part) / float(tree.get_height() + 1)

    deg = tree.get_average_radians()
    drawer.line((center, center), ctx.get_circle_point(deg, step + empty_part),
                color = tree.linecolor, stroke = tree.linestroke)
    draw_node(tree, 1, step + empty_part, ctx)

    if dot_legend:
        draw_dot_legend(ctx, dot_legend)
    if text_legend:
        draw_text_legend(ctx, text_legend)

    drawer.save()

def draw_node(node, level, used_radius, ctx):
    if (not node.get_children()):
        if used_radius >= ctx.radius - node.dotsize:
            return
        deg2 = node.radians
        start = ctx.get_circle_point(deg2, used_radius)
        end = ctx.get_circle_point(deg2, ctx.radius - node.dotsize)
        ctx.drawer.line(start, end, stroke = node.linestroke,
                        color = node.linecolor)
        return

    remaining_radius = ctx.radius - used_radius
    height = node.get_height()
    step = remaining_radius / float(height)

    lowest = 10
    highest = 0
    for child in node.get_children():
        deg2 = child.get_average_radians()
        inner = ctx.get_circle_point(deg2, used_radius)
        outer = ctx.get_circle_point(deg2, min(used_radius + step, ctx.radius - node.dotsize))
        ctx.drawer.line(inner, outer, stroke = node.linestroke,
                        color = node.linecolor)

        lowest = min(lowest, deg2)
        highest = max(highest, deg2)

        draw_node(child, level + 1, used_radius + step, ctx)

    r = used_radius
    start = ctx.get_circle_point(lowest, r)
    end = ctx.get_circle_point(highest, r)
    ctx.drawer.circle_segment(start, end, r, stroke = node.linestroke,
                              color = node.linecolor)

    if node.bannercolor:
        r = ctx.radius + ctx.drawer.get_text_size('This is a reasonably long text, I think [Key] (foo)')[1]
        (lowest, highest) = node.get_radian_span()
        start = ctx.get_circle_point(lowest, r)
        end = ctx.get_circle_point(highest, r)

        theid = 'id%s' % id(node)
        ctx.drawer.circle_segment(start, end, r, stroke = ctx.drawer.get_font_size() * 4,
                                  color = node.bannercolor, id = theid)
        ctx.drawer.draw_text_on_path(node.get_label(), theid, ctx.drawer.get_font_size() * 2)

def draw_dot_legend(ctx, dot_legend):
    offset = FONT_SIZE * 2
    (x, y) = (offset, offset)
    dotsize = FONT_SIZE / 4
    gap = FONT_SIZE / 4.0
    max_width = 0

    for (name, color) in dot_legend.items():
        ctx.drawer.circle((x, y), dotsize, color)
        max_width = max(ctx.drawer.get_text_size(name), max_width)[1]
        ctx.drawer.draw_text((x + dotsize + (gap/2), y + dotsize * 0.7), name)

        y = int(y + gap + FONT_SIZE)

    # FIXME: could draw a box around it?

def draw_text_legend(ctx, text_legend):
    offset = FONT_SIZE * 2
    (x, y) = (offset, offset)
    dotsize = FONT_SIZE / 4
    gap = FONT_SIZE / 3.0
    max_width = 0

    for (name, color) in text_legend.items():
        max_width = max(ctx.drawer.get_text_size(name)[1], max_width)
        ctx.drawer.draw_text((x, y + dotsize * 0.7), name, color = color)

        y = int(y + gap + FONT_SIZE)

    # FIXME: could draw a box around it?
