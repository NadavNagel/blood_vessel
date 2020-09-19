from blood_vessel.data_saver import *import pandas as pdfrom sklearn import linear_modelimport warningswarnings.filterwarnings('ignore')import matplotlib.pyplot as pltimport numpy as npimport torchimport numpy as npfrom torch.utils.data import TensorDataset, DataLoaderX = Nonetraining_files = ['batch43_obs0_99.pickle', 'batch43_obs100_199.pickle', 'batch43_obs200_399.pickle']test_file = 'batch43_obs200_299.pickle'def get_data_for_model(data):    X = None    for i in range(len(data)):        x = data[i].low_resolution.displacement_mesh.points.reshape(1720, 2 ,3)        y = data[i].high_resolution.strain_mesh.points.reshape(12127, 7, 3)        x = np.expand_dims(x, axis=0)        y = np.expand_dims(y, axis=0)        if X is None:            X = x            Y = y        else:            X = np.concatenate([X, x], axis=0)            Y = np.concatenate([Y, y], axis=0)    tensor_x = torch.Tensor(X)    tensor_y = torch.Tensor(Y)    # my_dataset = TensorDataset(tensor_x, tensor_y)    # my_dataloader = DataLoader(my_dataset)    return tensor_x, tensor_y ##my_dataloader##training_data = []for training_file in training_files:    training_data_temp = read_pickle(training_file)    training_data = training_data_temp + training_datatest_data = read_pickle(test_file)X_train, Y_train = get_data_for_model(training_data)train_data = TensorDataset(X_train, Y_train)train_loader = DataLoader(train_data,                          batch_size=64,                          shuffle=True)print('')# results = {}# centers = (350, 576, 1678, 2002) ##range(500, 600)  # range(100, 3000, 100)# for center in centers:#     results[center] = {}#     results[center]['crop_size'] = []#     results[center]['r_sqr'] = []#     for crop_size in range(1, 75):#         results[center]['crop_size'].append(crop_size)#         X_train, Y_train = get_data_for_model(training_data, crop_size, center)#         regression_model = linear_model.LinearRegression()#         regression_model.fit(X_train, Y_train)#         X_test, Y_test = get_data_for_model(test_data, crop_size, center)#         r_sqr_test = regression_model.score(X_test, Y_test)#         results[center]['r_sqr'].append(r_sqr_test)#         # print(regression_model.intercept_, regression_model.coef_)#     plt.plot(results[center]['crop_size'], results[center]['r_sqr'], label=center)## plt.legend()# plt.show()