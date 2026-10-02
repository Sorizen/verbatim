class PipelineError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ContractViolationError(PipelineError):
    pass


class LockedLineTooLongError(PipelineError):
    pass


class BudgetExceededError(PipelineError):
    pass


class ProviderError(PipelineError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class MediaToolError(PipelineError):
    pass
