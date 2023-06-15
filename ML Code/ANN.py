# Step 1: Import the required libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, concatenate
from keras.layers import Input
from keras.models import Model


# Step 2: Load the dataset
print('Loading dataset')
df = pd.read_csv('combined_data.csv')

# Step 3: Perform one-hot encoding on the categorical variables
print('One-hot encoding')
categorical_data = df[['Time_of_Day', 'Day_of_Week', 'Weather_Condition', 'Road_Type', 'Incident']]

# One-hot encode the categorical data
encoder = OneHotEncoder(handle_unknown='ignore')
categorical_data = encoder.fit_transform(categorical_data).toarray()

# Step 4: Split the dataset into training and testing sets
print('split train and test data')
X_train_cat, X_test_cat, y_train, y_test = train_test_split(
    categorical_data, df['Traffic_Volume'].values, test_size=0.2, random_state=42)


cat_input = Input(shape=(X_train_cat.shape[1],))
x1 = Dense(64, activation='relu')(cat_input)
x1 = Dense(32, activation='relu')(x1)

output = Dense(1, activation='linear')(x1)
# linear is better for regression tasks, sigmoid better for binary classification

model = Model(inputs=cat_input, outputs=output)

model.compile(optimizer='adam', loss='mse')

# Train the model
print('train model')
model.fit(X_train_cat, y_train, epochs=20, batch_size=32)

# Evaluate the model
print('evaluate model')
mse = model.evaluate(X_test_cat, y_test)
print('Mean Squared Error: {:.2f}'.format(mse))

from sklearn.metrics import mean_absolute_error

# Predict on test data
y_pred = model.predict(X_test_cat)

# Calculate MAE
mae = mean_absolute_error(y_test, y_pred)
print('Mean Absolute Error: {:.2f}'.format(mae))


# Save the model to a file
import pickle
model.save('trafficANN.h5')
pickle.dump(model, open('trafficANN.pkl', 'wb'))
# model=pickle.load(open('trafficANN.pkl','rb'))