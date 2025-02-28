import bcrypt
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))

    posts = relationship("Post", back_populates="owner")

    def set_password(self, password):
        """
        Hash and set the user's password with a salt.
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.hashed_password = hashed_password.decode('utf-8')

    def verify_password(self, password):
        """
        Verify the password against the stored hashed password.
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text)
    owner = relationship("User", back_populates="posts")
