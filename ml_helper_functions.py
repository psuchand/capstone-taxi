from random import random
from math import floor
from vincenty import vincenty

PENALTY_PROFIT_BAD_POS = -8
PENALTY_TIME_BAD_POS = 60*10
DRIVING_SPEED_IN_MPH = 12.5

COST_OF_TRAVEL_TIME_DOLLARS_HR = 42
OVERALL_AVG_WAIT_TIME = 11.4*60 #In Seconds
GOOD_POSITION_WAIT_TIME = 3*60 #In seconds

DATA_DIR = "../../taxi-data/"
TRAINING_DIR = DATA_DIR + "training/"

taxi_distance = pd.read_csv(TRAINING_DIR + "taxi_distance.csv", index_col = 0)

def random_ride(rides, from_position, starting_hour):
    """
    Randomly choose a ride from the given dataframe, at the specified position.    
    Sampling is done assuming the distribution of rides does not vary within the hour.
    """

    #Restrict to rides for the given hour and position
    rides = rides[(rides.hour == starting_hour) & (rides.pos == from_position)]

    try:
        choice = rides.sample(1)

        ending_pos = choice['dropoff_pos'].values[0]
        time_of_ride = choice['trip_time_in_secs'].values[0]
        distance_of_ride = choice['trip_distance'].values[0]
        
        profit = choice['profit'].values[0]
        print "Gas price for distance = ", gas_price_for_distance(distance_of_ride)
        print choice
        profit -= gas_price_for_distance(distance_of_ride)
        
#         print "ending_pos",ending_pos
#         print "time_of_ride",time_of_ride
#         print "distance_of_ride",distance_of_ride
#         print "profit",profit


        return ending_pos, profit, time_of_ride, distance_of_ride
    except Exception:
        print "Penalty!"
        return None, PENALTY_PROFIT_BAD_POS, PENALTY_TIME_BAD_POS, None

def better_position(starting_pos):
    """
    Determine a list of positions that good drivers frequent.

    Return the a list of positions that we think it would be worth to go to.
    """
    expected_profit_incl_travel = expected_profit_for_good_locations.apply( 
                            lambda z: z + time_and_gas_estimated_cost_function(z.name, starting_pos) , axis = 1)
    
    if starting_pos not in expected_profit.index:
        return None
        
    expected_profit_do_nothing = expected_profit.loc[starting_pos].values[0]
    
    good_choices = expected_profit_incl_travel
    good_choices = good_choices[good_choices.profit > expected_profit_do_nothing ]
    if len(good_choices.index) > 0:
        return good_choices.profit.argmax()
        
        #Another option is to sample randomly
        #return good_choices.sample(1).index.values[0]
    else:
        return None

def trip_time_and_distance(starting_pos, to_position):
    """
    Determine the average time of travel and trip distance according to
    NYC taxi rides.
    """
    dist = None
    drive_time = None
    try:
        dist = taxi_distance.loc[[starting_pos,to_position]]['trip_distance'].values[0]
        drive_time_in_sec = taxi_distance.loc[[starting_pos,to_position]]['trip_time_in_secs'].values[0]
    except Exception as e:
        pass

    return dist, drive_time_in_sec
    
def time_and_gas_estimated_cost_function(starting_pos, to_position):
    
    dist, drive_time_in_sec = trip_time_and_distance(starting_pos, to_position)
        
    if dist == None or drive_time_in_sec == None or dist > 1.5:
        return -100
    else:
        #This is gas price + travel time.
        return -1*(3.6*dist/29.0 + ((drive_time_in_sec/float(60*60))*COST_OF_TRAVEL_TIME_DOLLARS_HR))
    
def gas_price(start_pos, to_position):
    s_long, s_lat = [float(z) for z in starting_pos[1:-1].split(",")]
    d_long,d_lat = [float(z) for z in to_position[1:-1].split(",")]
    dist = vincenty((d_lat, d_long), (s_lat, s_long), miles=True)

    return 3.6*dist/29.0

def gas_price_for_distance(dist):
    return 3.6*dist/29.0

# def travel_time_in_seconds(starting_pos, to_position):
    
#     s_long, s_lat = [float(z) for z in starting_pos[1:-1].split(",")]
#     d_long,d_lat = [float(z) for z in to_position[1:-1].split(",")]
#     dist = vincenty((d_lat, d_long), (s_lat, s_long), miles=True)
    
#     return dist/float(DRIVING_SPEED_IN_MPH)

def simulate_naive_trajectory(rides, starting_position, starting_hour, max_trip_length_seconds):
    """
    Simulate the naive strategy of just doing a pickup wherever you are. 
    """
    current_pos = starting_position
    profit = 0
    remaining_seconds = max_trip_length_seconds
    while remaining_seconds > 0:

        #Pick a random ride.
        ending_pos, added_profit, time_of_ride, distance_of_ride = random_ride(rides, current_pos, starting_hour)
        #ending_pos, added_profit, length_of_ride = 
        profit += added_profit
        print "-",
        remaining_seconds -= time_of_ride + floor(random()*OVERALL_AVG_WAIT_TIME)
        if ending_pos != None:
            current_pos = ending_pos
    return profit

def simulate_informed_trajectory(rides, starting_position, starting_hour, max_trip_length_seconds):
    """
    Simulate the naive strategy of just doing a pickup wherever you are. 
    """
    current_pos = starting_position
    profit = 0
    remaining_seconds = max_trip_length_seconds
    while remaining_seconds > 0:

        #Pick a random ride.
        print "Picking new random ride. Current profit = ", profit
        ending_pos, added_profit, time_of_ride, distance_of_ride = random_ride(rides, current_pos, starting_hour)
        #ending_pos, added_profit, length_of_ride = random_ride(rides, current_pos, starting_hour)
        print "Got added profit = ", added_profit
        profit += added_profit
        remaining_seconds -= time_of_ride
        
        print "-",
        
        if ending_pos != None:
            #Would informed drivers make a different choice?
            p =  better_position(ending_pos)
            if p != None:
                print "Better Position \n\t" + reverse_geocode(ending_pos) + "\n\t" + reverse_geocode(p)
                current_pos = p
                drive_dist, drive_time_in_sec = trip_time_and_distance(ending_pos, p)
                print "\tdrive_dist = ", drive_dist
                print "\tdrive_time_in_sec", drive_time_in_sec
                
                #Update time remaining, and profit based on gas cost
                remaining_seconds -= drive_time_in_sec
                print "\tPrice of gas : ", gas_price_for_distance(drive_dist)
                profit -= gas_price_for_distance(drive_dist)
                
                print "\tProfit = ", profit
                #Model wait time at new position.
                remaining_seconds -= floor(random()*GOOD_POSITION_WAIT_TIME)

                #print "*",
                print "\tTrying better position: %.2f minutes lost."%(float(drive_time_in_sec)/(60.0))
                continue
            
            current_pos = ending_pos
            
        remaining_seconds -= floor(random()*OVERALL_AVG_WAIT_TIME)
        print "Profit = ", profit

    return profit

def reverse_geocode(pos):
    """
    Given a longitude, latitude pair, reverse geocode and print it.
    """
    return "Skip geocoding" + str(pos)
    lon, lat = [float(z) for z in pos.strip().replace("(", "").replace(")","").split(",")]
    address = geocoder.google([lat, lon], method='reverse').address
    
    if address == None:
        return ""
    else:
        return address

def train(rides):
    """
    Train the ML algorithm on the given dataset.

    Training data is saved in TRAINING_DIR, and loaded in the ML algorithm.
    """

    X = rides.groupby('pos').size()
    good_positions = X[ X > X.quantile(.8)]

    good_positions.to_csv(TRAINING_DIR + "good_positions.csv")
    #Determine Expected Profit
    expected_profit = rides[['pos','profit']]
    expected_profit = expected_profit[(expected_profit.profit < 200) & (expected_profit.profit > -5)]
    expected_profit = expected_profit.groupby('pos').mean()
    expected_profit.to_csv(TRAINING_DIR + "expected_profit.csv")