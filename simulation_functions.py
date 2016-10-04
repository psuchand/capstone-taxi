from random import random
from math import floor
from vincenty import vincenty

PENALTY_PROFIT_BAD_POS = -8
PENALTY_TIME_BAD_POS = 60*10
DRIVING_SPEED_IN_MPH = 20

COST_OF_TRAVEL_TIME_DOLLARS_HR = 42
OVERALL_AVG_WAIT_TIME = 11.4*60 #In Seconds

def random_ride(hotspots, from_position, starting_hour):
    """
    Randomly choose a ride from the given dataframe, at the specified position.    
    Sampling is done assuming the distribution of rides does not vary within the hour.
    """
    
    try:
        #Restrict to rides for the given position
        rides = hotspots[hotspots.pos == from_position]

        #Restrict to rides for the given hour
        rides = rides[(rides.hour == starting_hour) & (rides.pos == from_position)]

        choice = rides.sample(1)

        ending_pos = choice['dropoff_pos'].values[0]
        profit = choice['profit'].values[0]
        length_of_ride = choice['trip_time_in_secs'].values[0]

        return ending_pos, profit, length_of_ride
    except Exception:
        print "Penalty!"
        return None, PENALTY_PROFIT_BAD_POS, PENALTY_TIME_BAD_POS

def better_position(starting_pos):
    """
    Determine a list of positions that good drivers frequent.

    Return the a list of positions that we think it would be worth to go to.
    """
    expected_profit_incl_travel = expected_profit_for_good_locations.apply( 
                            lambda z: z + distance_loss(z.name, starting_pos) , axis = 1)
    

    if starting_pos not in expected_profit.index:
        return None

    expected_profit_do_nothing = expected_profit.loc[starting_pos].values[0]
    
    good_choices = expected_profit_incl_travel
    good_choices = good_choices[good_choices.profit > expected_profit_do_nothing]
    if len(good_choices.index) > 0:
        return good_choices.sample(1).index.values[0]
    else:
        return None

def distance_loss(starting_pos, to_position):

    s_long, s_lat = [float(z) for z in starting_pos[1:-1].split(",")]
    d_long,d_lat = [float(z) for z in to_position[1:-1].split(",")]
    dist = vincenty((d_lat, d_long), (s_lat, s_long), miles=True)

    return -1*(3.6*dist/29.0 + (dist/float(DRIVING_SPEED_IN_MPH))*COST_OF_TRAVEL_TIME_DOLLARS_HR)

def gas_price(start_pos, to_position):
    s_long, s_lat = [float(z) for z in starting_pos[1:-1].split(",")]
    d_long,d_lat = [float(z) for z in to_position[1:-1].split(",")]
    dist = vincenty((d_lat, d_long), (s_lat, s_long), miles=True)

    return -1*(3.6*dist/29.0)

def travel_time_in_seconds(starting_pos, to_position):
    
    s_long, s_lat = [float(z) for z in starting_pos[1:-1].split(",")]
    d_long,d_lat = [float(z) for z in to_position[1:-1].split(",")]
    dist = vincenty((d_lat, d_long), (s_lat, s_long), miles=True)
    
    return dist/float(DRIVING_SPEED_IN_MPH)

def simulate_naive_trajectory(rides, starting_position, starting_hour, max_trip_length_seconds):
    """
    Simulate the naive strategy of just doing a pickup wherever you are. 
    """
    current_pos = starting_position
    profit = 0
    remaining_seconds = max_trip_length_seconds
    while remaining_seconds > 0:

        #Pick a random ride.
        ending_pos, added_profit, length_of_ride = random_ride(rides, current_pos, starting_hour)
        profit += added_profit
        remaining_seconds -= length_of_ride + floor(random()*OVERALL_AVG_WAIT_TIME)
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
        ending_pos, added_profit, length_of_ride = random_ride(rides, current_pos, starting_hour)
        profit += added_profit
        remaining_seconds -= length_of_ride + floor(random()*OVERALL_AVG_WAIT_TIME)
        
        if ending_pos != None:
            #Would informed drivers make a different choice?
            p =  better_position(ending_pos)
            if p != None:
                current_pos = p
                travel_time_new_pos = travel_time_in_seconds(ending_pos, p)
                remaining_seconds -= travel_time_new_pos
                profit -= gas_price(ending_pos, p)
                print "*",
                #print "Trying better position: %.2f seconds lost."%travel_time_new_pos
                continue
                
            current_pos = ending_pos
                
    return profit

def reverse_geocode(pos):
    """
    Given a longitude, latitude pair, reverse geocode and print it.
    """
    lon, lat = [float(z) for z in pos.strip().replace("(", "").replace(")","").split(",")]
    return geocoder.google([lat, lon], method='reverse').address
    