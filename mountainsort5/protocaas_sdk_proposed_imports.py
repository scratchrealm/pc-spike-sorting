from typing import Any, Optional, List


# This would be defined inside protocaas.sdk
class _ParameterGroup:
    def __init__(self, *,
        help: str = ''
    ):
        self.help = help

# This would be defined inside protocaas.sdk
# We need to use a function here rather than a class so that we can return the Any type
def parameter_group(*,
        help: str = ''
    ) -> Any: # it's important that this returns Any so that the linter is okay with using it
    return _ParameterGroup(
        help=help
    )

# This would be defined inside protocaas.sdk
class _Parameter:
    def __init__(self, *,
        default: Any,
        help: str = '',
        options: Optional[List[Any]] = None
    ):
        self.default = default
        self.help = help
        self.options = options

_not_specified = object()

# This would be defined inside protocaas.sdk
# We need to use a function here rather than a class so that we can return the Any type
def parameter(*,
    default: Any=_not_specified,
    help: str = '',
    options: Optional[List[Any]] = None
) -> Any: # it's important that this returns Any so that the linter is okay with using it
    return _Parameter(
        default=default,
        help=help,
        options=options
    )