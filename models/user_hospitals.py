from sqlalchemy import Column, Integer, Text

from database import Base


class UserHospitals(Base):
    __tablename__ = "user_hospitals"

    userID = Column(Text(100), nullable=True)
    hospitalID = Column(Integer, nullable=True)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Create A Text
    def __repr__(self):
        return "<Name %r>" % self.firstName
