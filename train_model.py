import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor


df = pd.read_csv("restaurant_data.csv")


df = df.drop(['Restaurant ID', 'Restaurant Name', 'Address'], axis=1, errors='ignore')

df.fillna(method='ffill', inplace=True)


df = pd.get_dummies(df, drop_first=True)

X = df.drop("Aggregate rating", axis=1)
y = df["Aggregate rating"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeRegressor()
model.fit(X_train, y_train)


pickle.dump(model, open("model.pkl", "wb"))

print("Model trained & saved successfully!")