from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text, BINARY

from database import Base

# Init db
# db = SQLAlchemy()


class Users(Base):
    __tablename__ = "users"

    id = Column(Text(100), primary_key=True)
    username = Column(Text(25), nullable=False, unique=True)
    firstName = Column(Text(50), nullable=False)
    lastName = Column(Text(50), nullable=False)
    companyName = Column(Text(100), nullable=True)
    mailingAddress = Column(Text(50), nullable=True)
    mailingCity = Column(Text(50), nullable=True)
    mailingState = Column(Text(50), nullable=True)
    mailingZip = Column(Text(5), nullable=True)
    email = Column(Text(100), nullable=False, unique=True)
    phoneNumber = Column(Text(12), nullable=True)
    userPassword = Column(Text(60), nullable=False)
    userRole = Column(Text(20), nullable=True)

    # Create A Text
    def __repr__(self):
        return "<Name %r>" % self.firstName
