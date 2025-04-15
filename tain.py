import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pickle

# Load dataset
df = pd.read_csv('data/SFPD_Incidents_2021_to_Present_Reduced.csv')

# Drop missing values in critical columns
df.dropna(subset=['Incident Datetime', 'Incident Category'], inplace=True)

# Convert datetime column to datetime format
df['Incident Datetime'] = pd.to_datetime(df['Incident Datetime'], errors='coerce')
df.dropna(subset=['Incident Datetime'], inplace=True)

# Extract features
df['Hour'] = df['Incident Datetime'].dt.hour
df['Month'] = df['Incident Datetime'].dt.month
df['DayOfWeek'] = df['Incident Datetime'].dt.day_name()

# Only keep necessary columns
df = df[['Incident Category', 'Hour', 'Month', 'DayOfWeek']]

# Drop rows with missing values
df.dropna(inplace=True)

# Use one-hot encoding for DayOfWeek
df = pd.get_dummies(df, columns=['DayOfWeek'])

# Define features and target
X = df.drop(columns=['Incident Category'])
y = df['Incident Category']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Save column names for prediction input formatting
with open('model_columns.pkl', 'wb') as f:
    pickle.dump(X.columns.tolist(), f)
