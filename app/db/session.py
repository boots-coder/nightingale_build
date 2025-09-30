from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 定义数据库URL
# "sqlite:///./nightingale.db" 表示在项目根目录下创建一个名为 nightingale.db 的SQLite数据库文件。
# check_same_thread is needed only for SQLite. It's not needed for other databases.
SQLALCHEMY_DATABASE_URL = "sqlite:///./nightingale.db"

# 2. 创建 SQLAlchemy 引擎 (engine)
# 引擎是 SQLAlchemy 与数据库沟通的核心。
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. 创建数据库会话 (Session)
# 每个 SessionLocal 实例都是一个数据库会话。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 创建一个 Base 类
# 之后我们创建的所有数据库模型（表）都将继承这个类。
Base = declarative_base()