import sqlalchemy.ext.declarative
import sqlalchemy.orm

engine = sqlalchemy.create_engine("postgresql://postgres:@postgis/priceticker")

db_session = sqlalchemy.orm.scoped_session(
    sqlalchemy.orm.sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)

Base = sqlalchemy.ext.declarative.declarative_base()
Base.query = db_session.query_property()
