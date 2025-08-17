import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models.domain_tables import Record

def summary_by_account(db: Session) -> pd.DataFrame:
    rows = db.execute(select(Record.account, func.sum(Record.amount)).group_by(Record.account)).all()
    return pd.DataFrame(rows, columns=['Hesap', 'Toplam'])
