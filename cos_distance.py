#Рассчитываем косинусное расстояние для кр
#https://habr.com/ru/post/150399/

import csv
import math

#обходим tuple unpacking in python 3

def star(f):
  return lambda args: f(*args)

def ReadFile (filename = "cos.csv"):
    f = open (filename)
    r = csv.reader (f)
    mentions = dict()
    for line in r:
        user = line[0]
        product = line[1]
        rate = float(line[2])
        if not user in mentions:
            mentions[user] = dict()
        mentions[user][product] = rate
    f.close()
    return mentions

def distCosine (vecA, vecB):
    def dotProduct (vecA, vecB):
        d = 0.0
        for dim in vecA:
            if dim in vecB:
                d += vecA[dim]*vecB[dim]
        return d
    return dotProduct (vecA,vecB) / math.sqrt(dotProduct(vecA,vecA)) / math.sqrt(dotProduct(vecB,vecB))

def makeRecommendation (userID, userRates, nBestUsers, nBestProducts):
    matches = [(u, distCosine(userRates[userID], userRates[u])) for u in userRates if u != userID]
    bestMatches = sorted(matches, key=star(lambda x,y: (y ,x)), reverse=True)[:nBestUsers]
    print ("Most correlated with '%s' users:" % userID)
    for line in bestMatches:
        print ("  UserID: %6s  Coeff: %6.4f" % (line[0], line[1]))
    sim = dict()
    sim_all = sum([x[1] for x in bestMatches])
    bestMatches = dict([x for x in bestMatches if x[1] > 0.0])
    for relatedUser in bestMatches:
        for product in userRates[relatedUser]:
            if not product in userRates[userID]:
                if not product in sim:
                    sim[product] = 0.0
                sim[product] += userRates[relatedUser][product] * bestMatches[relatedUser]
    for product in sim:
        sim[product] /= sim_all
    bestProducts = sorted(sim.items(), key=star(lambda x,y: (y,x)), reverse=True)[:nBestProducts]
    print ("Most correlated products:")
    for prodInfo in bestProducts:
        print ("  ProductID: %6s  CorrelationCoeff: %6.4f" % (prodInfo[0], prodInfo[1]))
    return [(x[0], x[1]) for x in bestProducts]

if __name__ == '__main__':
    rec = makeRecommendation('ivan', ReadFile(), 5, 5)
    print ('...end of calculations...')