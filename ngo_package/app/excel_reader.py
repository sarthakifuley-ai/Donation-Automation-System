import pandas as pd

excel_file = "data/donations.xlsx"

def get_donors():
    df = pd.read_excel(excel_file)
    donors = df.to_dict(orient="records")
    return donors