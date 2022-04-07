## Whisky Recommender by User Based Nearest Neighbor
## Authoer: Hiuyan Lau
## April 7, 2022
## Raw Data Source: Whiskybase.com

import pandas as pd
import numpy as np

## DATA CLEANING AND PREPERATION ##

# Load raw data extracted from the data scraper
raw_rating_data = pd.read_csv('userratings_raw.csv')

# Create UserIDs and WhiskyIDs based usernames and whisky names
whisky_id = pd.DataFrame(raw_rating_data['Whisky'].unique()).reset_index().set_axis(['whiskyID', 'Whisky Name'], axis=1)
user_id = pd.DataFrame(raw_rating_data['user'].unique()).reset_index().set_axis(['userID', 'user'], axis=1)

# Rearrange and extract user-ratings records with userIDs and whiskyIDs
raw_rating_data = raw_rating_data.merge(whisky_id, left_on = 'Whisky', right_on = 'Whisky Name').merge(user_id, left_on = 'user', right_on = 'user')
raw_rating_data['User Rating'] = pd.to_numeric(raw_rating_data['User Rating'], errors = 'coerce')
rating_matrix = raw_rating_data[['userID','whiskyID','User Rating']]


## RECOMMENDATION FUNCTION ##
def run_recommendation(rating_matrix, myuserID, numNeighbors = 20):

    # Extract target user ratings, and find all users that has contributed ratings to any whisky rated by the target user
    targetuser_rating = rating_matrix[rating_matrix['userID'] == myuserID]
    all_relevant_ratings = rating_matrix[(rating_matrix['whiskyID'].isin(targetuser_rating['whiskyID'].tolist())) & (rating_matrix['userID'] != myuserID)]
    relevant_ratings = all_relevant_ratings.groupby(['userID'])

    pearsonCorrelationDict = {}

    # Calculate Pearson Correlation for each relevant users
    for userID, relevant_rating in relevant_ratings:

        numRatings = len(relevant_rating)
        if numRatings > 2:
            relevant_rating = relevant_rating.sort_values(by='whiskyID')
            targetuser_rating = targetuser_rating.sort_values(by='whiskyID')
            t_rating = targetuser_rating[targetuser_rating['whiskyID'].isin(relevant_rating['whiskyID'].tolist())][
                'User Rating'].tolist()
            r_rating = relevant_rating['User Rating'].tolist()
            Sxx = sum([i ** 2 for i in t_rating]) - pow(sum(t_rating), 2) / float(numRatings)
            Syy = sum([i ** 2 for i in r_rating]) - pow(sum(r_rating), 2) / float(numRatings)
            Sxy = sum(i * j for i, j in zip(t_rating, r_rating)) - sum(t_rating) * sum(r_rating) / float(numRatings)

            if Sxx != 0 and Syy != 0:
                pearsonCorrelationDict[userID] = Sxy / np.sqrt(Sxx * Syy)
            else:
                pearsonCorrelationDict[userID] = 0

    # Index the Pearson Corr - Relevant User matrix
    pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
    pearsonDF.columns = ['similarityIndex']
    pearsonDF['userId'] = pearsonDF.index
    pearsonDF.index = range(len(pearsonDF))

    # From the Pearson Corr - Relevant User, sort and find out the top X Relevant Users (Neighbors)
    topUsers = pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:numNeighbors]

    # For each neighbor, multiply similarity index with each whisky rating to find the weighted rating for each whisky
    topUsersRating = topUsers.merge(rating_matrix, left_on='userId', right_on='userID', how='inner')
    topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['User Rating']

    # Sum the weighted ratings from each neighbors for each whisky
    tempTopUsersRating = topUsersRating.groupby('whiskyID').sum()[['similarityIndex', 'weightedRating']]
    tempTopUsersRating.columns = ['sum_similarityIndex', 'sum_weightedRating']

    # Put into df
    recommendation_df = pd.DataFrame()
    recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
    recommendation_df['whiskyID'] = tempTopUsersRating.index

    # Sort by weighted average rating to find the most relevant whiskies
    recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)

    return recommendation_df

# Run the recommendation function
recommendation_df = run_recommendation(rating_matrix, 12, 20)

# Merge whisky names to whiskyIDs for the output
recommendation_df = recommendation_df.merge(whisky_id, left_index=True, right_on='whiskyID', how='left')

# Print Output
print(recommendation_df[['whiskyID', 'Whisky Name', 'weighted average recommendation score']].head(10))