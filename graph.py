from random import *

from constants import *
from region import *

class Graph:
	def __init__(self, id, description, species):
		self.id = id
		self.description = description
		self.species = species
		self.head = Node(HEAD_VALUE, HEAD_INDEX)
		self.tail = Node(TAIL_VALUE, TAIL_INDEX)
		self.current_path = REFERENCE_PATH_INDEX
		self.current_index = 0
		self.paths = [REFERENCE_PATH_INDEX]
		self.nodes = [self.head, self.tail]

	def add_node(self, node):
		length = len(self.nodes)
		del self.nodes[-1]
		if (node.index != len(self.nodes)):
			node.index = len(self.nodes)
		self.nodes.append(node)
		self.nodes.append(self.tail)
		self.current_index += 1

	def get_node_by_index(self, index):
		if (index == float('inf')):
			return self.tail

		if (index < len(self.nodes)):
			return self.nodes[index]

		return False

	def get_reference_genome_representation(self):
		reference = self.get_reference_genome()

		s = ""
		for node in reference[1:-1]:
			s += node.value

		return s

	def get_reference_genome(self):
		reference = []
		node = self.head

		while (node):
			reference.append(node)
			node = node.get_neighbour_by_path(REFERENCE_PATH_INDEX)

		return reference

	def add_path(self, start, stop_index, old_path, new_path):
		if not new_path in self.paths:
			self.paths.append(new_path)

		if (start.has_path(new_path)):
			return self.get_node_by_index(stop_index)

		curr = start
		while curr:
			temp = curr.get_neighbour_by_path(old_path)
			edge = curr.get_edge(temp)

			if not (new_path in edge.paths):
				edge.paths.append(new_path)
			curr = temp

			if (curr.index == stop_index):
				return curr

		return False

	def add_SNP(self, value, index, path):
		if not path in self.paths:
			self.paths.append(path)

		prev = self.add_path(self.head, index - 1, REFERENCE_PATH_INDEX, path)
		next = prev.get_neighbour_by_path(REFERENCE_PATH_INDEX).get_neighbour_by_path(REFERENCE_PATH_INDEX)

		old_snp = prev.get_neighbour_by_base(value)
		if old_snp:
			prev.get_edge(old_snp).paths.append(path)
			old_snp.get_edge(next).paths.append(path)
		else:
			new = Node(value, self.current_index)
			self.add_node(new)
			prev.add_neighbour(new, path)
			new.add_neighbour(next, path)

		self.add_path(next, TAIL_INDEX, REFERENCE_PATH_INDEX, path)

	def add_deletion(self, length, index, path):
		if not path in self.paths:
			self.paths.append(path)

		prev = self.add_path(self.head, index, REFERENCE_PATH_INDEX, path)

		next = prev
		for i in range(0, length + 1):
			tmp = next.get_neighbour_by_path(REFERENCE_PATH_INDEX)
			edge = next.get_edge(tmp)
			if (path in edge.paths):
				edge.paths.remove(path)
			next = tmp

		old_deletion = prev.get_edge(next)
		if old_deletion:
			old_deletion.paths.append(path)
		else:
			prev.add_neighbour(next, path)

		self.add_path(next, TAIL_INDEX, REFERENCE_PATH_INDEX, path)

	def add_insertion(self, value, index, path):
		if not path in self.paths:
			self.paths.append(path)

		prev = self.add_path(self.head, index, REFERENCE_PATH_INDEX, path)
		next = prev.get_neighbour_by_path(REFERENCE_PATH_INDEX)
		self.generate_insertion(prev, next, value, path)
		self.add_path(next, TAIL_INDEX, REFERENCE_PATH_INDEX, path)

	def add_short_insertion(self, original, value, index, path):
		if not path in self.paths:
			self.paths.append(path)

		prev = self.add_path(self.head, index, REFERENCE_PATH_INDEX, path)
		next = prev
		for i in range(1, len(original) + 1):
			tmp = next.get_neighbour_by_path(REFERENCE_PATH_INDEX)
			edge = next.get_edge(tmp)
			if (path in edge.paths):
				edge.paths.remove(path)
			next = tmp
		self.generate_insertion(prev, next, value, path)
		self.add_path(next, TAIL_INDEX, REFERENCE_PATH_INDEX, path)

	def generate_insertion(self, prev, next, value, path):
		for neighbour in prev.neighbours:
			if path in neighbour.paths:
				if (len(neighbour.paths) == 1):
					prev.neighbours.remove(neighbour)
				else:
					neighbour.paths.remove(path)

		first = prev.get_neighbour_by_base(value[1])
		if not first:
			first = Node(value[1], self.current_index)
			self.add_node(first)
			prev.add_neighbour(first, path)
		else:
			prev.get_edge(first).paths.append(path)

		last = first
		for i in range(2, len(value)):
			old_insert = last.get_neighbour_by_base(value[i])
			if old_insert:
				last.get_edge(old_insert).paths.append(path)
				last = old_insert
			else:
				new = Node(value[i], self.current_index)
				self.add_node(new)
				last.add_neighbour(new, path)
				last = new

		if (last.get_edge(next)):
			last.get_edge(next).paths.append(path)
		else:
			last.add_neighbour(next, path)

	def insert_global_alignment(self, alignment, new_path, name):
		path = self.get_path_from_alignment(alignment)
		exitable = False #TODO: REMOVE

		if (len(path) != len(new_path)):
			print('Can only align global alignments of equal length')
			return

		for i in range(0, len(new_path)):
			if (new_path[i]):
				self.head.add_neighbour(new_path[i], name)
				break

		for i in range(len(new_path) - 1, 0, -1):
			if (new_path[i]):
				new_path[i].add_neighbour(self.tail, name)
				break
		self.paths.append(name)
		prev = self.head
		new_prev = self.head
		for i in range(0, len(path)):
			if not path[i]:
				new_prev = new_path[i]
				self.add_node(new_path[i])
			elif not new_path[i]:
				prev = path[i]
			elif (path[i].value == new_path[i].value):
				if (prev == new_prev):
					edge = prev.get_edge(path[i])
					for incoming in new_path[i].incoming:
						for names in incoming.paths:
							if not names in edge.paths:
								edge.paths.append(names)
					prev.neighbours.remove(prev.get_edge(new_path[i]))
				else:
					new_prev.add_neighbour(path[i], name)
					old_edge = new_prev.get_edge(new_path[i])
					if (old_edge):
						new_prev.neighbours.remove(old_edge)

				for neighbour in new_path[i].neighbours:
					for j in range(0, len(neighbour.dest.incoming)):
						if (neighbour.dest.incoming[j].src.index == new_path[i].index):
							neighbour.dest.incoming[j].src = path[i]

				for neighbour in new_path[i].neighbours:
					path[i].neighbours.append(neighbour)
					neighbour.dest.incoming.append(neighbour)

				new_prev = prev = path[i]
			else:
				self.add_node(new_path[i])
				new_prev = new_path[i]
				prev = path[i]

		# Remove duplicates of tail-edges
		if prev == new_prev:
			edge = prev.get_edge(prev.get_neighbour_by_base(TAIL_VALUE))
			temp = edge
			while temp:
				prev.neighbours.remove(temp)
				temp = prev.get_edge(prev.get_neighbour_by_base(TAIL_VALUE))
			edge.paths.append(name)
			prev.neighbours.append(edge)



	def get_path_from_alignment(self, alignment):
		path = []

		i = 0
		last = self.head
		while (i < len(alignment)):
			while (i < len(alignment) and alignment[i] == '-'):
				path.append(None)
				i += 1
			if (i >= len(alignment)):
				break

			last = last.get_neighbour_by_base(alignment[i])
			if not last:
				print('Invalid alignment at index ' + str(i) + ': ' + alignment[i])
				return
			path.append(last)
			i += 1

		return path

	def find_shortest_distance(self, start, end):
		source = self.get_node_by_index(start)
		return source.recursive_search(end)['length']

	def print_DOT_representation(self, filename):
		printer = DOTPrinter(self.paths)
		printer.search(self.head)
		printer.write(filename)

	def is_critical(self, node):
		size = 0
		for neighbour in node.neighbours:
			size += len(neighbour.paths)

		return size == len(self.paths)

	def is_index_critical(self, index):
		return self.is_critical(self.get_node_by_index(index))

	def find_critical_regions(self):
		critical = []
		for i in range(0, len(self.nodes)):
			if (self.is_critical(self.get_node_by_index(i))):
				critical.append(i)

		return sorted(self.head.find_critical(len(self.paths), critical))

	def find_most_probable_path(self):
		curr = self.head

		path = []
		probability = 1.0
		while True:
			if (curr == self.tail):
				break
			most = 0
			total = 0
			next = None
			for neighbour in curr.neighbours:
				total += len(neighbour.paths)
				if (len(neighbour.paths) > most):
					most = len(neighbour.paths)
					next = neighbour.dest

			curr = next
			path.append(curr)
			probability *= float(most) / total

		return path, probability[0:-1]

	def set_all_visited(self, value):
		for node in self.nodes:
			node.visited = value

	def generate_left_right_contexts(self):
		self.set_all_visited(False)

		left_contexts = []
		right_contexts = []
		self.clear_contexts()
		self.tail.generate_left_right_index(left_contexts, 'left')
		self.clear_contexts()
		self.head.generate_left_right_index(right_contexts, 'right')

		return left_contexts, right_contexts

	def clear_contexts(self):
		for node in self.nodes:
			node.contexts = {}

	def get_regions(self):
		self.set_all_visited(False)

		curr = self.head
		critical = True
		regions = []
		i = 0
		while (curr.index != TAIL_INDEX):
			region = Region(i, curr)
			curr = self.get_regions_rec(curr, region, critical, True)
			print('Ended region in ' + str(curr.index))
			critical = not critical
			regions.append(region)
			i += 1

		return regions

	def get_regions_rec(self, curr, region, critical, first):
		if (curr.index == TAIL_INDEX):
			return curr
		if (critical):
			region.add_node(curr)
			if (len(curr.neighbours) > 1):
				return curr
			return self.get_regions_rec(curr.neighbours[0].dest, region, critical, False)
		else:
			region.add_node(curr)
			if ((not first) and self.is_critical(curr)):
				return curr
			end = False
			for neighbour in curr.get_neighbours():
				temp = False
				if not neighbour.visited:
					temp = self.get_regions_rec(neighbour, region, critical, False)
				elif temp:
					end = temp
			return end

class Node:
	def __init__(self, value, index):
		self.value = value
		self.index = index
		self.neighbours = []
		self.incoming = []

	def get_neighbours(self):
		neighbours = []
		for edge in self.neighbours:
			neighbours.append(edge.dest)

		return neighbours

	def get_neighbour_by_path(self, path_index):
		for neighbour in self.neighbours:
			if path_index in neighbour.paths:
				return neighbour.dest

		return False

	def get_neighbour_by_index(self, index):
		if (index < len(self.neighbours)):
			return self.neighbours[index].dest

		return False

	def get_neighbour_by_base(self, base):
		for neighbour in self.neighbours:
			if (neighbour.dest.value == base):
				return neighbour.dest

		return False

	def add_neighbour(self, neighbour, path=REFERENCE_PATH_INDEX):
		edge = Edge(self, neighbour, path)
		self.neighbours.append(edge)
		neighbour.incoming.append(edge)

	def delete_neighbour(self, neighbour):
		if (neighbour in self.neighbours):
			elf.neighbours.remove(neighbour)

	def recursive_search(self, index, iterations=0):
		if (index == self.index):
			return {'node': self, 'length': iterations}

		else:
			for neighbour in self.get_neighbours():
				pair = neighbour.recursive_search(index, iterations + 1)
				if pair['node']:
					return pair

			return {'node': False, 'length': float('inf')}

		return True

	def get_edge(self, target):
		for neighbour in self.neighbours:
			if (neighbour.dest == target):
				return neighbour

		return False

	def has_path(self, path):
		for neighbour in self.neighbours:
			if (path in neighbour.paths):
				return True

		return False

	def set_visited(self, value):
		self.visited = value
		for neighbour in self.get_neighbours():
			if not (hasattr(neighbour, 'visited') and neighbour.visited == value):
				neighbour.set_visited(value)

	def generate_left_right_index(self, contexts, direction):
		if (hasattr(self, 'contexts') and len(self.contexts) > 0):
			l = []
			for value in self.contexts.values():
				l.append(self.value + value['context'])
			return l

		if direction == 'left':
			end_index = HEAD_INDEX
			next = self.incoming
			target = 'src'
		else:
			end_index = TAIL_INDEX
			next = self.neighbours
			target = 'dest'

		if (self.index == end_index):
			return ['$']
		else:
			self.contexts = {}
			for edge in next:
				for context in edge.get_node(target).generate_left_right_index(contexts, direction):
					self.contexts[context + str(self.index)] = {'context': context, 'index': self.index}

			l = []
			for key in self.contexts:
				context = self.contexts[key]
				if (len(context['context']) > MAX_SUFFIX_LENGTH):
					context['context'] = context['context'][0:MAX_SUFFIX_LENGTH]

				l.append(self.value + context['context'])
				contexts.append(context)

			return l

class Edge:
	def __init__(self, src, dest, path):
		self.src = src
		self.dest = dest
		self.paths = [path]

	def get_node(self, name):
		if (name == 'src'):
			return self.src
		elif (name == 'dest'):
			return self.dest
		else:
			return None

class DOTPrinter:
	def __init__(self, paths):
		self.vertices = {}
		self.edges = []
		self.colours = [['green', 0x7CFC00], ['red', 0xFF0000], ['black', 0x000000], ['blue', 0xADD8E6], ['yellow', 0xFFFF00], ['chocolate', 0xD2691E], ['crimson', 0xDC143C], ['cyan', 0x00FFFF], ['deep pink', 0xFF1493], ['indigo', 0x4B0082]]
	
		self.colour_scheme = {}
		if (len(paths) > len(self.colours)):
			print('Unable to handle this many paths')
			for path in paths:
				self.colour_scheme[path] = colours[0][1]
		else:
			for i in range(0, len(paths)):
				self.colour_scheme[paths[i]] = self.colours[i][1]

		print('Colours: ' + str(self.colour_scheme))

	def search(self, head):
		self.vertices = {}
		self.edges = []
		self.vertices[HEAD_INDEX] = {'value': HEAD_VALUE, 'paths': [REFERENCE_PATH_INDEX]}

		queue = [head]
		while (len(queue) > 0):
			curr = queue.pop(0)
			neighbours = curr.neighbours
			for neighbour in neighbours:
				if not (neighbour.dest.index in self.vertices.keys()):
					paths = []
					for incoming in neighbour.dest.incoming:
						for path in incoming.paths:
							paths.append(path)
					self.vertices[neighbour.dest.index] = {'value':str(neighbour.dest.value), 'paths':paths}
					queue.append(neighbour.dest)
				self.edges.append({'src':curr.index, 'dest':neighbour.dest.index, 'paths':neighbour.paths})

	def write(self, filename):
		file = open(filename, 'w')
		file.write('digraph {\n')
		file.write('graph [rankdir=LR, fontname=fixed, splines=true overlap=false, nodesep=1.0]\n\n')

		file.write('\t// Vertices\n')
		for key in self.vertices.keys():
			colours = []
			for path in self.vertices[key]['paths']:
				colours.append(self.colour_scheme[path])
			colour = merge_colours(colours)
			file.write('\t' + str(key) + ' [label="' + self.vertices[key]['value'] + '", xlabel="' + str(key) + '", color="#' + colour + '", style=filled];\n')

		file.write('\n\t//Edges\n')
		for edge in self.edges:
			colours = []
			for path in edge['paths']:
				colours.append(self.colour_scheme[path])

			colour = merge_colours(colours)
			file.write('\t' + str(edge['src']) + ' -> ' + str(edge['dest']) + ' [color="#' + str(colour) + '"];\n')

		file.write('}')
		file.close()

def merge_colours(colours):
	r = 0
	g = 0
	b = 0

	for colour in colours:
		r += (colour & 0xFF0000) >> 16
		g += (colour & 0x00FF00) >> 8
		b += colour & 0x0000FF


	r = int(r / len(colours)) << 16
	g = int(g / len(colours)) << 8
	b = int(b / len(colours))

	#return hex(r + g + b)
	return str(0x7CFC00)