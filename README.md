# Analysis of NYC Taxi Data
In this project, we analyze NYC Yellow Cab data to help drivers operate more efficiently. For a description of the analysis see 

The algorithm is trained in train.py, execute by first pre-processing the data,

python pre_process.py

then training by

python train.py

You can test the algorithm by running simulations from the iPython notebook ml-test

Analysis will be available here

https://rocky-plains-26026.herokuapp.com/

### Download data
To use these files, you will need to download NYC Yellow cab data.

Download the links below (replace the number 1 with an integer 1-9):
https://nyctaxitrips.blob.core.windows.net/data/trip_data_1.csv.zip
https://nyctaxitrips.blob.core.windows.net/data/trip_fare_1.csv.zip

or use the bash script

for i in `seq 1 10`;
do
   wget https://nyctaxitrips.blob.core.windows.net/data/trip_data_$i.csv.zip ;
done


for i in `seq 1 10`; 
do 
   wget https://nyctaxitrips.blob.core.windows.net/data/trip_fare_$i.csv.zip ; 
done

### Pre process data

We analyze taxi rides that occur betwen 7 and 10am on weekday mornings. The script pre_process.py will filter for these rides, as well as clean the data, add columns for profit, idle time by driver, and calculate hourly wage.