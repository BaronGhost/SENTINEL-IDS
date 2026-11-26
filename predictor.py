import pandas as pd
import numpy as np
import joblib
import os


class IDSPredictor:
    def __init__(self, dataset_type='unsw'):
        """
        dataset_type: 'unsw' for unsw, 'ids17' for ids17
        """
        self.dataset_type = dataset_type
        # FIX: Capital 'M' to match your PyCharm folder
        base_path = f'Models/{dataset_type}'

        # Load Artifacts with EXACT file names from your screenshot
        if dataset_type == 'unsw':
            self.stage1_model = joblib.load(f'{base_path}/stage1_rf_triage.joblib')
            self.stage2_model = joblib.load(f'{base_path}/stage2_lgbm_detective.joblib')
            self.top_30_features = joblib.load(f'{base_path}/top_30_features.joblib')
        else:  # ids17
            self.stage1_model = joblib.load(f'{base_path}/stage1_rf.joblib')
            self.stage2_model = joblib.load(f'{base_path}/stage2_rf.joblib')

        self.le = joblib.load(f'{base_path}/label_encoder_main.joblib')
        self.train_columns = joblib.load(f'{base_path}/train_columns.joblib')

    def _preprocess(self, df):
        """Cleans and aligns the incoming CSV to match training data"""
        df = df.copy()
        df.columns = df.columns.str.strip()

        # 1. Drop leakage columns
        cols_to_drop = ['Flow ID', 'Src IP', 'Dst IP', 'Source IP', 'Destination IP', 'Timestamp', 'Src Port',
                        'Dst Port']
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

        # 2. Sanitize
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna()

        # Drop Label if it exists
        if 'Label' in df.columns:
            df = df.drop(columns=['Label'])

        # 3. One-Hot Encoding
        df = pd.get_dummies(df, drop_first=True)

        # Convert booleans to int to prevent model warnings
        for col in df.select_dtypes(include=['bool']).columns:
            df[col] = df[col].astype(int)

        # 4. Align columns
        df = df.reindex(columns=self.train_columns, fill_value=0)

        return df

    def predict(self, df):
        """Runs the two-stage chained prediction"""
        try:
            # Preprocess the data
            X = self._preprocess(df)

            if len(X) == 0:
                return None, "No valid rows left after cleaning (check for NaNs/inf)."

            # --- STAGE 1 ---
            if self.dataset_type == 'unsw':
                # Safety check
                for f in self.top_30_features:
                    if f not in X.columns:
                        X[f] = 0
                X_stage1 = X[self.top_30_features]
            else:
                X_stage1 = X  # IDS2017 uses all features

            stage1_probs = self.stage1_model.predict_proba(X_stage1)[:, 1]
            stage1_preds = (stage1_probs >= 0.5).astype(int)

            # --- STAGE 2 ---
            stage2_preds_encoded = self.stage2_model.predict(X)
            stage2_preds_labels = self.le.inverse_transform(stage2_preds_encoded)

            # --- CHAINING ---
            final_predictions = np.where(stage1_preds == 0, 'BENIGN', stage2_preds_labels)

            # Add results back to the original dataframe
            results_df = df.loc[X.index].copy()
            results_df['Verdict'] = final_predictions
            results_df['Attack_Probability'] = np.round(stage1_probs, 4)

            return results_df, None

        except Exception as e:
            return None, str(e)

    def predict_file(self, file_input, chunksize=50000):
        """Processes large CSVs in chunks to prevent RAM crashes."""
        try:
            results_list = []

            # file_input can be a file path (str) or a Streamlit uploaded file object
            chunk_iterator = pd.read_csv(
                file_input,
                encoding='latin-1',
                low_memory=False,
                chunksize=chunksize
            )

            for i, chunk in enumerate(chunk_iterator):
                # Run the normal predict on the chunk
                res_chunk, error = self.predict(chunk)
                if error:
                    return None, f"Error in chunk {i}: {error}"
                results_list.append(res_chunk)

            # Combine all chunks back into one DataFrame
            final_results = pd.concat(results_list, ignore_index=True)
            return final_results, None

        except Exception as e:
            return None, str(e)