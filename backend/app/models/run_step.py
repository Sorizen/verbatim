from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import StepName, StepStatus
from app.models.base import BaseDbModel
from app.models.columns import enum_column, money_column

if TYPE_CHECKING:
    from app.models.run import Run


class RunStep(BaseDbModel):
    __tablename__ = 'run_steps'

    run_id: Mapped[str] = mapped_column(ForeignKey('runs.id', ondelete='CASCADE'), index=True)
    name: Mapped[StepName] = mapped_column(enum_column(StepName))
    status: Mapped[StepStatus] = mapped_column(enum_column(StepStatus))
    attempt: Mapped[int]
    detail: Mapped[str | None] = mapped_column(Text)
    cost_usd: Mapped[float] = mapped_column(money_column(), default=0.0)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    run: Mapped['Run'] = relationship(back_populates='steps')
