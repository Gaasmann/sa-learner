#!/usr/bin/env python3

import pickle
from salearner.trainer import SALearner
from salearner.saconfig import ConfigGenerator
import time

# import pickle
with open('data.pickle', 'rb') as file_handler:
    data = pickle.load(file_handler)
# create an SALeaner object with learning_rate = 30
sa_learner = SALearner(data, 30)
# setup timer and go learn for 24800 cycles
begin = time.time()
sa_learner.init_graph()
sa_learner.learn(24,20,True)
print("{:.2f} seconds".format(time.time() - begin))
# Generate and save a SA user_prefs file
res = sa_learner.results
cg = ConfigGenerator(data['rules'], res['weights'], res['bias'][0,0])
conf = cg.get_config()
with open('/tmp/sa-score.conf', 'w')as a:
    a.write(conf)
