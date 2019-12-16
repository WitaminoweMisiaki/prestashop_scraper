from scraper.data_structures.tree_node import TreeNode


class Tree:
    def __init__(self):
        self.root = TreeNode(2, 'root', 1)
        self.uid_counter = 3

    def search(self, path, node=None):
        if node is None:
            node = self.root
        else:
            node = node

        while path:
            found = False
            for child in node.children:
                if str(path[0]) == child.name:
                    node = child
                    path = path[1:]
                    found = True
                    break
            if found is False:
                return False, node, path

        return True, node

    def add_path(self, path):
        result = self.search(path)
        node = result[1]
        if result[0] is False:
            children = result[2]
            node = self.add_children_to_path(node, children)

        return node.uid

    def add_children_to_path(self, parent, children):
        for child in children:
            parent.children.append(TreeNode(self.uid_counter, child, parent.uid))
            self.uid_counter += 1
            parent = self.search(path=[child], node=parent)[1]

        return parent

    def get_children_nodes(self, node=None):
        if node is None:
            node = self.root

        nodes = []
        for child in node.children:
            nodes.append(child)
            nodes.extend(self.get_children_nodes(child))

        return nodes
