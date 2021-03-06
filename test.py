import sys

from suffix_tree import *
from graph import *
from parser import *
from utils import *
from index import *

def suffix_tree_test():
	tree = SuffixTree()
	tree.add_word('AAAA', 1)
	assert 1 == len(tree.lookup('AAAA'))
	assert 3 == tree.lookup('AAAA')[1]
	tree.add_word('AAAT', 2)
	assert 2 == len(tree.lookup('AAAA'))
	assert 2 == tree.lookup('AAAA')[2]
	assert 2 == len(tree.lookup('AAA'))
	assert 2.5 == tree.lookup('AAA')[1]
	assert 2.5 == tree.lookup('AAA')[2]
	tree.add_word('AAAC', 3)
	assert 3 == len(tree.lookup('AAAG'))
	assert 2 == tree.lookup('AAAG')[1]
	assert 2 == tree.lookup('AAAG')[2]
	assert 2 == tree.lookup('AAAG')[3]
	assert 3 == tree.lookup('AAAA')[1]
	assert 0 == len(tree.lookup('TTTTTTT'))
	assert 3 == len(tree.lookup('AAAATTT'))
	assert 3 == tree.lookup('AAAATTT')[1]
	assert 0 == len(tree.lookup('AGGG'))

	return tree

def graph_test():
	graph = parse_reference_genome('data/test.fasta')
	parse_VCF_variants(graph, 'data/min.vcf')

	return graph

def alignment():
	sys.setrecursionlimit(10000)
	graph = parse_reference_genome('data/hla_b27/sequences/ref.fasta')

	name, alignment1, alignment2 = parse_global_alignment('data/hla_b27/alignments/ref-01.alignment')
	alignment = generate_graph_from_alignment(alignment2, name, graph)
	graph.insert_global_alignment(alignment1, alignment, name)

	for i in range(1, len(graph.nodes) - 1):
		print('Got ' + str(graph.get_node_by_index(i).index) + ' on ' + str(i))
		assert i == graph.get_node_by_index(i).index

	index = generate_left_right_index(graph)
	mappings = index.map_sequence('ACGGACGGAGAACCGAGA')

def critical_test(graph):
	assert False == graph.is_index_critical(7)
	assert True == graph.is_index_critical(12)
	assert True == graph.is_index_critical(15)
	assert True == graph.is_index_critical(16)

if __name__ == '__main__':
	#tree = suffix_tree_test()
	graph = graph_test()
	#critical_test(graph)
	alignment()