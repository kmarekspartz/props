from dataclasses import dataclass

from props import for_all, ArbitraryInterface, one_of, arbitrary

for_all(int, int)(lambda a, b: a + b == b + a)
for_all(int, int)(lambda a, b: a * b == b * a)
for_all(int, int, int)(lambda a, b, c: c * (a + b) == a * c + b * c)


def prop_associative(a, b, c):
    return a + (b + c) == (a + b) + c


for_all(int, int, int)(prop_associative)


def prop_list_append_pop(list, element):
    if element not in list:
        list.append(element)
        assert element in list
        list.pop()
        return element not in list
    return element in list  # TODO: untested


for_all(list, int)(prop_list_append_pop)


class BinaryTree(ArbitraryInterface):
    @classmethod
    def arbitrary(cls):
        return arbitrary(one_of(Leaf, Node))


class Leaf(BinaryTree):
    @classmethod
    def arbitrary(cls):
        return cls()  # an instance of Leaf.


@dataclass
class Node(BinaryTree):
    left: BinaryTree
    right: BinaryTree

    @classmethod
    def arbitrary(cls):
        return cls(
            # This is equivalent:
            arbitrary(BinaryTree),
            # to this:
            BinaryTree.arbitrary())  # an instance of Node with two subtrees.
