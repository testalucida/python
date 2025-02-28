import pandas as pd
import ezodf

doc = ezodf.opendoc('/home/martin/Projects/python/Anlage_V/Stammdaten_TEST.ods')
print("Spreadsheet contains %d sheet(s)." % len(doc.sheets))

for sheet in doc.sheets:
    print("-"*40)
    print("   Sheet name : '%s'" % sheet.name)
    print("Size of Sheet : (rows=%d, cols=%d)" % (sheet.nrows(), sheet.ncols()) )

# convert the first sheet to a pandas.DataFrame
sheet = doc.sheets["Wohnung"]
df_dict = {}
for i, row in enumerate(sheet.rows()):
    # row is a list of cells
    # assume the header is on the first row
    print( "i: ", i )
    if i > 35: break
    if i == 0:
        # columns as lists in a dictionary
        df_dict = {cell.value: [] for cell in row}
        # create index for the column headers
        col_index = {j: cell.value for j, cell in enumerate(row)}
        continue
    for j, cell in enumerate(row):
        if j > 15: break
        # use header instead of column index
        df_dict[col_index[j]].append(cell.value)
# and convert to a DataFrame
df = pd.DataFrame(df_dict)
print( df )
