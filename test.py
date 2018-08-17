import unittest

from props import AbstractTestArbitraryInterface, ArbitraryInterface, \
    arbitrary, for_all

from examples import BinaryTree, prop_associative


class ForgotToImplementArbitrary(ArbitraryInterface):
    pass


class TestProps(unittest.TestCase, AbstractTestArbitraryInterface):
    def setUp(self):
        self.cls = BinaryTree

    def test_forgot_to_implement_arbitrary(self):
        with self.assertRaises(NotImplementedError):
            arbitrary(ForgotToImplementArbitrary)

    def test_floats_are_not_associative(self):
        with self.assertRaises(AssertionError):
            for_all(float, float, float)(prop_associative)
