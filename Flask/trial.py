from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

# Table definitions
class Subject(Base):
    __tablename__ = 'subjects'
    subject_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_name = Column(String(80), unique=True, nullable=False)
    chapters = relationship("Chapter", back_populates="subject")


class Chapter(Base):
    __tablename__ = 'chapters'
    chapter_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.subject_id'), nullable=False)
    chapter_name = Column(String(80), nullable=False)
    subject = relationship("Subject", back_populates="chapters")
    modules = relationship("Module", back_populates="chapter")


class Module(Base):
    __tablename__ = 'modules'
    module_id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.chapter_id'), nullable=False)
    module_name = Column(String(80), nullable=False)
    video_url = Column(Text)
    chapter = relationship("Chapter", back_populates="modules")


# Setup
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
session = Session()

# Insert data
# Add subject
french = Subject(subject_name='Geography')
session.add(french)
session.commit()

# Add chapter
intro = Chapter(chapter_name='Rocks', subject_id=french.subject_id)
session.add(intro)
session.commit()

# Add module
numbers = Module(module_name='Igneous Rocks', chapter_id=intro.chapter_id)
session.add(numbers)
session.commit()

print("Inserted French > Introduction > Numbers successfully.")

