from sqlalchemy import create_engine

def get_connection():

    username = "root"
    password = "Manas0086"
    host = "localhost"
    database = "ai_business_kpi"

    engine = create_engine(
        f"mysql+pymysql://{username}:{password}@{host}/{database}"
    )

    return engine