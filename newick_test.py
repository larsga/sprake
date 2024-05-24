# encoding=utf-8

import io, unittest
from sprake import newick

def test_basic():
    tree = newick.parse_string('(A,B,(C,D));')
    assert len(tree.get_children()) == 3
    assert tree.get_label() == None

    (a, b, parent) = tree.get_children()
    assert a.get_label() == 'A'
    assert b.get_label() == 'B'
    assert parent.get_label() == None
    assert len(parent.get_children()) == 2

    (c, d) = parent.get_children()
    assert c.get_label() == 'C'
    assert d.get_label() == 'D'

def test_basic_serialization():
    serialize_check('(A,B,(C,D));')

def test_unlabeled_distance():
    tree = newick.parse_string('(:0.1,:0.2,(:0.3,:0.4):0.5);')
    assert len(tree.get_children()) == 3
    assert tree.get_label() == None
    assert tree.get_distance() == None

    (a, b, parent) = tree.get_children()
    assert a.get_label() == None, repr(a.get_label())
    assert a.get_distance() == 0.1
    assert b.get_label() == None
    assert b.get_distance() == 0.2
    assert parent.get_label() == None
    assert len(parent.get_children()) == 2
    assert parent.get_distance() == 0.5

    (c, d) = parent.get_children()
    assert c.get_label() == None
    assert c.get_distance() == 0.3
    assert d.get_label() == None
    assert d.get_distance() == 0.4

def test_unlabeled_distance_serialize():
    serialize_check('(:0.1,:0.2,(:0.3,:0.4):0.5);')

def test_unlabeled_distance2():
    tree = newick.parse_string('(:0.1,:0.2,(:0.3,:0.4):0.5):0.0;')
    assert len(tree.get_children()) == 3
    assert tree.get_label() == None
    assert tree.get_distance() == 0.0

    (a, b, parent) = tree.get_children()
    assert a.get_label() == None, repr(a.get_label())
    assert a.get_distance() == 0.1
    assert b.get_label() == None
    assert b.get_distance() == 0.2
    assert parent.get_label() == None
    assert len(parent.get_children()) == 2
    assert parent.get_distance() == 0.5

    (c, d) = parent.get_children()
    assert c.get_label() == None
    assert c.get_distance() == 0.3
    assert d.get_label() == None
    assert d.get_distance() == 0.4

def test_unlabeled_distance2_serialize():
    serialize_check('(:0.1,:0.2,(:0.3,:0.4):0.5):0.0;')

def test_labeled_distance():
    tree = newick.parse_string('(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);')
    assert len(tree.get_children()) == 3
    assert tree.get_label() == None
    assert tree.get_distance() == None

    (a, b, parent) = tree.get_children()
    assert a.get_label() == 'A', repr(a.get_label())
    assert a.get_distance() == 0.1
    assert b.get_label() == 'B'
    assert b.get_distance() == 0.2
    assert parent.get_label() == None
    assert len(parent.get_children()) == 2
    assert parent.get_distance() == 0.5

    (c, d) = parent.get_children()
    assert c.get_label() == 'C'
    assert c.get_distance() == 0.3
    assert d.get_label() == 'D'
    assert d.get_distance() == 0.4

def test_labeled_distance_serialize():
    serialize_check('(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);')

def test_real_example():
    tree = newick.parse_string('((wine004:0.00017,(spirits011:0.00012,(AMS_5.re:0.00010,AIL_3.re:0.00012):0.00002):0.00002):0.00031,AII_1.re:0.00050);')
    assert len(tree.get_children()) == 2
    assert tree.get_label() == None
    assert tree.get_distance() == None

    (a, aii) = tree.get_children()
    assert a.get_label() == None
    assert a.get_distance() == 0.00031
    assert aii.get_label() == 'AII_1.re'
    assert aii.get_distance() == 0.0005

    (wine, b) = a.get_children()
    assert wine.get_label() == 'wine004'
    assert wine.get_distance() == 0.00017
    assert b.get_label() == None
    assert b.get_distance() == 0.00002

    (spirits, c) = b.get_children()
    assert spirits.get_label() == 'spirits011'
    assert spirits.get_distance() == 0.00012
    assert c.get_label() == None
    assert c.get_distance() == 0.00002

    (ams, ail) = c.get_children()
    assert ams.get_label() == 'AMS_5.re'
    assert ams.get_distance() == 0.0001
    assert ail.get_label() == 'AIL_3.re'
    assert ail.get_distance() == 0.00012

def test_real_example_serialize():
    serialize_check('((wine004:0.00017,(spirits011:0.00012,(AMS_5.re:0.0001,AIL_3.re:0.00012):0.00002):0.00002):0.00031,AII_1.re:0.0005);')

def test_other_real():
    tree = newick.parse_string('((BE017,(ABI1525,ABI1606)),(BR005,XXX));')
    assert len(tree.get_children()) == 2
    assert tree.get_label() == None
    assert tree.get_distance() == None

def test_other_real_serialize():
    serialize_check('((BE017,(ABI1525,ABI1606)),(BR005,XXX));')

def test_naming_internal_nodes():
    tree = newick.parse_string('(A,B,(C,D)E)F;')
    assert len(tree.get_children()) == 3
    assert tree.get_label() == 'F'
    assert tree.get_distance() == None

    (a, b, e) = tree.get_children()
    assert a.get_label() == 'A'
    assert a.get_distance() == None
    assert len(a.get_children()) == 0

    assert b.get_label() == 'B'
    assert b.get_distance() == None
    assert len(b.get_children()) == 0

    assert e.get_label() == 'E'
    assert e.get_distance() == None
    assert len(e.get_children()) == 2

    (c, d) = e.get_children()
    assert c.get_label() == 'C'
    assert c.get_distance() == None
    assert len(c.get_children()) == 0

    assert d.get_label() == 'D'
    assert d.get_distance() == None
    assert len(d.get_children()) == 0

def test_naming_internal_nodes_serialize():
    serialize_check('(A,B,(C,D)E)F;')

def test_bootstrap_vales():
    tree = newick.parse_string('((Escherichia_coli_O6:0.00000,Escherichia_coli_K12:0.00022)I2:0.00022[76],(Shigella_flexneri_2a_2457T:0.00000,Shigella_flexneri_2a_301:0.00000)I3:0.00266[100])I4:0.00000[75];')

    assert len(tree.get_children()) == 2
    assert tree.get_label() == 'I4'
    assert tree.get_distance() == 0
    assert tree.get_bootstrap() == 75

def test_non_ascii():
    tree = newick.parse_string('(A,Bøø,(C,D));')
    assert len(tree.get_children()) == 3
    assert tree.get_label() == None

    (a, b, parent) = tree.get_children()
    assert a.get_label() == 'A'
    assert b.get_label() == 'Bøø'
    assert parent.get_label() == None
    assert len(parent.get_children()) == 2

    (c, d) = parent.get_children()
    assert c.get_label() == 'C'
    assert d.get_label() == 'D'

# ===========================================================================
# utilities

def serialize_check(input):
    tree = newick.parse_string(input)

    outf = io.StringIO()
    output = newick.to_newick(outf, tree)
    assert input == outf.getvalue()
