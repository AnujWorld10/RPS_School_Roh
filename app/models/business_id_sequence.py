from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BusinessIDSequence(Base):
    __tablename__ = "business_id_sequences"

    sequence_name: Mapped[str] = mapped_column(String(50), primary_key=True)
    last_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
