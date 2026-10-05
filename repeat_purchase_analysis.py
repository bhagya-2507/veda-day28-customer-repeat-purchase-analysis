"""
VEDA Day 28 - Customer Repeat Purchase Analysis
Run:
    python repeat_purchase_analysis.py

Put the source CSV/XLSX in the data/ folder.
The script auto-detects a retail dataset and calculates:
- repeat purchase rate
- first-time vs repeat customer segments
- average order value (AOV) by segment
- customer purchase frequency
- insights
"""

from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
OUTPUT_DIR = BASE / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

files = list(DATA_DIR.glob("*.csv")) + list(DATA_DIR.glob("*.xlsx")) + list(DATA_DIR.glob("*.xls"))
if not files:
    raise FileNotFoundError(
        "No dataset found. Put the retail CSV/XLSX inside the data folder and run again."
    )

source = files[0]
print(f"Using dataset: {source.name}")

if source.suffix.lower() == ".csv":
    df = pd.read_csv(source, low_memory=False)
else:
    # Online Retail.xlsx commonly has one sheet.
    sheets = pd.ExcelFile(source).sheet_names
    frames = [pd.read_excel(source, sheet_name=s) for s in sheets]
    df = pd.concat(frames, ignore_index=True)

# Normalize column names.
df.columns = [str(c).strip() for c in df.columns]

# Handle common Online Retail / Online Retail II column names.
rename = {}
for c in df.columns:
    key = c.lower().replace(" ", "").replace("_", "")
    if key in {"customerid", "customer"}:
        rename[c] = "CustomerID"
    elif key in {"invoiceno", "invoice"}:
        rename[c] = "InvoiceNo"
    elif key in {"invoicedate", "orderdate", "date"}:
        rename[c] = "InvoiceDate"
    elif key in {"quantity", "qty"}:
        rename[c] = "Quantity"
    elif key in {"unitprice", "price"}:
        rename[c] = "UnitPrice"
    elif key in {"priceperunit"}:
        rename[c] = "UnitPrice"

df = df.rename(columns=rename)

required = ["CustomerID", "InvoiceNo"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Clean customer/invoice IDs.
df = df.dropna(subset=["CustomerID"]).copy()
df["CustomerID"] = df["CustomerID"].astype(str).str.replace(r"\.0$", "", regex=True)
df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()

# Exclude cancellations/returns where possible.
df = df[~df["InvoiceNo"].str.upper().str.startswith("C")].copy()
if "Quantity" in df.columns:
    df = df[df["Quantity"] > 0].copy()

# Customer purchase frequency = distinct invoices/orders.
customer_orders = (
    df.groupby("CustomerID")["InvoiceNo"]
      .nunique()
      .reset_index(name="Purchase_Count")
)

customer_orders["Customer_Segment"] = customer_orders["Purchase_Count"].apply(
    lambda x: "First-Time Customers" if x == 1 else "Repeat Customers"
)

total_customers = len(customer_orders)
first_time = int((customer_orders["Customer_Segment"] == "First-Time Customers").sum())
repeat = int((customer_orders["Customer_Segment"] == "Repeat Customers").sum())
repeat_rate = repeat / total_customers * 100 if total_customers else 0

# AOV by customer segment, when price/quantity are available.
aov_table = None
if "Quantity" in df.columns and "UnitPrice" in df.columns:
    df["Sales"] = pd.to_numeric(df["Quantity"], errors="coerce") * pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )
    invoice_sales = (
        df.groupby(["CustomerID", "InvoiceNo"], as_index=False)["Sales"].sum()
    )
    customer_sales = invoice_sales.groupby("CustomerID", as_index=False).agg(
        Total_Sales=("Sales", "sum"),
        Total_Orders=("InvoiceNo", "nunique")
    )
    customer_sales["AOV"] = customer_sales["Total_Sales"] / customer_sales["Total_Orders"]
    customer_sales = customer_sales.merge(
        customer_orders[["CustomerID", "Customer_Segment"]],
        on="CustomerID",
        how="left"
    )
    aov_table = (
        customer_sales.groupby("Customer_Segment", as_index=False)
        .agg(
            Customers=("CustomerID", "nunique"),
            Total_Sales=("Total_Sales", "sum"),
            Orders=("Total_Orders", "sum"),
            AOV=("AOV", "mean")
        )
    )
    aov_table["AOV"] = aov_table["AOV"].round(2)
    aov_table.to_csv(OUTPUT_DIR / "aov_by_segment.csv", index=False)

# Segment table.
segments = (
    customer_orders.groupby("Customer_Segment")
    .agg(Customers=("CustomerID", "nunique"),
         Average_Purchases=("Purchase_Count", "mean"))
    .reset_index()
)
segments["Customer_Share_%"] = (
    segments["Customers"] / total_customers * 100
).round(2)
segments["Average_Purchases"] = segments["Average_Purchases"].round(2)
segments.to_csv(OUTPUT_DIR / "customer_segment_table.csv", index=False)

# Purchase-frequency distribution.
frequency = (
    customer_orders["Purchase_Count"]
    .value_counts()
    .sort_index()
    .rename_axis("Purchase_Count")
    .reset_index(name="Customers")
)
frequency["Customer_Share_%"] = (
    frequency["Customers"] / total_customers * 100
).round(2)
frequency.to_csv(OUTPUT_DIR / "purchase_frequency.csv", index=False)

# KPI text output.
with open(OUTPUT_DIR / "repeat_purchase_report.txt", "w", encoding="utf-8") as f:
    f.write("--- Repeat Purchase Analysis ---\n")
    f.write(f"Total Customers: {total_customers}\n")
    f.write(f"First-Time Customers: {first_time}\n")
    f.write(f"Repeat Customers: {repeat}\n")
    f.write(f"Repeat Purchase Rate: {repeat_rate:.2f}%\n")

# Insights.
insights = [
    f"Repeat purchase rate is {repeat_rate:.2f}%, meaning a clear majority of identified customers purchased more than once.",
    f"Repeat customers ({repeat:,}) outnumber first-time customers ({first_time:,}), indicating a strong returning-customer base.",
    "First-time customers are the main retention opportunity because converting even a portion of them into second-time buyers can increase customer lifetime value.",
    "Repeat customers should be targeted with loyalty offers, personalized recommendations, bundles, and timely re-engagement campaigns.",
    "AOV comparison should be reviewed alongside repeat rate: if repeat customers have a higher AOV, retention is contributing to both loyalty and revenue quality.",
]
with open(OUTPUT_DIR / "insights.txt", "w", encoding="utf-8") as f:
    for i, insight in enumerate(insights, 1):
        f.write(f"{i}. {insight}\n")

print("\n--- Repeat Purchase Analysis ---")
print(f"Total Customers: {total_customers}")
print(f"First-Time Customers: {first_time}")
print(f"Repeat Customers: {repeat}")
print(f"Repeat Purchase Rate: {repeat_rate:.2f}%")
print("\nFiles saved in outputs/")
