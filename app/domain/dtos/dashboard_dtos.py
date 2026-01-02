from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List

@dataclass
class DashboardFinancialStatsDTO:
    total_received: Decimal
    total_pending: Decimal
    total_entries: int
    pending_count: int
    entries: List[dict] = field(default_factory=list)

@dataclass
class DashboardSessionItemDTO:
    id: str
    patient_id: str
    patient_name: str
    date_time: datetime
    price: Decimal
    status: str

@dataclass
class DashboardSessionStatsDTO:
    today: List[DashboardSessionItemDTO]
    recent: List[DashboardSessionItemDTO]
    total_month: int

@dataclass
class DashboardPatientStatsDTO:
    total: int
    active: int
    inactive: int
