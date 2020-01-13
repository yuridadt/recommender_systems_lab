import pandas as pd
from math import isnan, sqrt

df = pd.read_csv('ratingsABDwithgaps.csv',sep = ';', index_col=0).T
users_gaps = df.to_dict()
#убираем пропущенные значения
users ={}
for key, value in users_gaps.items():
    users[key] = {k: value[k] for k in value if not isnan(value[k])}


class recommender:

    def __init__(self, data, k=1, metric='pearson', n=5):
        """
        k - для ближайших соседей
        metric - формула расстояния
        n максимальнео число рекомендаций
        """
        self.k = k
        self.n = n
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}

        self.frequencies = {}
        self.deviations = {}

        self.metric = metric
        if self.metric == 'pearson':
            self.fn = self.pearson

        # на вход принимаем только словари
        if type(data).__name__ == 'dict':
            self.data = data

    # здесь рассчитывается матрица отклонений
    def computeDeviations(self):
        for ratings in self.data.values():
            # первый пользователь и его рейтинг:
            for (item, rating) in ratings.items():
                self.frequencies.setdefault(item, {})
                self.deviations.setdefault(item, {})
                # вторйо пользователь и его рейтинг:
                for (item2, rating2) in ratings.items():
                    if item != item2:
                        # рассчитываем разницу
                        self.frequencies[item].setdefault(item2, 0)
                        self.deviations[item].setdefault(item2, 0.0)
                        self.frequencies[item][item2] += 1
                        self.deviations[item][item2] += rating - rating2

        for (item, ratings) in self.deviations.items():
            for item2 in ratings:
                ratings[item2] /= self.frequencies[item][item2]

    def slopeOneRecommendations(self, id):
        recommendations = {}
        frequencies = {}
        for (userItem, userRating) in self.data[id].items():
            # здесь смотрим фильмы, которые пользователь не оценил
            for (diffItem, diffRatings) in self.deviations.items():
                if diffItem not in self.data[id] and \
                        userItem in self.deviations[diffItem]:
                    freq = self.frequencies[diffItem][userItem]
                    recommendations.setdefault(diffItem, 0.0)
                    frequencies.setdefault(diffItem, 0)
                    # считаем рекомендации для отсутсвующго фильма
                    recommendations[diffItem] += (diffRatings[userItem] +
                                                  userRating) * freq
                    frequencies[diffItem] += freq
        recommendations = [(k,
                            v / frequencies[k])
                           for (k, v) in recommendations.items()]
        # сортируем
        recommendations.sort(key=lambda artistTuple: artistTuple[1],
                             reverse=True)
        return recommendations[:50]

    def pearson(self, rating1, rating2):
        ''' Вычисление коэффиицента Пирсона для двух величин'''
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        if n == 0:
            return 0
        # рассчитываем знаменатель
        denominator = (sqrt(sum_x2 - pow(sum_x, 2) / n)
                       * sqrt(sum_y2 - pow(sum_y, 2) / n))
        if denominator == 0:
            return 0
        else:
            return (sum_xy - (sum_x * sum_y) / n) / denominator


    def computeNearestNeighbor(self, username):
        """сортирует список пользователей, основываясь на их дистанции до username"""
        distances = []
        for instance in self.data:
            if instance != username:
                distance = self.fn(self.data[username],
                                   self.data[instance])
                distances.append((instance, distance))
        # сортируем и выдаем первого ближайшего
        distances.sort(key=lambda artistTuple: artistTuple[1],
                       reverse=True)
        return distances

    def recommend(self, user):
        """Give list of recommendations"""
        recommendations = {}
        # получаем лист соседей по близкости
        nearest = self.computeNearestNeighbor(user)
        userRatings = self.data[user]
        # задаем общ дистанцию
        totalDistance = 0.0
        for i in range(self.k):
           totalDistance += nearest[i][1]
        # рассчитываем веса для k ближайших соседей
        for i in range(self.k):
           weight = nearest[i][1] / totalDistance
           name = nearest[i][0]
           neighborRatings = self.data[name]
           # находим фильмы, которые не отмечены
           for artist in neighborRatings:
              if not artist in userRatings:
                 if artist not in recommendations:
                    recommendations[artist] = (neighborRatings[artist]
                                               * weight)
                 else:
                    recommendations[artist] = (recommendations[artist]
                                               + neighborRatings[artist]
                                               * weight)
        recommendations = list(recommendations.items())
        recommendations = [(k, v)
                           for (k, v) in recommendations]
        # сортируем и выдаем топ-n рекомендаций
        recommendations.sort(key=lambda artistTuple: artistTuple[1],
                             reverse = True)
        return recommendations[:self.n]


if __name__ == "__main__":

    #рассчитываем матрицу отклонений

    r = recommender(users)
    r.computeDeviations()
    dev = r.deviations
    print ('матрица отклонений = ', dev)

    #рассчитываем SlopeOne

    id = 'Дадтеев Юрий Олегович'
    slopeOne = r.slopeOneRecommendations(id)
    print('slope One для ' + id + '=', slopeOne)

    #рассчитываем ближайших соседей для пользователя,

    knn = r.computeNearestNeighbor(id)
    print('список ближайших соседей для ' + id + ':', knn)

    # получаем рекомендацию для пользователя на основании k его ближайших соседей,

    rec = r.recommend(id)
    print('рекомендуемые фильмы для' + id + ':', rec)
    print('...end of calculations...')