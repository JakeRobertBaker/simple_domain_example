from enum import Enum
from abc import ABC, abstractmethod

from app.domain.exceptions import (
    QuestionIrrelevantParams,
    QuestionMissingParams,
    QuestionParamError,
)

from app.domain.validators import validate_int


class ParamsDict:
    """Wrapper that tracks which params have been accessed"""

    def __init__(self, params: dict):
        self._params = params.copy()
        self._accessed = set()

    def get(self, key):
        if key not in self._params:
            raise QuestionMissingParams(f"Missing required param: {key}")
        self._accessed.add(key)
        return self._params[key]

    def get_unused(self):
        return set(self._params.keys()) - self._accessed


class Params(ABC):
    def __init__(self, params: dict | None = None):
        if params:
            wrapped = ParamsDict(params)
            self._validate(wrapped)
            unused = wrapped.get_unused()
            if unused:
                raise QuestionIrrelevantParams(f"Unexpected params: {list(unused)}")
        else:
            self._generate()

    @abstractmethod
    def _validate(self, params: ParamsDict):
        """Get and validate params from ParamsDict. Non-mutating."""
        pass

    @abstractmethod
    def _generate(self):
        """Generate params."""
        pass


class Topic(Enum):
    CALCULUS = "calculus"
    ALGEBRA = "algebra"
    LINEAR_ALGEBRA = "linear_algebra"
    NUMBER_THEORY = "number_theory"


class Question(ABC):
    topic: Topic

    def __init__(self, params: dict):
        self._internal_setup(params)

    @abstractmethod
    def _internal_setup(self, params: dict):
        pass


class ExampleParams(Params):
    def _validate(self, params: ParamsDict) -> None:
        # can have very simple parameterisation
        self.m: int = validate_int(params.get("m"))
        # we may have some strange validation logic
        n = validate_int(params.get("n"))
        # m cannot divide m and vice versa
        if not (n % self.m != 0) and (self.m % n == 0):
            raise QuestionParamError("n and m cannt divide one another")
        self.n: int = n

    def _generate(self):
        self.m = 75
        self.n = 12


class Example(Question):
    topic = Topic.NUMBER_THEORY

    def _internal_setup(self, params: dict):
        self.params = ExampleParams(params)
        self.y = self.params.m + self.params.n
