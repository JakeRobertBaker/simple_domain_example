from __future__ import annotations

from enum import Enum
from abc import ABC, abstractmethod

from app.domain.exceptions import (
    QuestionError,
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
        """Generate p/Toparams."""
        pass


class Topic(Enum):
    CALCULUS = "calculus"
    ALGEBRA = "algebra"
    LINEAR_ALGEBRA = "linear_algebra"
    NUMBER_THEORY = "number_theory"


class RegistryDict:
    """Registry keyed by (topic, name), prevents overwrites."""

    def __init__(self):
        self._data: dict[Topic, dict[str, type[Question]]] = {t: {} for t in Topic}

    def add(self, question_cls: type[Question]):
        if not (isinstance(question_cls, type) and issubclass(question_cls, Question)):
            raise QuestionError("Registry can only add Question subclasses")
        topic = question_cls.topic
        name = question_cls.__name__
        if name in self._data[topic]:
            raise QuestionError(
                f"Registry already contains Question '{name}' for topic '{topic.value}'"
            )
        self._data[topic][name] = question_cls

    def get(self, topic: Topic, name: str) -> type[Question]:
        if name not in self._data[topic]:
            raise QuestionError(
                f"No question '{name}' found for topic '{topic.value}'"
            )
        return self._data[topic][name]

    def get_all(self) -> dict[Topic, dict[str, type[Question]]]:
        return {topic: dict(questions) for topic, questions in self._data.items()}


class Question(ABC):
    topic: Topic
    _registry: RegistryDict = RegistryDict()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Only process concrete classes
        if not hasattr(cls, "__abstractmethods__") or not cls.__abstractmethods__:
            # Validate topic
            if not hasattr(cls, "topic"):
                raise TypeError(f"{cls.__name__} must define a 'topic' class variable")
            if not isinstance(cls.topic, Topic):
                raise TypeError(
                    f"{cls.__name__}.topic must be a Topic enum, got {type(cls.topic)}"
                )

            cls._registry.add(cls)

    @classmethod
    def get_question_class(cls, topic: Topic, name: str) -> type[Question]:
        return cls._registry.get(topic, name)

    @classmethod
    def get_all_questions(cls) -> dict[Topic, dict[str, type[Question]]]:
        return cls._registry.get_all()

    def __init__(self, params: dict | None = None):
        self._internal_setup(params)

    @abstractmethod
    def _internal_setup(self, params: dict | None = None):
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

    def _internal_setup(self, params: dict | None = None):
        self.params = ExampleParams(params)
        self.y = self.params.m + self.params.n
