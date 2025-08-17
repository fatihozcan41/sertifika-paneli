import pandas as pd
from sqlalchemy.orm import Session
from models.domain_tables import Record

def import_dataframe(df: pd.DataFrame, db: Session):
    # Simple example: expects columns: date, account, description, amount
    columns = {c.lower(): c for c in df.columns}
    for _, row in df.iterrows():
        rec = Record(
            date=str(row.get(columns.get("date"), "")),
            account=str(row.get(columns.get("account"), "")),
            description=str(row.get(columns.get("description"), "")),
            amount=float(row.get(columns.get("amount"), 0) or 0),
        )
        db.add(rec)
    db.commit()
