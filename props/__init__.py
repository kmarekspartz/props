"""
Props.

Property-based testing for Python.
"""
import sys
import random
from collections.abc import Hashable


class ArbitraryInterface(object):
    """
    Interface to inherit from in order to use your classes with Props.

    *Note:* Please provide an implementation for the `arbitrary` method.
    """
    @classmethod
    def arbitrary():
        """
        Return a randomized instance of the class which inherits from this
        interface.
        """
        raise NotImplementedError


class AbstractTestArbitraryInterface(object):
    """
    A test mixin to check for the existence of an `arbitrary` method.

    To test this, mixin to your test case as following:

        class TestYourClass(AbstractTestArbitraryInterface,
                            unittest.TestCase):
            def setUp(self):
                self.cls = YourClass
    """
    def test_arbitrary(self):
        """
        Checks for inheritance from `ArbitraryInterface` and for the
        existence of the `arbitrary` method.
        """
        try:
            assert issubclass(self.cls, ArbitraryInterface)
            self.cls = cls.arbitrary()
        except AssertionError:
            self.fail(
                self.cls.__name__ +
                ' does not inherit from ArbitraryInterface.'
            )
        except NotImplementedError:
            self.fail(
                self.cls.__name__ +
                ' does not implement an `arbitrary` method.'
            )


class ArbitraryError(Exception):
    """
    Raised when argument to arbitrary is not an instance of Arbitrary
    interface, in the arbitrary dictionary, or None.
    """
    pass


class AbstractArbitrary(dict):
    """
    Helper class for the arbitrary function.
    Subclasses dict in order to allow for injection of type-level dispatch.

    This is too clever to be idiomatic.
    """
    def __call__(self, cls):
        if cls is None:
            return None
        if issubclass(cls, ArbitraryInterface):
            return cls.arbitrary()
        if cls in self:
            return self[cls]()
        raise ArbitraryError(
            'No instance of Arbitrary found for {0}. '
            'Did you remember to inherit from '
            'ArbitraryInterface?'.format(cls.__name__)
        )


arbitrary = AbstractArbitrary({
    int: lambda: random.randint(-sys.maxsize - 1, sys.maxsize),
    bool: lambda: arbitrary(int) > 0,
    ## sys.float_info_max:
    float: lambda: random.gauss(0, sys.maxsize),
    complex: lambda: complex(arbitrary(float), arbitrary(float)),
    str: lambda: ''.join(chr((i % 127) + 1) for i in arbitrary(list_of(int))),
    tuple: lambda: arbitrary(
        tuple_of(*[
            generator for generator in arbitrary.keys()
            if generator is not tuple
            and issubclass(generator, Hashable)
        ])
    ),
    set: lambda: arbitrary(
        set_of(*[
            generator for generator in arbitrary.keys()
            if generator is not tuple
            and issubclass(generator, Hashable)
        ])
    ),
    list: lambda: arbitrary(
        list_of(*[
            generator for generator in arbitrary.keys()
            if generator is not list
            and issubclass(generator, Hashable)
        ])
    ),
    dict: lambda: arbitrary(
        dict_of(**{
            arbitrary(str): generator for generator in arbitrary.keys()
            if generator is not dict
            and issubclass(generator, Hashable)
        })
    )
})


def for_all(*generators):
    """
    Takes a list of generators and returns a closure which takes a property,
    then tests the property against arbitrary instances of the generators.
    """
    ## Pass in n as an argument
    n = 100
    def test_property(property_function):
        """
        A closure which takes a property and tests it against arbitrary
        instances of the generators in the closure.
        """
        for generator in generators:
            assert (issubclass(generator, ArbitraryInterface)
                    or generator in arbitrary)

        def test_once():
            """
            Tests the property against a single set of instances of the
            generators.
            """
            instances = [
                arbitrary(generator) for generator in generators
            ]
            try:
                assert property_function(*instances)
            except AssertionError:
                generator_names = ', '.join(
                    generator.__name__ for generator in generators
                )
                stringed_instances = ', '.join(
                    str(instance) for instance in instances
                )
                error_message = ' '.join([
                    'Instances <',
                    stringed_instances,
                    '> of <',
                    generator_names,
                    '> do not satisfy a property.'
                ])
                raise AssertionError(error_message)
        for _ in range(n):
            test_once()
    return test_property


def maybe_a(generator):
    """
    Generates either an arbitrary value of the specified generator or None.
    This is a class factory, it makes a class which is a closure around the
    specified generator.
    """
    class MaybeAGenerator(ArbitraryInterface):
        """
        A closure class around the generator specified above, which generates
        either that generator or None.
        """
        @classmethod
        def arbitrary(cls):
            """
            Generate either the enclosed generator or None.
            """
            return arbitrary(one_of(None, generator))
    MaybeAGenerator.__name__ = ''.join([
        'maybe_a(',
        generator.__name__,
        ')'
    ])
    return MaybeAGenerator


def maybe_an(generator):
    """
    An alias for `maybe_a`. Provided for syntactic convenience.
    """
    return maybe_a(generator)


def one_of(*generators):
    """
    Generates an arbitrary value of one of the specified generators.
    This is a class factory, it makes a class which is a closure around the
    specified generators.
    """
    class OneOfGenerators(ArbitraryInterface):
        """
        A closure class around the generators specified above, which
        generates one of the generators.
        """
        @classmethod
        def arbitrary(cls):
            """
            Generate one of the enclosed generators.
            """
            return arbitrary(random.choice(generators))
    OneOfGenerators.__name__ = ''.join([
        'one_of(',
        ', '.join(generator.__name__ for generator in generators),
        ')'
    ])
    return OneOfGenerators


def tuple_of(*generators):
    """
    Generates a tuple by generating values for each of the specified
    generators.
    This is a class factory, it makes a class which is a closure around the
    specified generators.
    """
    class TupleOfGenerators(ArbitraryInterface):
        """
        A closure class around the generators specified above, which
        generates a tuple of the generators.
        """
        @classmethod
        def arbitrary(cls):
            """
            Generate a tuple of the enclosed generators.
            """
            return tuple([
                arbitrary(generator)
                for generator in generators
                if generator is not tuple
            ])
    TupleOfGenerators.__name__ = ''.join([
        'tuple_of(',
        ', '.join(generator.__name__ for generator in generators),
        ')'
    ])
    return TupleOfGenerators


def set_of(*generators):
    """
    Generates a set consisting solely of the specified generators.
    This is a class factory, it makes a class which is a closure around the
    specified generators.
    """
    class SetOfGenerators(ArbitraryInterface):
        """
        A closure class around the generators specified above, which
        generates a set of the generators.
        """
        @classmethod
        def arbitrary(cls):
            """
            Generate a set of the enclosed generators.
            """
            arbitrary_set = set()
            for generator in generators:
                arbitrary_set |= {
                    arbitrary(generator)
                    ## max_size / len(generators):
                    for _ in range(arbitrary(int) % 100)
                }
            return arbitrary_set
    SetOfGenerators.__name__ = ''.join([
        'set_of(',
        ', '.join(generator.__name__ for generator in generators),
        ')'
    ])
    return SetOfGenerators


def list_of(*generators):
    """
    Generates a list consisting solely of the specified generators.
    This is a class factory, it makes a class which is a closure around the
    specified generators.
    """
    class ListOfGenerators(ArbitraryInterface):
        """
        A closure class around the generators specified above, which
        generates a list of the generators.
        """
        @classmethod
        def arbitrary(cls):
            """
            Generate a list of the enclosed generators.
            """
            arbitrary_list = []
            for generator in generators:
                arbitrary_list += [
                    arbitrary(generator)
                    ## max_length / len(generators):
                    for _ in range(arbitrary(int) % 100)
                ]
            return arbitrary_list
    ListOfGenerators.__name__ = ''.join([
        'list_of(',
        ', '.join(generator.__name__ for generator in generators),
        ')'
    ])
    return ListOfGenerators


def dict_of(**kwargs):
    """
    Generates a homogeneous dict of the specified generators using kwargs.
    You can generate non-homogeneous dicts using `dict`.
    This is a class factory, it makes a class which is a closure around the
    specified keys and generators.
    """
    class DictOfKeyGenerators(ArbitraryInterface):
        """
        A closure class around the keys and generators specified above, which
        generates a dict of the keys and generators.
        """
        @classmethod
        def arbitrary(cls):
            """
            Generate a dict of the enclosed keys and generators.
            """
            return {
                key: arbitrary(generator)
                for key, generator
                in kwargs.iteritems()
            }
    DictOfKeyGenerators.__name__ = ''.join([
        'dict_of(',
        ', '.join([
            key + '=' + generator.__name__
            for key, generator
            in kwargs.iteritems()
        ]),
        ')'
    ])
    return DictOfKeyGenerators
