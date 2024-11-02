from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the connection URL: replace `username`, `password`, and `database_name`
DATABASE_URL = "mysql+pymysql://qudus:danildubov@localhost/backend_training"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for our classes to inherit from
Base = declarative_base()

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

Base.metadata.create_all(engine)

#new_user = User(username="Bob", email="bob@example.com")
#session.add(new_user)
#session.commit()
#print("New user added:", new_user)
user = session.query(User).filter_by(username="john_doe").first()
print(user)
