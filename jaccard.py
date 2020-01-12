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

    similarity_matrix = sim_matrix(film_counts)
    print('Матрица схожести: ',similarity_matrix)