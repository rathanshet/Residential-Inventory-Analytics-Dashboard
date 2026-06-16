import openpyxl

file_path = "/Users/shetu/Downloads/SWW_RERA AREAs Final 28-1-26 Bajaj  (1).xlsx"
wb = openpyxl.load_workbook(file_path, data_only=False)
sheet = wb["AREA statement "]

print("Formulas in columns 13 to 18:")
for r in range(3, 15):
    row_vals = []
    for c in range(14, 19):
        cell = sheet.cell(row=r, column=c)
        row_vals.append(cell.value)
    print(f"Row {r:2d}: {row_vals}")
