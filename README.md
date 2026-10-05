# VEDA Day 28 — Customer Repeat Purchase Analysis

## Objective
Measure repeat purchase behavior and identify repeat-customer segments using Python and Pandas.

## Tools
- Python
- Pandas
- CSV / Excel
- Matplotlib (optional for visualization)

## Key Results
| Metric | Result |
|---|---:|
| Total Customers | 4,312 |
| First-Time Customers | 1,419 |
| Repeat Customers | 2,893 |
| Repeat Purchase Rate | 67.09% |

## Customer Segments
| Segment | Customers | Share |
|---|---:|---:|
| First-Time Customers | 1,419 | 32.91% |
| Repeat Customers | 2,893 | 67.09% |

## Method
1. Load the retail transaction dataset.
2. Remove missing customer IDs.
3. Exclude cancellation invoices where applicable.
4. Count distinct invoices for each customer.
5. Classify customers with 1 purchase as **First-Time** and 2+ purchases as **Repeat**.
6. Calculate Repeat Purchase Rate:
   `Repeat Customers / Total Customers × 100`
7. Compare segment behavior using AOV when price and quantity fields are available.

## Deliverables
- `repeat_purchase_kpi.csv`
- `customer_segment_table.csv`
- `insights.md`
- `repeat_purchase_analysis.py`
- `project_report.pdf`

## Business Takeaway
A **67.09%** repeat purchase rate indicates a strong returning-customer base. The next growth opportunity is converting first-time buyers into repeat customers through retention and loyalty strategies.
