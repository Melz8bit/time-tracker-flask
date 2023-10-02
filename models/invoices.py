from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, Double

from database import Base


class Invoices(Base):
    __tablename__ = "invoices"

    invoiceCode = Column(Text(10), nullable=False, unique=True)
    invoiceNumber = Column(Integer)
    invoiceStatus = Column(Text(20), nullable=False, default="Pending")
    invoiceStatusDate = Column(DateTime, nullable=False, default=datetime.today())
    invoiceTotal = Column(Double, nullable=True)
    invoiceUserID = Column(Text(100), nullable=False)
    invoiceUserHospitalID = Column(Integer, nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Create A Text
    def __repr__(self):
        return "<Invoice Code %r>" % self.invoiceCode
