class ToGException(Exception):
    """Raised when a prompt can not be answered using ToG."""

    pass


class InstructionError(Exception):
    """Raised when the agent did not follow the instructions."""

    pass


class FormatError(Exception):
    """Raised when an answer does not match required format."""

    pass
