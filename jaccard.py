import pandas as pd
from math import isnan

def sim_matrix(dict):
    similarity_matrix ={}
    for (movie1, people1) in dict.items():
        size_1 = len(people1)
        jac_dict = {}
        for (movie2, people2) in film_counts.items():
            if movie1 != movie2:
                size_2 = len(people2)
                intersect = list(set(people1).intersection(set(people2)))
                size_in = len(intersect)
                #рассчитываем расстояние Жаккара
                jaccard_distance = 1 - size_in / (size_1 + size_2 - size_in)
                jac_dict[movie2]= jaccard_distance
        similarity_matrix[movie1]= jac_dict
    return similarity_matrix

def association_method(dict,all_people):
    association_matrix ={}
    size_all = len(all_people)
    for (movie1, people1) in dict.items():
        size_1 = len(people1)
        size_not1 = size_all - size_1
        assoc_dict = {}
        for (movie2, people2) in film_counts.items():
            if movie1 != movie2:
                size_2 = len(people2)
                intersect = list(set(people1).intersection(set(people2)))
                size_in = len(intersect)
                intersect_not1_2 = list(all_people.intersection(set(people2)))
                size_not1_2 = len(intersect_not1_2)
                #рассчитываем метод ассоциаций
                association_distance = 1 - size_in * size_not1 / (size_1 * size_not1_2)
                assoc_dict[movie2]= association_distance
        association_matrix[movie1]= assoc_dict
    return association_matrix

if __name__ == "__main__":
    df = pd.read_csv('ratingsABDwithgaps.csv',sep = ';', index_col=0)#.T
    users_gaps = df.to_dict()
    #убираем пропущенные значения
    films ={}
    for key, value in users_gaps.items():
        films[key] = {k: value[k] for k in value if not isnan(value[k])}

    film_counts ={}
    for key, value in films.items():
        film_counts[key] = list(value.keys())

    #считаем всего пользователей
    all_people =set(df.index)

    similarity_matrix = sim_matrix(film_counts)
    print('Матрица схожести: ',similarity_matrix)

    association_matrix = association_method(film_counts, all_people)
    print('Матрица ассоциаций: ', association_matrix)