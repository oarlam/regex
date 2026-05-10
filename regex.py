from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        self.next_states = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if isinstance(state, (StarState, PlusState)):
                try:
                    return state.check_next(next_char)
                except NotImplementedError:
                    pass

        for state in self.next_states:
            if state.check_self(next_char):
                return state

        raise NotImplementedError("rejected string")


class StartState(State):

    def __init__(self):
        self.next_states = []

    def check_self(self, char):
        return False


class TerminationState(State):
    def __init__(self):
        self.next_states = []

    def check_self(self, char):
        return False



class DotState(State):
    """
    state for . character (any character accepted)
    """

    def __init__(self):
        self.next_states = []

    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    def __init__(self, symbol: str) -> None:
        self.next_states = []
        self.symbol = symbol

    def check_self(self, char: str) -> State | Exception:
        return char == self.symbol


class StarState(State):

    def __init__(self, checking_state: State):
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        if self.checking_state.check_self(char):
            return True
        for state in self.next_states:
            if state.check_self(char):
                return True
        return False

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                if isinstance(state, StarState) and not state.checking_state.check_self(next_char):
                    return state.check_next(next_char)
                return state
        if self.checking_state.check_self(next_char):
            return self
        raise NotImplementedError("rejected string")


class PlusState(State):

    def __init__(self, checking_state: State):
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                if isinstance(state, StarState) and not state.checking_state.check_self(next_char):
                    return state.check_next(next_char)
                return state
        if self.checking_state.check_self(next_char):
            return self
        raise NotImplementedError("rejected string")



class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        prev_state = self.curr_state
        last_state = self.curr_state
        for char in regex_expr:
            new_state = self.__init_next_state(char, last_state)
            if isinstance(new_state, StarState):
                if last_state in prev_state.next_states:
                    prev_state.next_states.remove(last_state)
                prev_state.next_states.append(new_state)
                last_state = new_state

            elif isinstance(new_state, PlusState):
                last_state.next_states.append(new_state)
                prev_state = last_state
                last_state = new_state

            else:
                prev_state = last_state
                prev_state.next_states.append(new_state)
                last_state = new_state

        last_state.next_states.append(TerminationState())

    def __init_next_state(
        self, next_token: str, tmp_next_state: State) -> State:

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")
        return new_state

    def check_string(self, text: str) -> bool:
        curr_state = self.curr_state
        try:
            for char in text:
                curr_state = curr_state.check_next(char)

            def can_terminate(state: State) -> bool:
                for nxt in state.next_states:
                    if isinstance(nxt, TerminationState):
                        return True
                    if isinstance(nxt, (StarState, PlusState)) and can_terminate(nxt):
                        return True
                return False

            return can_terminate(curr_state)

        except NotImplementedError:
            return False


# if __name__ == "__main__":
#     regex_pattern = "a*4.+hi"

#     regex_compiled = RegexFSM(regex_pattern)
#     print(f'{regex_pattern =}')
#     print("aaaaaa4uhi", regex_compiled.check_string("aaaaaa4uhi"))  # True
#     print("4uhi", regex_compiled.check_string("4uhi"))  # True
#     print("meow", regex_compiled.check_string("meow"))  # False

def test():
    fsm = RegexFSM("cat")
    assert fsm.check_string("cat") is True
    assert fsm.check_string("dog") is False
    assert fsm.check_string("ca") is False

    fsm = RegexFSM("c.t")
    assert fsm.check_string("cat") is True
    assert fsm.check_string("cot") is True
    assert fsm.check_string("c!t") is True
    assert fsm.check_string("c9t") is True
    assert fsm.check_string("ct") is False

    fsm = RegexFSM("a*b")
    assert fsm.check_string("b") is True
    assert fsm.check_string("ab") is True
    assert fsm.check_string("a") is False
    assert fsm.check_string("ac") is False

    fsm = RegexFSM("a+b")
    assert fsm.check_string("b") is False
    assert fsm.check_string("ab") is True
    print("All tests passed successfully!")

test()
