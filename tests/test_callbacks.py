# coding: utf-8

import pytest
import mock
from statemachine.callbacks import Callbacks
from statemachine.dispatcher import resolver_factory
from statemachine.exceptions import InvalidDefinition


@pytest.fixture
def ObjectWithCallbacks():
    class ObjectWithCallbacks(object):
        def __init__(self):
            super(ObjectWithCallbacks, self).__init__()
            self.name = "statemachine"
            self.callbacks = Callbacks(resolver=resolver_factory(self)).add(
                ["life_meaning", "name", "a_method"]
            )

        @property
        def life_meaning(self):
            return 42

        def a_method(self, *args, **kwargs):
            return args, kwargs

    return ObjectWithCallbacks


class TestCallbacksMachinery:
    def test_raises_exception_without_setup_phase(self):
        func = mock.Mock()

        callbacks = Callbacks()
        callbacks.add(func)

        with pytest.raises(InvalidDefinition):
            callbacks(1, 2, 3, a="x", b="y")

        func.assert_not_called()

    def test_can_add_callback(self):
        callbacks = Callbacks()
        func = mock.Mock()

        callbacks.add(func)
        callbacks.setup(lambda x: x)

        callbacks(1, 2, 3, a="x", b="y")

        func.assert_called_once_with(1, 2, 3, a="x", b="y")

    def test_can_add_callback_that_is_a_string(self):
        callbacks = Callbacks()
        func = mock.Mock()
        resolver = mock.Mock(return_value=func)

        callbacks.add("my_method").add("other_method")
        callbacks.add("last_one")
        callbacks.setup(resolver)

        callbacks(1, 2, 3, a="x", b="y")

        resolver.assert_has_calls(
            [
                mock.call("my_method"),
                mock.call("other_method"),
            ]
        )
        assert func.call_args_list == [
            mock.call(1, 2, 3, a="x", b="y"),
            mock.call(1, 2, 3, a="x", b="y"),
            mock.call(1, 2, 3, a="x", b="y"),
        ]

    def test_callbacks_are_iterable(self):
        callbacks = Callbacks()

        callbacks.add("my_method").add("other_method")
        callbacks.add("last_one")

        assert [c.func for c in callbacks] == ["my_method", "other_method", "last_one"]

    def test_add_many_callbacks_at_once(self):
        callbacks = Callbacks()
        method_names = ["my_method", "other_method", "last_one"]

        callbacks.add(method_names)

        assert [c.func for c in callbacks] == method_names

    @pytest.mark.parametrize("suppress_errors", [False, True])
    def test_raise_error_if_didnt_found_attr(self, suppress_errors):
        callbacks = Callbacks(resolver_factory(object()))

        if suppress_errors:
            callbacks.add("this_does_no_exist", suppress_errors=suppress_errors)
        else:
            with pytest.raises(InvalidDefinition):
                callbacks.add("this_does_no_exist", suppress_errors=suppress_errors)

    def test_collect_results(self):
        callbacks = Callbacks()
        func1 = mock.Mock(return_value=10)
        func2 = mock.Mock(return_value=("a", True))
        func3 = mock.Mock(return_value={"key": "value"})

        callbacks.add([func1, func2, func3])
        callbacks.setup(lambda x: x)

        results = callbacks(1, 2, 3, a="x", b="y")

        assert results == [
            10,
            ("a", True),
            {"key": "value"},
        ]

    def test_callbacks_values_resolution(self, ObjectWithCallbacks):
        x = ObjectWithCallbacks()
        assert x.callbacks(xablau=True) == [42, "statemachine", ((), {"xablau": True})]