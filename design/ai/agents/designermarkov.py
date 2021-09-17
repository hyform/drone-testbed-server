import pickle
import random
import math


class DesignerMarkov():


    def __init__(self):

        first_order_markov_d = pickle.load( open( "static/ai/designer_first_order_markov", "rb" ) )
        design_cache = pickle.load( open( "static/ai/design_cache_first_order_markov", "rb" ) )

        number_of_designer_events_dist = [0.466666667, 0.666666667, 1, 0.933333333, 0.8, 0.666666667, 0.4, 0.1, 0.033333333, 0.133333333]
        for ind in range(10):
            chain = []
            config = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3"
            MM = self.sample_from_binned_dist(number_of_designer_events_dist, 9, 374)
            for i in range(MM):

                if "Submit" in config:
                    d = config.split(":")[1]
                    print(ind, d, "Submit", design_cache[d][0], design_cache[d][1], design_cache[d][2])
                if "Evaluated" in config:
                    d = config.split(":")[1]
                    #print(ind, d, "Evaluated", design_cache[d][0], design_cache[d][1], design_cache[d][2])
                if "Open" in config:
                    d = config.split(":")[1]
                    #print(ind, d, "Open", design_cache[d][0], design_cache[d][1], design_cache[d][2])
                if "SelectedAI" in config:
                    d = config.split(":")[1]
                    #print(ind, d, "SelectedAI", design_cache[d][0], design_cache[d][1], design_cache[d][2])
                chain.append(config)

                # are we stuck
                stuck = False;
                M = 20
                if len(chain) > M:
                    test = {}
                    for j in range(len(chain) - M, len(chain)):
                        test[chain[j]] = 't'
                    stuck = len(test) <= 5

                options = first_order_markov_d[config]
                if len(options) == 0 or stuck and config != "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3":
                    # reset design
                    config = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3"
                else:
                    config = options[random.randrange(len(options))]
                    # if open, this is where the adaptive key could change based on the configuration



    def sample_from_binned_dist(self, bin_probs, minimum, maximum):
        sample = True
        counter = 0    # prevent infinite loop (if given a inefficient list bin_probs (ex 0.0001, 0, 0.001))
        while sample and counter < 1000:
            counter += 1
            x = random.random()
            y = random.random()
            bin = min(math.floor(x*len(bin_probs)),len(bin_probs) - 1)  # get the bin of the x position
            if y <= bin_probs[bin]:                                     # if y is less than the height of the bin
                return round(minimum + x*(maximum - minimum))
        return -1
