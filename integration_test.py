
import os, string, csv
from sprake import newick, treeviz, style

STYLE = 'examples/scer-x-skud.style'
DATA = 'examples/scer-x-skud.csv'
NWK = 'examples/scer-x-skud.nwk'

# pytest will automatically supply tmp_path
def test_pdf_tree(tmp_path):
    run('PDF', True, tmp_path)

def test_pdf_straight(tmp_path):
    run('PDF', False, tmp_path)

def test_png_tree(tmp_path):
    run('PNG', True, tmp_path)

def test_png_straight(tmp_path):
    run('PNG', False, tmp_path)

def test_svg_tree(tmp_path):
    run('SVG', True, tmp_path)

def test_svg_straight(tmp_path):
    run('SVG', False, tmp_path)

def run(format, tree_mode, tmp_path):
    tree = newick.parse_string(open(NWK).read())
    rules = style.parse_style(STYLE)
    data_by_id = {row['ID'] : row for row in csv.DictReader(open(DATA))}
    (text_legend, dot_legend) = style.apply_rules(tree, rules, data_by_id)

    if tree_mode:
        treeviz.render_tree(
            os.path.join(tmp_path, 'output.' + format),
            tree,
            text_legend = text_legend,
            format = format
        )
    else:
        treeviz.render_straight(
            os.path.join(tmp_path, 'output.' + format),
            tree,
            text_legend = text_legend,
            format = format
        )
