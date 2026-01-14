# generate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# === CUSTOMERS TABLE ===
n_customers = 500
signup_dates = pd.date_range(start='2024-01-01', end='2025-06-30', periods=n_customers).normalize()

customers = pd.DataFrame({
    'customer_id': range(1, n_customers + 1),
    'signup_date': signup_dates,
    'first_paid_date': signup_dates + pd.to_timedelta(np.random.randint(0, 30, n_customers), unit='D'),
    'country': np.random.choice(['DE', 'FR', 'NL', 'UK', 'ES'], n_customers, p=[0.4, 0.2, 0.15, 0.15, 0.1]),
    'acquisition_channel': np.random.choice(['Organic', 'Paid Social', 'Referral', 'Content', 'Outbound'], n_customers, p=[0.3, 0.25, 0.2, 0.15, 0.1]),
    'company_size_bucket': np.random.choice(['1-10', '11-50', '51-200', '201+'], n_customers, p=[0.5, 0.3, 0.15, 0.05])
})

# Some customers churn before first paid
customers.loc[customers.sample(frac=0.15).index, 'first_paid_date'] = None

customers.to_csv('customers.csv', index=False)
print(f"[OK] Generated customers.csv ({len(customers)} records)")

# === SUBSCRIPTIONS TABLE ===
subscriptions = []
sub_id = 1

for _, customer in customers.iterrows():
    if pd.isna(customer['first_paid_date']):
        continue  # Freemium only, no paid subscription
    
    current_date = customer['first_paid_date']
    end_date = datetime(2025, 12, 31)
    
    # Customer lifecycle: initial subscription + possible upgrades/downgrades
    tiers = ['Starter', 'Growth', 'Pro']
    mrr_map = {'Starter': 29, 'Growth': 99, 'Pro': 299}
    
    current_tier = np.random.choice(tiers, p=[0.6, 0.3, 0.1])
    
    while current_date < end_date:
        # Subscription duration (customers either churn or stay until end_date)
        churn_chance = 0.05  # 5% monthly churn
        months_active = np.random.geometric(churn_chance)
        
        sub_end = min(current_date + timedelta(days=30 * months_active), end_date)
        
        # Determine if churned
        churned = sub_end < end_date and np.random.random() < 0.3
        churn_date = sub_end if churned else None
        churn_reason = np.random.choice(['Price', 'Product Fit', 'Competitor', 'Other', None], p=[0.2, 0.3, 0.2, 0.2, 0.1]) if churned else None
        
        subscriptions.append({
            'subscription_id': sub_id,
            'customer_id': customer['customer_id'],
            'plan_tier': current_tier,
            'mrr': mrr_map[current_tier],
            'start_date': current_date.date(),
            'end_date': sub_end.date(),
            'churn_date': churn_date.date() if churn_date else None,
            'churn_reason': churn_reason
        })
        
        sub_id += 1
        
        if churned:
            break  # Customer churned, no more subscriptions
        
        # Possible upgrade/downgrade
        if np.random.random() < 0.15:  # 15% chance of tier change
            tier_idx = tiers.index(current_tier)
            if np.random.random() < 0.7 and tier_idx < 2:  # 70% upgrade
                current_tier = tiers[tier_idx + 1]
            elif tier_idx > 0:  # Downgrade
                current_tier = tiers[tier_idx - 1]
        
        current_date = sub_end

subscriptions_df = pd.DataFrame(subscriptions)
subscriptions_df.to_csv('subscriptions.csv', index=False)
print(f"[OK] Generated subscriptions.csv ({len(subscriptions_df)} records)")

# === USAGE EVENTS TABLE ===
usage_events = []
event_id = 1

for _, customer in customers.iterrows():
    if pd.isna(customer['first_paid_date']):
        n_events = np.random.randint(5, 30)  # Freemium users
    else:
        n_events = np.random.randint(50, 500)  # Paid users more active
    
    event_dates = pd.date_range(
        start=customer['signup_date'],
        end=min(datetime(2025, 12, 31), customer['signup_date'] + timedelta(days=540)),
        periods=n_events
    )
    
    for event_date in event_dates:
        usage_events.append({
            'event_id': event_id,
            'customer_id': customer['customer_id'],
            'event_date': event_date.date(),
            'feature_category': np.random.choice(['Core', 'Reporting', 'Integration', 'Admin'], p=[0.5, 0.25, 0.15, 0.1]),
            'event_count': np.random.randint(1, 20)
        })
        event_id += 1

usage_df = pd.DataFrame(usage_events)
usage_df.to_csv('usage_events.csv', index=False)
print(f"[OK] Generated usage_events.csv ({len(usage_df)} records)")

# === SALES TOUCHES TABLE ===
sales_touches = []
touch_id = 1

for _, customer in customers.iterrows():
    # Random number of sales touches per customer
    n_touches = np.random.randint(0, 20)
    
    touch_dates = pd.date_range(
        start=customer['signup_date'],
        end=min(datetime(2025, 12, 31), customer['signup_date'] + timedelta(days=365)),
        periods=n_touches
    ) if n_touches > 0 else []
    
    for touch_date in touch_dates:
        sales_touches.append({
            'touch_id': touch_id,
            'customer_id': customer['customer_id'],
            'touch_date': touch_date.date(),
            'touch_type': np.random.choice(['Email', 'Call', 'Demo', 'Check-in'], p=[0.4, 0.3, 0.2, 0.1]),
            'sales_rep_id': np.random.randint(1, 11),  # 10 sales reps
            'outcome': np.random.choice(['Connected', 'No Response', 'Meeting Scheduled', 'Opportunity'], p=[0.4, 0.3, 0.2, 0.1])
        })
        touch_id += 1

sales_df = pd.DataFrame(sales_touches)
sales_df.to_csv('sales_touches.csv', index=False)
print(f"[OK] Generated sales_touches.csv ({len(sales_df)} records)")

print("\n[OK] All files generated successfully")
print("Next: Import these CSVs into Supabase")

