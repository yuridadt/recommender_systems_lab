import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, coo_matrix
from lightfm import LightFM
from lightfm.evaluation import precision_at_k, auc_score

def _shuffle(uids, iids, data, random_state):
    shuffle_indices = np.arange(len(uids))
    random_state.shuffle(shuffle_indices)
    return (uids[shuffle_indices],
            iids[shuffle_indices],
            data[shuffle_indices])

def random_train_test_split(interactions_df, test_percentage=0.25,random_state=None):
    '''
    Функция принимаем датафрейм и создает тренировочную и тестовую выборки в формате scipy sparse_matrix
    '''
    interactions = csr_matrix(interactions_df.values)
    if random_state is None:
        random_state = np.random.RandomState()
    interactions = interactions.tocoo()
    shape = interactions.shape
    uids, iids, data = (interactions.row,
                        interactions.col,
                        interactions.data)
    uids, iids, data = _shuffle(uids, iids, data, random_state)
    cutoff = int((1.0 - test_percentage) * len(uids))
    train_idx = slice(None, cutoff)
    test_idx = slice(cutoff, None)
    train = coo_matrix((data[train_idx],
                               (uids[train_idx],
                                iids[train_idx])),
                              shape=shape,
                              dtype=interactions.dtype)
    test = coo_matrix((data[test_idx],
                          (uids[test_idx],
                           iids[test_idx])),
                         shape=shape,
                         dtype=interactions.dtype)
    return train, test

if __name__ == "__main__":

    df = pd.read_csv('ratingsABDwithgaps.csv',sep = ';', index_col=0).fillna(0)
    sparse_matrix = csr_matrix(df.values)
    #df = df.stack().reset_index(level=1)
    train, test = random_train_test_split(df)

    #Примениение гибридное рекомендательной системы в библиотеке LightFM
    # bpr - оптимизирует AUC
    model = LightFM(learning_rate=0.05, loss='bpr')
    model.fit(train, epochs=10)

    train_precision = precision_at_k(model, train, k=10).mean()
    test_precision = precision_at_k(model, test, k=10).mean()
    train_auc = auc_score(model, train).mean()
    test_auc = auc_score(model, test).mean()
    print('BPR Precision: train %.2f, test %.2f.' % (train_precision, test_precision))
    print('BPR AUC: train %.2f, test %.2f.' % (train_auc, test_auc))

    # Примениение гибридное рекомендательной системы в библиотеке LightFM
    # warp - оптимизирует precision
    model = LightFM(learning_rate=0.05, loss='warp')
    model.fit_partial(train, epochs=10)
    train_precision = precision_at_k(model, train, k=10).mean()
    test_precision = precision_at_k(model, test, k=10).mean()
    train_auc = auc_score(model, train).mean()
    test_auc = auc_score(model, test).mean()
    print('WARP Precision: train %.2f, test %.2f.' % (train_precision, test_precision))
    print('WARP AUC: train %.2f, test %.2f.' % (train_auc, test_auc))
    print('...end of calculations...')