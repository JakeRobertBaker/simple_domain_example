from enum import Enum
from abc import ABC, abstractmethod
from collections import UserDict

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
        """Generate params."""
        pass


class RegistryDict(UserDict):
    """Registry keyed by topic_name, prevents overwrites."""

    def __setitem__(self, key: str, question: type["Question"]):
        """Add a question class to the registry."""
        # Construct expected key from question's topic and name
        expected_key = f"{question.topic.value}_{question.__name__}"

        # Validate key format
        if key != expected_key:
            raise ValueError(
                f"Registry key '{key}' must match format "
                f"'topic_classname': expected '{expected_key}'"
            )

        # Check if this key already exists (prevent overwrite)
        if key in self.data:
            raise QuestionError(
                f"Cannot register {question.__name__}: a question with topic "
                f"'{question.topic.value}' and name '{question.__name__}' "
                f"is already registered"
            )

        self.data[key] = question


class Topic(Enum):
    CALCULUS = "calculus"
    ALGEBRA = "algebra"
    LINEAR_ALGEBRA = "linear_algebra"
    NUMBER_THEORY = "number_theory"


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

            # Register the question class with topic_name key
            cls._registry[f"{cls.topic.value}_{cls.__name__}"] = cls

    @classmethod
    def get_question_class(cls, topic: Topic, name: str) -> type["Question"]:
        """Get a question class by topic and name from the registry"""
        key = f"{topic.value}_{name}"
        return cls._registry[key]

    @classmethod
    def get_all_questions(cls) -> dict[str, type["Question"]]:
        """Get all registered question classes"""
        return dict(cls._registry)

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
