Props
=====

Property-based testing for Python à la
`QuickCheck <http://en.wikipedia.org/wiki/QuickCheck>`__.

``for_all``
-----------

``for_all`` takes a list of generators (see below) and a property. It
then tests the property for arbitrary values of the generators.

Here's an example testing the commutative and associative properties of
``int``\ s:

.. code:: python

    for_all(int, int)(lambda a, b: a + b == b + a)
    for_all(int, int)(lambda a, b: a * b == b * a)
    for_all(int, int, int)(lambda a, b, c: c * (a + b) == a * c + b * c)

Generators
----------

*Note:* These are not the same as Python generators. We should rename
them. Generaters? Blech.

A generator is a specification of a set of possible Python objects. A
generator is either:

-  One of the following built-in types:

   -  ``None``, ``bool``, ``int``, ``float``, ``long``, ``complex``,
      ``str``, ``tuple``, ``set``, ``list``, or ``dict``

-  A class that implements the ArbitraryInterface
-  Or constructed using the generator combinators.

Combinators
~~~~~~~~~~~

-  ``maybe_a``

   -  Generates either an arbitrary value of the specified generator or
      None.

-  ``maybe_an``

   -  An alias for ``maybe_a``. Provided for syntactic convenience.

-  ``one_of``

   -  Generates an arbitrary value of one of the specified generators.

-  ``tuple_of``

   -  Generates a tuple by generating values for each of the specified
      generators.

-  ``set_of``

   -  Generates a homogeneous set of the specified generator. You can
      generate non-homogeneous sets using ``set``.

-  ``list_of``

   -  Generates a homogeneous list of the specified generator. You can
      generate non-homogeneous lists using ``list``.

-  ``dict_of``

   -  Generates a homogeneous dict of the specified generators using
      kwargs. You can generate non-homogeneous dicts using ``dict``.

``arbitrary``
-------------

``arbitrary`` takes a generator and returns a single instance of the
generator.

ArbitraryInterface
------------------

We provide a mixin with one classmethod, ``arbitrary``, which raises
``NotImplementedError``. To implement generators for your own classes,
please inherit from ArbitraryInterface and provide an implementation for
``arbitrary``.

Here's an example implementation of a Binary Tree class:

.. code:: python

    class BinaryTree(ArbitraryInterface):
        ...
        @classmethod
        def arbitrary(cls):
            return arbitrary(one_of(Leaf, Node))

    class Leaf(BinaryTree):
        ...
        @classmethod
        def arbitrary(cls):
            return cls(...)  # an instance of Leaf.

    class Node(BinaryTree):
        ...
        @classmethod
        def arbitrary(cls):
            return cls(
                ...
                # This is equivalent:
                arbitrary(BinaryTree),
                # to this:
                BinaryTree.arbitrary()
            )  # an instance of Node with two subtrees.

AbstractTestArbitraryInterface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We also provide an ``AbstractTestArbitraryInterface`` with you can mixin
to your test cases for each class that implements ``ArbitraryInterface``
to ensure the ``arbitrary`` method is implemented:

.. code:: python

    class TestBinaryTree(AbstractTestArbitraryInterface,
                         TestCase):
        def setUp(self):
            self.obj = BinaryTree

To Do
=====

-  all built in types: http://docs.python.org/2/library/stdtypes.html
-  ranges
-  import some faker generators for more semantic random values

