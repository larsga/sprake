
from sprake import style

def test_color_1():
    color = style.parse_color('#4dab4d')
    assert '#4dab4d' == color.to_html_rgb()

def test_color_2():
    color = style.parse_color('#b3059e')
    assert '#b3059e' == color.to_html_rgb()
