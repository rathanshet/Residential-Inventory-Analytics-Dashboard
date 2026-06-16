import openpyxl

file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
wb = openpyxl.load_workbook(file_path, data_only=False)
sheet = wb["AREA statement "]

print("Formula in cells:")
# Let's print formulas for first 15 rows, columns 5, 6, 7, 8, 9, 10, 11, 12, 13
for r in range(1, 15):
    row_vals = []
    for c in range(1, 19):
        cell = sheet.cell(row=r, column=c)
        val = cell.value
        row_vals.append(val)
    print(f"Row {r:2d}: {row_vals[:14]}")
