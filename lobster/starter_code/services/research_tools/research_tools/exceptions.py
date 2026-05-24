class NoSearchResultsError(Exception):
    """Raised when the search returns no results."""


class ConfigurationError(Exception):
    pass


class DatasetNotAvailableError(Exception):
    pass


class InvalidDatasetError(Exception):
    pass