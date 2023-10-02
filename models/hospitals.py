from sqlalchemy import Column, Integer, Text

from database import Base


class Hospitals(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hospitalName = Column(Text(100), nullable=False)
    hospitalCode = Column(Text(10), nullable=False, unique=True)
    hospitalAddress = Column(Text(100), nullable=True)
    hospitalCity = Column(Text(50), nullable=True)
    hospitalState = Column(Text(50), nullable=True)
    hospitalZip = Column(Text(5), nullable=True)
    hospitalPhone = Column(Text(12), nullable=True)
    hospitalEmail = Column(Text(100), nullable=True)

    # Create A Text
    def __repr__(self):
        return "<Hospital Name %r>" % self.hospitalName
