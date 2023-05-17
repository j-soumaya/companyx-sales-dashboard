import pandas as pd

df = pd.read_excel(
        io="data.xlsx",
        engine="openpyxl",
        sheet_name="xx",
        skiprows=0,
        usecols="A:AL",
        nrows=447782
    )

df.info()