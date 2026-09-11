import enum


class SourceStatus(str, enum.Enum):
    ACTIVE = "active"
    MISSING_FROM_SOURCE = "missing_from_source"
    INACTIVE = "inactive"


class StreamStatus(str, enum.Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class ReportType(str, enum.Enum):
    DEAD_STREAM = "dead_stream"
    WRONG_CHANNEL = "wrong_channel"
    WRONG_LOGO = "wrong_logo"
    WRONG_CONTENT = "wrong_content"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    OPEN = "open"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class SyncStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
