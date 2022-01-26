
from sprake import style
from nose.tools import eq_

def test_color_1():
    color = style.parse_color('#4dab4d')
    eq_('#4dab4d', color.to_html_rgb())

def test_color_2():
    color = style.parse_color('#b3059e')
    eq_('#b3059e', color.to_html_rgb())
