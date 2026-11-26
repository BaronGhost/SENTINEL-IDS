import pandas as pd
from predictor import IDSPredictor

print("Loading UNSW Model...")
predictor = IDSPredictor(dataset_type='unsw')

print("Loading a sample CSV...")
csv_path = 'datasets/CIC-UNSW-NB15/CICFlowMeter_out.csv'
df = pd.read_csv(csv_path, encoding='latin-1', low_memory=False)

print("Running prediction on first 100 rows...")
# Take just 100 rows for a quick test
sample_df = df.head(100)

results, error = predictor.predict(sample_df)

if error:
    print(f"❌ ERROR: {error}")
else:
    print("✅ SUCCESS!")
    print(results[['Label', 'Verdict', 'Attack_Probability']].head(10))