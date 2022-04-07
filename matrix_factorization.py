import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## DATA CLEANING AND PREPERATION ##

# Load raw data extracted from the data scraper
rawdata = pd.read_csv('userratings_raw.csv')

# Create UserIDs and WhiskyIDs based usernames and whisky names
whisky_id = pd.DataFrame(rawdata['Whisky'].unique()).reset_index().set_axis(['whiskyID', 'Whisky Name'], axis=1)
user_id = pd.DataFrame(rawdata['user'].unique()).reset_index().set_axis(['userID', 'user'], axis=1)

# Rearrange and extract user-ratings records with userIDs and whiskyIDs
rawdata = rawdata.merge(whisky_id, left_on = 'Whisky', right_on = 'Whisky Name').merge(user_id, left_on = 'user', right_on = 'user')
rawdata['User Rating'] = pd.to_numeric(rawdata['User Rating'], errors = 'coerce')
rawratings = rawdata[['userID','whiskyID','User Rating']]

# Creating a user-whisky rating Matrix
y = pd.pivot_table(rawratings, index='userID', columns='whiskyID', values='User Rating', aggfunc=np.mean)
y.fillna(0, inplace=True)
yy = y.to_numpy()

## RECOMMENDATION FUNCTION ##
class matrix_factorization():

    def __init__(self, data, features):
        self.data = data
        self.features = features
        self.user_count = data.shape[0]
        self.item_count = data.shape[1]
        self.user_features = np.random.uniform(low=0.1, high=0.9, size=(self.user_count, self.features))
        self.item_features = np.random.uniform(low=0.1, high=0.9, size=(self.features, self.item_count))

    def MSE(self):
        matrix_product = np.matmul(self.user_features, self.item_features)
        return np.sum((self.data - matrix_product) ** 2)

    def single_gradient(self, user_row, item_col, wrt_user_idx=None, wrt_item_idx=None):
        if wrt_user_idx != None and wrt_item_idx != None:
            return 'Too many elements.'
        elif wrt_user_idx == None and wrt_item_idx == None:
            return 'Insufficient elements.'
        else:
            u_row = self.user_features[user_row, :]
            i_col = self.item_features[:, item_col]
            ui_rating = float(self.data[user_row, item_col])
            prediction = float(np.dot(u_row, i_col))
            if wrt_user_idx != None:
                row_elem = float(i_col[wrt_user_idx])
                gradient = 2 * (ui_rating - prediction) * row_elem
            else:
                col_elem = float(u_row[wrt_item_idx])
                gradient = 2 * (ui_rating - prediction) * col_elem
            return gradient

    def user_feature_gradient(self, user_row, wrt_user_idx):
        summation = 0
        for col in range(0, self.item_count):
            summation += self.single_gradient(user_row=user_row, item_col=col, wrt_user_idx=wrt_user_idx)
        return summation / self.item_count

    def item_feature_gradient(self, item_col, wrt_item_idx):
        summation = 0
        for row in range(0, self.user_count):
            summation += self.single_gradient(user_row=row, item_col=item_col, wrt_item_idx=wrt_item_idx)
        return summation / self.user_count

    def update_user_features(self, learning_rate):
        for i in range(0, self.user_count):
            for j in range(0, self.features):
                self.user_features[i, j] += learning_rate * self.user_feature_gradient(user_row=i, wrt_user_idx=j)

    def update_item_features(self, learning_rate):
        for i in range(0, self.features):
            for j in range(0, self.item_count):
                self.item_features[i, j] += learning_rate * self.item_feature_gradient(item_col=j, wrt_item_idx=i)

    def train_model(self, learning_rate=0.1, iterations=1000):
        for i in range(iterations):
            self.update_user_features(learning_rate=learning_rate)
            self.update_item_features(learning_rate=learning_rate)

            print(self.MSE())

# Run Model
d = matrix_factorization(yy, 2)
d.train_model(learning_rate=0.1, iterations=10)

def printoutput(userID):
    output = pd.DataFrame(np.dot(d.user_features, d.item_features)[userID], index=y.columns, columns=['Score'])
    output = output.merge(whisky_id, left_index=True, right_on='whiskyID', how='left')
    print(output.sort_values(by='Score', ascending=False).head(10))

# Print Recommendation for Specific User
printoutput(12)