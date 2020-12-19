from pydantic import BaseModel


class DatetimeProcessingConfig(BaseModel):
    request_patterns = [
        "(?P<year>\\d{4})-(?P<month>\\d{1,2})-(?P<day>\\d{1,2})\\s(?P<hours>\\d{1,2}):(?P<minutes>\\d{2})",
        "(?P<day>\\d{1,2})\\.(?P<month>\\d{1,2})\\.(?P<year>\\d{4})\\s(?P<hours>\\d{1,2}):(?P<minutes>\\d{2})"
    ]
    response_pattern: str = "%Y-%m-%d %H:%M"
    boiler_controller_timezone: str = "Asia/Yekaterinburg"
