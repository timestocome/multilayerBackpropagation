
# https://github.com/timestocome
# https://www.kaggle.com/c/LANL-Earthquake-Prediction

# read in statistical files created and test models using cross validation 
# to identify useful features


################################################################################
# libraries
################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


##################################################################################
# print settings
##################################################################################
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 1000)

np.set_printoptions(precision=10)



###################################################################################
# read training data that was created with prep_data.py, 
# split into train and hold out sets
###################################################################################
print('Reading data.............................')


features = [
	'gt_2std', 
	'gt_3std', 
	'power1', 
	'power2', 
	'power3',
	'power4', 
	'median_dev_abs', 
]

print('n features', len(features))


# read in raw data
data = pd.read_csv('stats_data.csv', index_col=0)
print('length data', len(data))

#eatures = list(data.columns.values)
#features.remove('time_to_failure')

targets = ['time_to_failure']

x = data[features][0:7500]
y = data['time_to_failure'][0:7500]

x_holdout = data[features][7500:len(data)]
y_holdout = data['time_to_failure'][7500:len(data)]



print(data.columns.values)
print('********************************************************************************')
print('starting features')
print(features)
print('--------------------------------------------------------------------------------')
print('Samples %d' %(len(x)))


#########################################################################################
# import sklearn libraries for model
#########################################################################################
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score



print('Splitting data')
# split data up into features, targets, train and test sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)




# create model
clf = RandomForestRegressor(n_estimators=256, n_jobs=6, max_depth=14, max_features=2, criterion='mse')



# train model using cross validation 
print('training....')

cv_results = cross_validate(clf, x_train, y_train, cv=5, return_train_score=True)
print('-----------------cv_results--------------------------')
print('Train: %f, std %f' % (np.mean(cv_results['train_score']) * 100., np.std(cv_results['train_score'])))
print('Test: %f std %f' % (np.mean(cv_results['test_score']) * 100., np.std(cv_results['test_score'])))




###################################################################################################
# re-fit classifier on all training data except holdout to check feature values
####################################################################################################
print('----------------------Feature importance--------------')
clf.fit(x, y)
feature_values = zip(features, clf.feature_importances_)
feature_values = sorted(feature_values, key = lambda z: z[1])

for i, j in feature_values:
    print(' %s     %.9f ' %(i, j))




# check classifier accuracy on holdout data
predict_test = clf.predict(x_holdout) 
y_test = y_holdout.values 

print('=========================================================================')
mae = (np.abs(predict_test - y_test )).mean()
print('mae error on hold out data', mae)
print('actual max/min', y_test.max(), y_test.min())
print('predicted max/min', predict_test.max(), predict_test.min())
print('=========================================================================')



###############################################################################################
# plot predictions vs actual on training data and holdout data
##############################################################################################

predict_train = clf.predict(data[features]) 
predict_y = data['time_to_failure']

fig, ax = plt.subplots(figsize=(16, 16))
plt.plot(predict_train, c='r', label='Predicted')
plt.plot(predict_y, c='b', label='Actual', alpha=0.3)
plt.legend()
plt.grid(True)
plt.savefig('predictions.png')
plt.show()



#############################################################################################
# retrain on all training data, including holdout, then run submission data through
# read in test data and run it through clf
# save submission file to upload to kaggle
#############################################################################################
# refit on all training data
x = data[features]
y = data['time_to_failure']
clf.fit(x, y)


# save training predictions might use later
predict = clf.predict(x)
np.savetxt('rf_train_predictions.csv', predict)



fig, ax = plt.subplots(figsize=(16, 16))
plt.plot(predict, c='r', label='Predicted')
plt.plot(y, c='b', label='Actual', alpha=0.3)
plt.legend()
plt.grid(True)
plt.savefig('predictions.png')
plt.show()



submission_data = pd.read_csv('stats_test.csv', index_col=0)


submission_data['time_to_failure'] = clf.predict(submission_data[features]) 
submission_data = submission_data[['seg_id','time_to_failure']]
submission_data.set_index('seg_id', inplace=True)

submission_data.to_csv('rf_submission.csv', header='seg_id,time_to_failure')

print('-----------------  finished --------------------')



