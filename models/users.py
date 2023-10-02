from flask_login import UserMixin
from sqlalchemy import Column, Text
from werkzeug.security import generate_password_hash, check_password_hash

from database import Base


class Users(Base, UserMixin):
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
    userPassword = Column(Text(128), nullable=False)
    userRole = Column(Text(20), nullable=True)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.userPassword = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.userPassword, password)

    # Create A Text
    def __repr__(self):
        return "<Name %r>" % self.firstName
