from sqlalchemy import Column, Integer, Text, DateTime, Date, Double

from database import Base


class Timesheets(Base):
    __tablename__ = "timesheets"

    userID = Column(Text(100), nullable=False)
    hospitalID = Column(Integer, nullable=False)
    dateWorked = Column(Date, nullable=False)
    clockInTime = Column(DateTime, nullable=False)
    clockOutTime = Column(DateTime, nullable=False)
    timeWorkedInSeconds = Column(Integer, nullable=False)
    rateAmount = Column(Double, nullable=False)
    rateType = Column(Text(50), nullable=False)
    dailyAmount = Column(Double, nullable=False)
    invoiceCode = Column(Text(10), nullable=True)
    taxPercent = Column(Double, nullable=True)
    timesheetID = Column(Integer, primary_key=True, autoincrement=True)

    # Create A Text
    def __repr__(self):
        return "<Timesheet ID %r>" % self.timesheetID
