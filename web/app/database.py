import sqlalchemy.ext.declarative
import sqlalchemy.orm

from conf import settings

engine = sqlalchemy.create_engine(settings['DB_URL'])

db_session = sqlalchemy.orm.scoped_session(
    sqlalchemy.orm.sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)

Base = sqlalchemy.ext.declarative.declarative_base()
Base.query = db_session.query_property()
