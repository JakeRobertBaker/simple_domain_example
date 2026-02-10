from abc import ABC, abstractmethod

from app.domain.exceptions import (
    QuestionIrrelevantParams,
    QuestionMissingParams,
)


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
