class ProcessingError(Exception):
    """An error ocurred in the processing pipeline"""
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