
import os, random, string, shutil, csv
from sprake import newick, treeviz, style

STYLE = 'examples/scer-x-skud.style'
DATA = 'examples/scer-x-skud.csv'
NWK = 'examples/scer-x-skud.nwk'

testdir = 'tests_' + ''.join([random.choice(string.ascii_letters) for ix in range(10)])
def setup():
    os.mkdir(testdir)

def test_pdf_tree():
    run('PDF', True)

def test_pdf_straight():
    run('PDF', False)

def test_png_tree():
    run('PNG', True)

def test_png_straight():
    run('PNG', False)

def test_svg_tree():
    run('SVG', True)

def test_svg_straight():
    run('SVG', False)

def teardown():
    pass #shutil.rmtree(testdir)

def run(format, tree):
    tree = newick.parse_string(open(NWK).read())
    rules = style.parse_style(STYLE)
    data_by_id = {row['ID'] : row for row in csv.DictReader(open(DATA))}
    text_legend = style.apply_rules(tree, rules, data_by_id)

    if tree:
        treeviz.render_tree(
            os.path.join(testdir, 'output.' + format),
            tree,
            text_legend = text_legend,
            format = format
        )
    else:
        treeviz.render_straight(
            os.path.join(testdir, 'output.' + format),
            tree,
            text_legend = text_legend,
            format = format
        )
