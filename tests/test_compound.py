import pytest

from statemachine import State
from statemachine import StateMachine


@pytest.fixture()
def compound_engine_cls():
    class TestMachine(StateMachine):
        class engine(State.Builder, name="Engine", initial=True):
            off = State("Off", initial=True)
            on = State("On")

            turn_off = on.to(off)
            turn_on = off.to(on)

    return TestMachine


class TestNestedDeclarations:
    def test_capture_constructor_arguments(self, compound_engine_cls):
        sm = compound_engine_cls()
        assert isinstance(sm.engine, State)
        assert sm.engine.name == "Engine"
        assert sm.engine.initial is True

    def test_list_children_states(self, compound_engine_cls):
        sm = compound_engine_cls()
        assert [s.id for s in sm.engine.children] == ["off", "on"]

    def test_list_events(self, compound_engine_cls):
        sm = compound_engine_cls()
        assert [e.name for e in sm.events] == ["turn_off", "turn_on"]
