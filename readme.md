# Whisky Recommender
Author: Hiuyan Lau

## Run Dockerized API
- Build a docker image using the Docerfile
- Run the image using detach mode.
- Send a GET request to 0.0.0.0:5000/getrecommendations?userId=[UserId]&numNeighbors=[k]
- UserId = User Id of the subject user, and k = number of nearest neighbors for the algorithm

## Gathering Data
- All data was gathered from www.whiskybase.com.
- Run whisky_base_com_scraper.py to scrape and gather data from the website.
- Data will be saved as userratings_raw.csv.
- Last Data Update: Dec 20, 2021

## User-based Nearest Neighbor Recommender
- Finding nearest user neighbor by Pearson Correlation
- Run user_based_nearest_neighbor.py
- Line 81: Customizable on target user ID (The "First Person" User ID) and number of nearest neighbor to be considered (Default: 20)

## Matrix Factorization
- Create intrinsic features for each whisky and user perference for each features
- Using gradient descent to reach the optimal user-feature and whisky-feature matrix
- Run matrix_factorization.py
- Line 87: Customiza number of intrinsic features (Default: 2)
- Line 88: Customize learning rate (Default: 0.1) and number of interations to run (Default: 10)