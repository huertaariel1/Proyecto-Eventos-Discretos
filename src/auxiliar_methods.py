import random
import math

def uniform(a,b):
    U = random.random()
    X = a + (b - a) * U
    return X
        
def exponential_inverse_trans(_lambda):
    U = random.random()
    X = -(1/_lambda) * math.log(U)
    return X

def get_max_children_number(p):
    if p < 0.6:
        if p < 0.75:
            if p < 0.35:
                if p < 0.2:
                    if p < 0.1:
                        if p < 0.05:
                            return 1000
                        return 5
                    return 4
                return 3
            return 2
        return 1
    return 0

def get_multipregnancy_count(p):
    if p < 0.7:
        return 1
    elif p < 0.7 + 0.18:
        return 2
    elif p < 0.7 + 0.18 + 0.06:
        return 3
    elif p < 0.7 + 0.18 + 0.06 + 0.04:
        return 4
    else:
        return 5

