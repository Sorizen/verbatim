from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import RunStatus, StepName
from app.models.base import BaseDbModel
from app.models.columns import enum_column, money_column

if TYPE_CHECKING:
    from app.models.run_step import RunStep


class Run(BaseDbModel):
    __tablename__ = 'runs'

    idea: Mapped[str] = mapped_column(Text)
    status: Mapped[RunStatus] = mapped_column(enum_column(RunStatus), default=RunStatus.QUEUED)
    current_step: Mapped[StepName | None] = mapped_column(enum_column(StepName))
    cost_usd: Mapped[float] = mapped_column(money_column(), default=0.0)
    review_reason: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    video_path: Mapped[str | None] = mapped_column(Text)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    steps: Mapped[list['RunStep']] = relationship(
        back_populates='run',
        cascade='all, delete-orphan',
        order_by='RunStep.created_at',
        lazy='selectin',
    )
