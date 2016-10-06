from ml_helper_functions import *

DATA_DIR = "./"
TRAINING_DIR = DATA_DIR + "training/"

if __name__ == "__main__":
    from helper_functions import *
    from pre_process import *
    print "Reading data...",
    rides = pd.read_csv(DATA_DIR + "rides.csv")
    print "done."
    print "Training...",
    train(rides)
    print "done."