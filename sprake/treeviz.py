
import sys, math
from decimal import Decimal
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

def get_drawer(outfile, format, font_size):
    if format == 'SVG':
        from sprake.draw_svg import SVGDrawer
        drawer = SVGDrawer(outfile, font_size)
    elif format == 'PNG':
        from sprake.draw_png import PNGDrawer
        drawer = PNGDrawer(outfile, font_size)
    elif format == 'PDF':
        from sprake.draw_pdf import PDFDrawer
        drawer = PDFDrawer(outfile, font_size)
    else:
        assert False, 'Unknown format "%s"' % format
    return drawer

def render_tree(outfile, tree, dot_legend = None, text_legend = None,
                format = 'SVG'):
    leaves = tree.get_leaves()

    drawer = get_drawer(outfile, format, FONT_SIZE)
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
            # degree = degree - 180
            width = drawer.get_text_size(node.get_label())[1]
            (textx, texty) = ctx.get_circle_point(deg - (text_step * 0.5), radius + width + node.dotsize + 2)

        drawer.draw_text((textx, texty), node.get_label(), degree,
                         node.textcolor)
        drawer.circle((x, y), node.dotsize, node.dotcolour)

    # draw the tree
    empty_part = radius * EMPTY_CENTER_FACTOR
    h = tree.get_distance_height() if tree.get_distance() != None else tree.get_height()
    step = (radius - empty_part) / float(h)

    deg = tree.get_average_radians()
    drawer.line((center, center), ctx.get_circle_point(deg, empty_part),
                color = tree.linecolor, stroke = tree.linestroke)
    draw_node(tree, 1, empty_part, ctx, step)

    if dot_legend:
        draw_dot_legend(ctx, dot_legend)
    if text_legend:
        draw_text_legend(ctx, text_legend)

    drawer.save()

def draw_node(node, level, used_radius, ctx, step):
    if (not node.get_children()):
        if used_radius >= ctx.radius - node.dotsize:
            return

        deg2 = node.radians
        start = ctx.get_circle_point(deg2, used_radius)
        end = ctx.get_circle_point(deg2, ctx.radius - node.dotsize)
        ctx.drawer.line(start, end, stroke = node.linestroke,
                        color = node.linecolor)
        return

    lowest = 10
    highest = 0
    for child in node.get_children():
        deg2 = child.get_average_radians()

        length = step * (node.get_distance() if node.get_distance() != None else 1.0)
        inner = ctx.get_circle_point(deg2, used_radius - node.linestroke / 2.0)
        outer = ctx.get_circle_point(deg2, min(used_radius + length, ctx.radius - node.dotsize))
        ctx.drawer.line(inner, outer, stroke = node.linestroke,
                        color = node.linecolor)

        lowest = min(lowest, deg2)
        highest = max(highest, deg2)

        draw_node(child, level + 1, used_radius + length, ctx, step)

    r = used_radius
    (x, y) = (ctx.center, ctx.center)
    ctx.drawer.circle_segment(x, y, lowest, highest, r,
                              stroke = node.linestroke, color = node.linecolor)

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
    text_height = ctx.drawer.get_text_size('X')[0]
    offset = text_height * 2
    (x, y) = (offset, offset)
    dotsize = text_height / 4
    gap = text_height / 4.0
    max_width = 0

    for (name, color) in dot_legend.items():
        ctx.drawer.circle((x, y), dotsize, color)
        max_width = max(ctx.drawer.get_text_size(name), max_width)[1]
        ctx.drawer.draw_text((x + dotsize + (gap/2), y + dotsize * 0.7), name)

        y = int(y + gap + text_height)

    # FIXME: could draw a box around it?

def draw_text_legend(ctx, text_legend):
    text_height = ctx.drawer.get_text_size('X')[0]
    offset = text_height * 2
    (x, y) = (offset, offset)
    dotsize = text_height / 4
    gap = text_height / 3.0
    max_width = 0

    for (name, color) in text_legend.items():
        max_width = max(ctx.drawer.get_text_size(name)[1], max_width)
        ctx.drawer.draw_text((x, y + dotsize * 0.7), name, color = color)

        y = int(y + gap + text_height)

    # FIXME: could draw a box around it?

# ===== STRAIGHT RENDERING MODE

def render_straight(outfile, tree, dot_legend = None, text_legend = None,
                    format = 'SVG'):
    leaves = tree.get_leaves()

    drawer = get_drawer(outfile, format, FONT_SIZE)
    (text_height, text_width) = drawer.get_text_size('A')

    for node in tree.get_leaves():
        text_width = max(text_width, drawer.get_text_size(node.get_label())[1])

    gap = text_height * TEXT_SPACING_FACTOR
    margin = 20
    tree_width = 1000
    scale_height = text_height + gap * 4

    tree_height = (text_height + gap) * len(leaves)
    height = margin + scale_height + tree_height + margin
    width = margin + tree_width + gap + text_width + margin

    drawer.create(height, width)

    if tree.get_distance() != None:
        draw_scale = True
        (biggest, increment) = calibrate_scale(tree.get_distance_height())
    else:
        draw_scale = False
        biggest = tree.get_height()
        increment = None

    # draw the leaves
    x = margin + tree_width + gap
    for (ix, leaf) in enumerate(leaves):
        y = margin + scale_height + gap * ix + text_height * (ix + 1)
        drawer.draw_text((x, y), leaf.get_label(), 0, leaf.textcolor)

    # draw the tree
    right_edge = margin + tree_width
    vstep = text_height + gap
    hstep = float(tree_width) / biggest # use biggest to match scale line
    y = int(round(margin + scale_height + 0.5 * tree_height))
    hpos = biggest - (tree.get_distance_height() if tree.get_distance() != None else (tree.get_height() + 1))
    draw_straight_node(drawer, tree, margin, y, hpos, vstep, hstep, right_edge)

    # draw the scale (if we have distances in the tree)
    if draw_scale:
        btmy = margin + scale_height
        drawer.line((margin, btmy), (margin + tree_width, btmy))
        v = biggest
        while v >= 0.0:
            x = margin + int(round((1.0 - (v / biggest)) * tree_width))
            drawer.line((x, btmy), (x, btmy - gap * 3))

            txt = nicely_float_to_str(v)
            w2 = int(round(drawer.get_text_size(txt)[1] / 2.0))
            drawer.draw_text((x - w2, btmy - gap * 4), txt)

            v -= increment

    drawer.save()

def nicely_float_to_str(v):
    return str(Decimal(str(v)).quantize(Decimal('0.1')))

# 0 is assumed smallest
def calibrate_scale(topval):
    scale = 10 # factor to get to 1.0

    biggest = math.ceil(topval * scale) / scale # largest number on scale
    increments = 1.0 / scale
    return (biggest, increments)

def draw_straight_node(drawer, node, margin, y, depth, vstep, hstep, right_edge):
    dist = node.get_distance() if node.get_distance() != None else 1.0

    # adjust by linestroke to make overlaps look better
    x1 = (margin + depth * hstep) - (node.linestroke / 2.0)
    x2 = margin + (depth + dist) * hstep
    drawer.line((x1, y), (x2, y),
                stroke = node.linestroke, color = node.linecolor)

    # this is the top of the vertical area the children fill
    depth += dist
    cy = y - int(round(vstep * len(node.get_leaves()) / 2))
    for child in node.get_children():
        ydelta = int(round(vstep * len(child.get_leaves()) / 2))
        cy += ydelta
        drawer.line((x2, y), (x2, cy), stroke = child.linestroke,
                color = child.linecolor)
        draw_straight_node(drawer, child, margin, cy, depth, vstep, hstep, right_edge)

        cy += ydelta

    if not node.get_children():
        drawer.line((x2, y), (right_edge, y), stroke = node.linestroke,
                    color = node.linecolor)
