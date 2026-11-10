
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.tools import tool


@tool
def get_current_datetime() -> str:
    """Get the current date, time, and timezone in Pakistan.

    Use this tool when the user asks about today's date,
    current time, day of the week, or date-related information.
    """

    now = datetime.now(ZoneInfo("Asia/Karachi"))

    return (
        f"Date: {now.strftime('%Y-%m-%d')}\n"
        f"Day: {now.strftime('%A')}\n"
        f"Time: {now.strftime('%I:%M:%S %p')}\n"
        f"Timezone: Asia/Karachi (PKT, UTC+05:00)"
    )
