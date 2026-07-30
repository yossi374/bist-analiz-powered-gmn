from enum import Enum

class Signal(str, Enum):
    AL = "AL"
    SAT = "SAT"
    TUT = "TUT"

class TrendDirection(str, Enum):
    YUKARI = "YUKARI"  # Bullish
    ASAGI = "ASAGI"    # Bearish
    YATAY = "YATAY"    # Sideways

class AgentRole(str, Enum):
    TEKNIK_ANALIST = "teknik_analist"
    TEMEL_ANALIST = "temel_analist"
    RISK_YONETICISI = "risk_yoneticisi"

class TimeInterval(str, Enum):
    ONE_MIN = "1m"
    FIVE_MIN = "5m"
    FIFTEEN_MIN = "15m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
