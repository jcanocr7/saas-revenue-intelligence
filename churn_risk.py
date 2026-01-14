import pandas as pd

#1 Load the data (Pandas reads the csv files)
print("Loading data...")
subs_df = pd.read_csv("subscriptions.csv")
usage_df = pd.read_csv("usage_events.csv")

#2 Preview the data (like looking at the top 5 rows in Excel)
print("\nPreview of subscriptions:")
print(subs_df.head())


#3 Aggregating usage (pivoting)
usage_counts = usage_df.groupby('customer_id')['event_count'].sum().reset_index()
usage_counts.columns = ['customer_id', 'total_usage']

#4 Merging (The Vlookup in Excel)
df = pd.merge(subs_df, usage_counts, on='customer_id',how='left')

#Fill "NaN" (empty values) with 0
df['total_usage'] = df['total_usage'].fillna(0)

print("\n---Data Stats---")
print(df[['mrr','total_usage']].describe())


#5 Define "High Risk logic"
# Stats showed Min usage is 456. So we must raise the threshold.
# New Rule: Paying > 20 EUR AND Usage < 1000 (The bottom ~15% of users)
risk_filter = (df['mrr'] > 20) & (df['total_usage']<1000)

#Apply the filter to create a new dataframe
#.copy() is crucial here - it tells Python "Make a clean standalone copy" not just a reference to the original
risky_customers = df[risk_filter].copy()

#6. Sort by who pays us the most (Priotize the biggest fires)
risky_customers = risky_customers.sort_values(by='mrr', ascending=False)

#7. Output the results
print("\n⚠️ HIGH CHURN RISK ALERT ⚠️")
print(f"Found {len(risky_customers)} customers paying >$20 with usage < 1000.")
print(risky_customers[['customer_id', 'plan_tier', 'mrr', 'total_usage']].head(10))

#Optional : Export to CSV For the sales team
risky_customers.to_csv('high_risk_customers.csv',index=False)
print("Exported to high_risk_customers.csv")