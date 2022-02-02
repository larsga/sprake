'''
Parser for Newick format files.
'''

import sys
from sprake import style

# distance here means distance to parent
class NewickNode:

    def __init__(self, parent, label = None, distance = None, bootstrap = None):
        self._parent = parent
        self._children = []
        self._label = label
        self._distance = distance
        self._bootstrap = bootstrap
        self._graph_init()

    def get_parent(self):
        return self._parent

    def has_children(self):
        return len(self._children) > 0

    def get_children(self):
        return self._children

    def get_label(self):
        return self._label

    def get_distance(self):
        return self._distance

    def get_bootstrap(self):
        return self._bootstrap

    # max sum of distances to bottom
    def get_distance_height(self):
        if not self._children:
            return self._distance
        return max([ch.get_distance_height() for ch in self._children]) + self._distance

    def add_child(self, child):
        self._children.append(child)

    def set_label(self, label):
        self._label = label

    def set_distance(self, distance):
        self._distance = distance

    def set_bootstrap(self, bootstrap):
        self._bootstrap = bootstrap

    def get_leaves(self):
        thelist = []
        self._get_leaves(thelist)
        return thelist

    def _get_leaves(self, thelist):
        if len(self._children) == 0:
            thelist.append(self)
        else:
            for ch in self._children:
                ch._get_leaves(thelist)

    def get_all_nodes(self):
        nodes = []
        self._get_all_nodes(nodes)
        return nodes

    def _get_all_nodes(self, nodes):
        nodes.append(self)
        for ch in self._children:
            ch._get_all_nodes(nodes)

    def get_height(self):
        if not self._children:
            return 0
        return max([ch.get_height() for ch in self._children]) + 1

    def find_common_parent_of(self, criterion):
        own = self._count_leaves_satisfying(criterion)
        for child in self.get_children():
            sub = child._count_leaves_satisfying(criterion)
            if sub > 0 and sub < own:
                return self
            elif sub == own:
                return child.find_common_parent_of(criterion)

    def _count_leaves_satisfying(self, criterion):
        return len([leaf for leaf in self.get_leaves()
                    if criterion(leaf)])

    # graphical stuff

    def _graph_init(self):
        # set during drawing
        self.degrees = None
        self.radians = None

        # configurable graphical styling
        self.dotcolour = style.WHITE
        self.dotsize = 5
        self.linestroke = 1
        self.linecolor = style.BLACK
        self.textcolor = style.BLACK
        self.bannercolor = None # node title becomes banner title

    def get_radian_span(self):
        leaves = [l.radians for l in self.get_leaves()]
        return (min(leaves), max(leaves))

    def get_average_radians(self):
        leaves = self.get_leaves()
        return sum([l.radians for l in leaves]) / len(leaves)

    def upmerge_linestyle(self):
        if not self._children:
            return

        for child in self._children:
            child.upmerge_linestyle()

        style = (self._children[0].linestroke, self._children[0].linecolor)
        for child in self._children[1 : ]:
            if style != (child.linestroke, child.linecolor):
                style = None
                break

        if style:
            (self.linestroke, self.linecolor) = style

def scan_while_not(data, pos, end_marker):
    while data[pos] not in end_marker:
        pos += 1
    return pos

def parse_string(data):
    pos = 0
    root = None
    current = None
    while data[pos] != ';':
        if data[pos] == '(':
            node = NewickNode(current)
            if current:
                current.add_child(node)
            current = node
            if not root:
                root = node
            pos += 1

        elif data[pos] == ')':
            pos += 1

            ix = scan_while_not(data, pos, ':,);')
            if ix != pos: # there was a label
                current.set_label(data[pos : ix])
                pos = ix

            if data[pos] == ':':
                ix = scan_while_not(data, pos, ',);[')

                if data[ix] == '[':
                    ix2 = scan_while_not(data, ix+1, ']')
                    current.set_bootstrap(int(data[ix + 1 : ix2]))

                current.set_distance(float(data[pos+1 : ix]))
                # print float(data[pos+1 : ix]), current.get_label(), current

                if data[ix] == '[':
                    pos = ix2 + 1
                else:
                    pos = ix

                if pos < len(data) and data[pos] == ',':
                    pos += 1

            current = current.get_parent()

        elif data[pos] == ',':
            pos += 1

        else:
            ix = scan_while_not(data, pos, ':,)')
            if data[ix] == ':':
                label = data[pos : ix] or None
                pos = ix + 1
                ix = scan_while_not(data, pos, ',)')
                distance = float(data[pos : ix])
            else:
                label = data[pos : ix] or None
                distance = None

            pos = ix
            node = NewickNode(current, label, distance)
            current.add_child(node)

            if data[pos] == ',':
                pos += 1

            # pos now on either '(', ')' or a label

    return root

def dump_tree(node, indent = 0):
    print('%s%s %s' % (' ' * indent, node._label, node._distance))
    for child in node._children:
        dump_tree(child, indent + 2)

def to_newick(outf, tree):
    _write_node(outf, tree)
    outf.write(';')

def _write_node(outf, node):
    if node.has_children():
        outf.write('(')

        for (ix, child) in enumerate(node.get_children()):
            if ix > 0:
                outf.write(',')
            _write_node(outf, child)

        outf.write(')')

        if node.get_label():
            outf.write(node.get_label())
        if node.get_distance() != None:
            outf.write(':')
            outf.write(float_to_str(node.get_distance()))
    else:
        if node.get_label():
            outf.write(node.get_label())
        if node.get_distance() != None:
            outf.write(':')
            outf.write(float_to_str(node.get_distance()))

def float_to_str(f):
    # copied from StackOverflow. embarrassing that this is necessary
    float_string = repr(f)
    if 'e' in float_string:  # detect scientific notation
        digits, exp = float_string.split('e')
        digits = digits.replace('.', '').replace('-', '')
        exp = int(exp)
        zero_padding = '0' * (abs(int(exp)) - 1)  # minus 1 for decimal point in the sci notation
        sign = '-' if f < 0 else ''
        if exp > 0:
            float_string = '{}{}{}.0'.format(sign, digits, zero_padding)
        else:
            float_string = '{}0.{}{}'.format(sign, zero_padding, digits)
    return float_string

if __name__ == '__main__':
    tree = parse_string(open(sys.argv[1]).read())
    dump_tree(tree)
