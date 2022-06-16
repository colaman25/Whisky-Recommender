## Flask API to call the nearest neighbor model
## Author: Hiuyan Lau
## June 16, 2022, 2022
## /getrecommendations [parameters: userId, numNeighbors]


from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import user_based_nearest_neighbor as model

app = Flask(__name__)
api = Api(app)


class getRecommendations(Resource):

    def get(self):
        userId = request.args.get('userId')
        numNeighbors = request.args.get('numNeighbors')
        if numNeighbors:
            return model.process_api(int(userId), int(numNeighbors))
        else:
            return model.process_api(int(userId))


api.add_resource(getRecommendations, '/getrecommendations')

if __name__ == '__main__':
    app.run()