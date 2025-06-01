#!/usr/bin/env python
# coding: utf-8

# In[2]:

m
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, Markdown
import base64

# Frequency multipliers
freq_map = {
    "Yearly": 1,
    "6 Months": 2,
    "Quarterly": 4,
    "Monthly": 12,
    "Bimonthly": 24,
    "Biweekly": 26,
    "Weekly": 52,
    "Daily (5 days/week)": 260,
    "Daily (7 days/week)": 365
}

# Create income input row
def create_income_row():
    member = widgets.Text(value="", placeholder="Guarantor / Spouse / etc.", description="Member:")
    source = widgets.Text(value="", placeholder="Job / SSI / Other", description="Source:")
    amount = widgets.FloatText(value=0.0, description="Amount:")
    freq = widgets.Dropdown(options=list(freq_map.keys()), value="Biweekly", description="Frequency:")
    row = widgets.HBox([member, source, amount, freq])
    return {"widgets": (member, source, amount, freq), "row": row}

# Sliding fee logic
def sliding_fee_category(family_size, annual_income):
    thresholds = {
        1: [15060, 18825, 22590, 26355, 30120],
        2: [20440, 25550, 30660, 35770, 40880],
        3: [25820, 32275, 38730, 45185, 51640],
        4: [31200, 39000, 46800, 54600, 62400],
        5: [36580, 45725, 54870, 64015, 73160],
        6: [41960, 52450, 62940, 73430, 83920],
        7: [47340, 59175, 71010, 82845, 94680],
        8: [52720, 65900, 79080, 92260, 105440]
    }
    if family_size > 8:
        extra = family_size - 8
        thresholds[family_size] = [x + extra * 5380 for x in thresholds[8]]
    limits = thresholds.get(family_size)
    if annual_income <= limits[0]: return "A – 100% FPL → $25 Nominal Fee"
    elif annual_income <= limits[1]: return "B – 125% FPL → 90% Discount"
    elif annual_income <= limits[2]: return "C – 150% FPL → 80% Discount"
    elif annual_income <= limits[3]: return "D – 175% FPL → 70% Discount"
    elif annual_income <= limits[4]: return "E – 200% FPL → 60% Discount"
    else: return "Above 200% FPL → No sliding discount"

# Household size
family_size_input = widgets.BoundedIntText(value=1, min=1, max=20, description='Family Size')

# Row logic
income_rows = []
rows_box = widgets.VBox()

def add_income_row(b=None):
    row = create_income_row()
    income_rows.append(row)
    rows_box.children = [r['row'] for r in income_rows]

def remove_income_row(b=None):
    if income_rows:
        income_rows.pop()
        rows_box.children = [r['row'] for r in income_rows]

# Add/Remove buttons
add_btn = widgets.Button(description="➕ Add Income", button_style='success')
remove_btn = widgets.Button(description="➖ Remove Last", button_style='danger')
add_btn.on_click(add_income_row)
remove_btn.on_click(remove_income_row)

# Add 2 rows initially
add_income_row()
add_income_row()

# Output
output = widgets.Output()
download_link = widgets.HTML()

def create_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a download="income_summary.csv" href="data:text/csv;base64,{b64}" target="_blank">📥 Download CSV</a>'

def calculate_total_income(b):
    output.clear_output()
    total_income = 0
    records = []

    for row in income_rows:
        member, source, amount, freq = [w.value for w in row['widgets']]
        if amount > 0:
            annual = amount * freq_map[freq]
            total_income += annual
            records.append({
                "Household Member": member,
                "Income Source": source,
                "Amount": amount,
                "Frequency": freq,
                "Annual Equivalent": annual
            })

    df = pd.DataFrame(records)
    category = sliding_fee_category(family_size_input.value, total_income)

    with output:
        display(Markdown(f"""
        ## 💡 Sliding Fee Summary:
        - **Family Size**: `{family_size_input.value}`
        - **Total Annual Income**: `${total_income:,.2f}`
        - **Sliding Fee Category**: **{category}**
        """))
        display(df)
        download_link.value = create_download_link(df)

calc_btn = widgets.Button(description="💾 Calculate", button_style='primary')
calc_btn.on_click(calculate_total_income)

# Display layout
display(Markdown("## 🏥 Amistad Health – Sliding Fee Schedule Calculator"))
display(family_size_input, widgets.HBox([add_btn, remove_btn]), rows_box, calc_btn, output, download_link)


# In[ ]:




