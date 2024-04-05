'''
Parser for style rules and object structure for the configuration.
'''

# ===========================================================================
# COLOR HANDLING

class Color:
    'Scale per color is 0..255'

    def __init__(self, red, green, blue):
        self._red = red
        self._green = green
        self._blue = blue

    def get_red_int(self):
        return self._red

    def get_green_int(self):
        return self._green

    def get_blue_int(self):
        return self._blue

    def to_html_rgb(self):
        return '#%s%s%s' % (tohex(self._red), tohex(self._green), tohex(self._blue))

    def to_rgb_tuple(self):
        return (self._red, self._green, self._red)

HEXDIGIT = '0123456789abcdef'
def tohex(num):
    return HEXDIGIT[int(num / 16)] + HEXDIGIT[num % 16]

BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)

# ===========================================================================
# CONFIG OBJECTS

class AbstractRule:

    def __init__(self, prop, setval):
        self._prop = prop
        self._setval = setval

    def update(self, node, data):
        if self._prop == 'textcolor':
            node.textcolor = self._setval
        elif self._prop == 'linecolor':
            node.linecolor = self._setval
        elif self._prop == 'linewidth':
            node.linestroke = int(self._setval)
        elif self._prop == 'dotcolor':
            node.dotcolour = self._setval
        elif self._prop == 'label':
            if data:
                node._label = data.get(self._setval) or node._label
        else:
            assert False, 'No implementation of rule property %s' % self._prop

class AllRule(AbstractRule):
    def __init__(self, prop, setval):
        AbstractRule.__init__(self, prop, setval)

    def matches(self, data):
        return True

    def __repr__(self):
        return '[Rule * -> %s=%s]' % (self._prop, self._setval)

class EqualsRule(AbstractRule):
    def __init__(self, field, value, prop, setval):
        AbstractRule.__init__(self, prop, setval)
        self._field = field
        self._value = value

    def matches(self, data):
        return data and data.get(self._field) == self._value

    def __repr__(self):
        return '[Rule %s=%s -> %s=%s]' % (self._field, self._value, self._prop, self._setval)

# ===========================================================================
# STYLE FILE PARSER

COLOR_PROPERTIES = set([
    'textcolor', 'linecolor', 'dotcolor'
])

def unhex(hexno):
    return hexdigit(hexno[0]) * 16 + hexdigit(hexno[1])

def hexdigit(digit):
    if digit in '0123456789':
        return ord(digit) - ord('0')
    elif digit in 'ABCDEF':
        return (ord(digit) - ord('A')) + 10
    elif digit in 'abcdef':
        return (ord(digit) - ord('a')) + 10

    assert False, 'Invalid hex digit "%s"' % digit

def parse_color(color):
    if color[0] == '#' and len(color) == 7:
        return Color(unhex(color[1 : 3]), unhex(color[3 : 5]), unhex(color[5 : ]))

    assert False, 'Unknown color "%s"' % color

def parse_style(filename):
    rules = []
    for line in open(filename):
        parts = [part.strip() for part in line.split(',')]

        if parts[0] == '*':
            creator = lambda prop, setval: AllRule(prop, setval)
        else:
            (field, value) = parts[0].split('=')
            creator = lambda prop, setval: EqualsRule(field, value, prop, setval)
        for part in parts[1 : ]:
            (prop, setval) = part.split('=')
            if prop in COLOR_PROPERTIES:
                setval = parse_color(setval)
            rules.append(creator(prop, setval))

    return rules

# ===========================================================================
# STYLE ENGINE

def apply_rules(tree, rules, data_by_id):
    for node in tree.get_all_nodes():
        data = data_by_id.get(node.get_label())
        for rule in rules:
            if rule.matches(data):
                rule.update(node, data)

    tree.upmerge_linestyle()

    text_legend = {rule._value : rule._setval for rule in rules
                   if rule._prop == 'textcolor' and hasattr(rule, '_value')}
    dot_legend = {rule._value : rule._setval for rule in rules
                   if rule._prop == 'dotcolor' and hasattr(rule, '_value')}
    return (text_legend, dot_legend)
