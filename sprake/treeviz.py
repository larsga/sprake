
import sys, math
from sprake import newick, style

SCALE_FACTOR        = 0.35
FONT_SIZE           = 12
MIN_CIRCUMFERENCE   = 300
EMPTY_CENTER_FACTOR = 0.25
TEXT_SPACING_FACTOR = 0.1

# draw_png.PNGDrawer
# draw_svg.SVGDrawer # no deps
# draw_pdf.PDFDrawer

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
        from sprake.draw_svg import SVGDrawer
        drawer = SVGDrawer(outfile, FONT_SIZE)
    elif format == 'PNG':
        from sprake.draw_png import PNGDrawer
        drawer = PNGDrawer(outfile, FONT_SIZE)
    elif format == 'PDF':
        from sprake.draw_pdf import PDFDrawer
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
