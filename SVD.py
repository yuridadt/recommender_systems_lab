import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
# строим рейтинговую матрицу
df = pd.read_csv('ratingsABDwithgaps.csv',sep = ';', index_col=0).fillna(0)

#получаем разряженую матрицу, которую нормализуем
R = df.as_matrix()
user_ratings_mean = np.mean(R, axis = 1)
R_demeaned = R - user_ratings_mean.reshape(-1, 1)

#выполняем разложение матрицы
U, sigma, Vt = svds(R_demeaned, k = 3)
#представляем в форме диагональнйо матрицы
sigma = np.diag(sigma)

#строим матрицу предсказаний для каждого пользователя
all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
preds_df = pd.DataFrame(all_user_predicted_ratings, columns = df.columns)
print('...end of calculations...')