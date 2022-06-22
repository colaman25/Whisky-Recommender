FROM ubuntu:20.04

ADD user_based_nearest_neighbor.py userratings_raw.csv api.py requirements.txt .

RUN apt-get update -y && \
          apt-get install -y python3 &&\
          apt-get install -y python3-pip && \
          pip install --upgrade pip && \
          pip install -r requirements.txt

CMD ["python3" , "api.py"]