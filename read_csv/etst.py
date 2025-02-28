from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import pandas as pd 

file = "calc_test_export.csv"
df:DataFrame = pd.read_csv(file)
print(df)
