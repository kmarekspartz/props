from props import *

import unittest

class TestProps(unittest.TestCase):
    def test_examples_from_readme(self):
        for_all(int, int)(lambda a, b: a + b == b + a)
        for_all(int, int)(lambda a, b: a * b == b * a)
        for_all(int, int, int)(lambda a, b, c: c * (a + b) == a * c + b * c)

        def prop_associative(a, b, c):
            return a + (b + c) == (a + b) + c

        for_all(int, int, int)(prop_associative)

        with self.assertRaises(AssertionError):
            for_all(float, float, float)(prop_associative)

        def prop_list_append_pop(list, element):
            if element not in list:
                list.append(element)
                assert element in list
                list.pop()
                return element not in list
            return element in list

        for_all(list, int)(prop_list_append_pop)

if __name__ == '__main__':
    unittest.main()
