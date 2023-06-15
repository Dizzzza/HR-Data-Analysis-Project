import pandas as pd
import requests
import os

data1 = pd.read_xml('../Data/A_office_data.xml')
data2 = pd.read_xml('../Data/B_office_data.xml')
data3 = pd.read_xml('../Data/hr_data.xml')

data1.set_index('employee_office_id', drop=False, inplace=True)
data2.set_index('employee_office_id', drop=False, inplace=True)
data3.set_index('employee_id', drop=False, inplace=True)

new_index = ['A' + str(i) for i in data1.index]
data1 = data1.rename(index=dict(zip(data1.index, new_index)))
new_index = ['B' + str(i) for i in data2.index]
data2 = data2.rename(index=dict(zip(data2.index, new_index)))

data_full = pd.concat([data1, data2], axis=0)

data_full = data_full.merge(data3, how='left', indicator=True, left_index=True, right_index=True)

data_full = data_full[data_full['_merge'] == 'both']

data_full.drop(['_merge', 'employee_id', 'employee_office_id'], axis=1, inplace=True)
data_full.sort_index(inplace=True)

data_spend_hours = data_full.loc[:,['Department', 'average_monthly_hours']]
data_spend_hours.sort_values('average_monthly_hours', ascending=False, inplace=True)
data_spend_hours.reset_index(inplace=True)
arr2 = []
for i in range(10):
    arr2.append(data_spend_hours.loc[i, 'Department'])

data_salary = data_full.loc[:, ['Department', 'salary', 'number_project']]
data_salary.query("Department == 'IT' & salary == 'low'", inplace=True)
arr3 = []
def ev_sat(df, name):
    arr_ex = []
    arr_ex.append(df.loc[name, "last_evaluation"])
    arr_ex.append(df.loc[name, "satisfaction_level"])
    return arr_ex

arr3.append(ev_sat(data_full, "A4"))
arr3.append(ev_sat(data_full, "B7064"))
arr3.append(ev_sat(data_full, "A3033"))

def count_bigger_5(series):
    return series.where(series > 5).count()

new_data = data_full.groupby('left').agg({'number_project': ['median',count_bigger_5],
                                          'time_spend_company': ['mean', 'median'],
                                          'Work_accident': 'mean',
                                          'last_evaluation': ['mean','std']})
new_data = new_data.round(2)

piv_data1 = data_full.pivot_table(index='Department', columns=['left', 'salary'], values='average_monthly_hours', aggfunc='median')
piv_data2 = data_full.pivot_table(index='time_spend_company', columns='promotion_last_5years',
                                  values=['last_evaluation', 'satisfaction_level'],
                                  aggfunc=['max', 'mean', 'min'])
piv_data1 = piv_data1.where((piv_data1[(0.0, 'high')] < piv_data1[(0.0, 'medium')]) |
                            (piv_data1[(1.0, 'low')] < piv_data1[(1.0, 'high')]))
piv_data2 = piv_data2.where(piv_data2[('mean', 'last_evaluation', 0)] > piv_data2[('mean', 'last_evaluation', 1)])
piv_data1 = piv_data1.round(2)
piv_data2 = piv_data2.round(2)
piv_data1.dropna(axis=0, inplace=True)
piv_data2.dropna(axis=0, inplace=True)
print(piv_data1.to_dict())
print(piv_data2.to_dict())
