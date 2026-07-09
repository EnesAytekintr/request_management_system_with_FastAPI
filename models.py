from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer

class inputs(Base):
    __tablename__ = "inputs"

    inputID = Column(Integer,primary_key=True, index=True)
    input_text = Column(String)

    input_request = relationship("requests", back_populates="input" ,cascade="all, delete-orphan", single_parent=True)

class outputs(Base):
    __tablename__ = "outputs"

    outputID = Column(Integer, primary_key=True, index=True)
    output_text = Column(String)

    output_request = relationship("requests", back_populates="output", cascade="all, delete-orphan", single_parent=True)

class ai_model(Base):
    __tablename__ = "ai_model"

    modelID = Column(Integer, primary_key=True, index=True)
    model_name = Column(String)

    model_request = relationship("requests", back_populates="model")

class users(Base):
    __tablename__ = "users"

    userID = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    subscription = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    user_request = relationship("requests", back_populates="user", cascade="all, delete-orphan")

class requests(Base):
    __tablename__ = "requests"

    requestID = Column(Integer, primary_key=True, index=True)
    userID = Column(Integer, ForeignKey("users.userID", ondelete="CASCADE"))
    modelID = Column(Integer, ForeignKey("ai_model.modelID", ondelete="SET NULL"), nullable=True)
    inputID = Column(Integer, ForeignKey("inputs.inputID", ondelete="CASCADE"))
    outputID = Column(Integer, ForeignKey("outputs.outputID", ondelete="CASCADE"))

    input = relationship("inputs", back_populates="input_request")
    output = relationship("outputs", back_populates="output_request")
    model = relationship("ai_model", back_populates="model_request")
    user = relationship("users", back_populates="user_request")