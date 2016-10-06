from ml_helper_functions import *
from helper_functions import *
from pre_process import *

import pandas as pd

DATA_DIR = "./"
TRAINING_DIR = DATA_DIR + "training/"

if __name__ == "__main__":
	print "This function trains the ML model based on rides.csv. Output is in " + TRAINING_DIR + "\n\n"
    print "Reading data...",
    rides = pd.read_csv(DATA_DIR + "rides.csv")
    print "done."
    print "Training...",
    train(rides)
    print "done."