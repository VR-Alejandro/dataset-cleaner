class ProcessingError(Exception):
    """Error base de la pipeline de procesamiento"""
    pass

class DatasetLoadError(ProcessingError):
    pass


class ValidationError(ProcessingError):
    pass


class CleaningError(ProcessingError):
    pass


class StatisticsError(ProcessingError):
    pass


class CleanedDatasetGenerationError(ProcessingError):
    pass

class ReportGenerationError(ProcessingError):
    pass