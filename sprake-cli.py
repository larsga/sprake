
import sys, csv, argparse
from sprake import newick, treeviz, style

def rename(infile, format):
    suffix = {
        'SVG' : '.svg',
        'PNG' : '.png',
        'PDF' : '.pdf',
    }[format]

    ix = infile.rfind('.')
    return infile[ : ix] + suffix

parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs = 1)
parser.add_argument('--style')
parser.add_argument('--data')
parser.add_argument('--mode', choices = ['tree', 'straight'], default = 'tree')
parser.add_argument('--format', default = 'SVG')
parser.add_argument('--dump', action='store_true')

args = parser.parse_args()

tree = newick.parse_string(open(args.infile[0]).read())
if args.dump:
    newick.dump_tree(tree)

text_legend = None
if args.style and args.data:
    rules = style.parse_style(args.style)
    data_by_id = {row['ID'] : row for row in csv.DictReader(open(args.data))}
    text_legend = style.apply_rules(tree, rules, data_by_id)

if args.mode == 'tree':
    treeviz.render_tree(
        rename(args.infile[0], args.format),
        tree,
        text_legend = text_legend,
        format = args.format
    )
else:
    treeviz.render_straight(
        rename(args.infile[0], args.format),
        tree,
        text_legend = text_legend,
        format = args.format
    )
