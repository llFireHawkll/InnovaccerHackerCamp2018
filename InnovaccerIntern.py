###########################INNOVACCER HACKERCAMP SUMMER INTERN ASSIGNMENT###############################

import os                                   # For OS related operations
import dedupe                               # For ML stuff
import pandas as pd                         # For Data Management and Representation

# Loading the Dataset
Data = pd.read_csv('./Train.csv')
print("\n")
print("Loading The Training Dataset.........")
print(Data.head())

print("\n")
print("Dataset Shape...........")
print(Data.shape)
print("\n")
print("Dataset Columns/Features......")
print(Data.dtypes)
print("\n")
print("\n")
   
Data['ID'] = range(len(Data.index))
Train = Data.to_dict('ID')

settings_file = 'csv_example_learned_settings'
training_file = 'csv_example_training.json'


# If a settings file already exists, we'll just load that and skip training
if os.path.exists(settings_file):
    print('reading from', settings_file)
    print("\n")
    with open(settings_file, 'rb') as f:
        deduper = dedupe.StaticDedupe(f)
else:
    # ## Training

    # Define the fields dedupe will pay attention to
    fields = [
            {'field' : 'ln', 'type': 'String'},
            {'field' : 'dob', 'type': 'String'},
            {'field' : 'gn', 'type': 'String'},
            {'field' : 'fn', 'type': 'String'},
        ]

    # Create a new deduper object and pass our data model to it.
    deduper = dedupe.Dedupe(fields)

    # To train dedupe, we feed it a sample of records.
    deduper.sample(Train, 15000)

    # If we have training data saved from a previous run of dedupe,
    # look for it and load it in.
    # __Note:__ if you want to train from scratch, delete the training_file
    if os.path.exists(training_file):
        print('reading labeled examples from ', training_file)
        with open(training_file, 'rb') as f:
            deduper.readTraining(f)

    # ## Active learning
    # Dedupe will find the next pair of records
    # it is least certain about and ask you to label them as duplicates
    # or not.
    # use 'y', 'n' and 'u' keys to flag duplicates
    # press 'f' when you are finished
    print('starting active labeling...')
    dedupe.consoleLabel(deduper)

    # Using the examples we just labeled, train the deduper and learn
    # blocking predicates
    deduper.train()

    # When finished, save our training to disk
    with open(training_file, 'w') as tf:
        deduper.writeTraining(tf)

    # Save our weights and predicates to disk.  If the settings file
    # exists, we will skip all the training and learning next time we run
    # this file.
    with open(settings_file, 'wb') as sf:
        deduper.writeSettings(sf)


threshold = deduper.threshold(Train, recall_weight=1)
print("\n")
print("\n")
print('Making Cluster Of Similar Names..........')
clustered_dupes = deduper.match(Train, threshold)
print(clustered_dupes)
print("\n")

for (cluster_id, cluster) in enumerate(clustered_dupes):
    id_set, scores = cluster
    cluster_d = [Train[c] for c in id_set]
    print(cluster_d)
    print()

list1 = [] # list1 contains all the entries for duplicate record clusters for ex. (66, 67, 68, 69, 70, 71, 72, 73, 74)
list2 = [] # list2 contains the first entry of the duplicate record for each cluster we have found for ex.(66)
newlist = [] # newlist contains the entries except list2 which is for ex. (67, 68, 69, 70, 71, 72, 73, 74)
finallist = [] # finallist contains all the indexes except those present in newlist


for (cluster_id, cluster) in enumerate(clustered_dupes):
    list2.append(cluster[0][0])
    for i in cluster[0]:
        list1.append(i)

newlist = list(set(list1) - set(list2))

for i in range(Data.shape[0]):
    finallist.append(i)

finallist = list(set(finallist) - set(newlist))


FinalDF = pd.DataFrame(columns=['ln','dob','gn','fn'])
for i in finallist:
    FinalDF = FinalDF.append(Data.iloc[i])

FinalDF = FinalDF.drop(['ID'], axis=1)

filename = 'Train_Correct.csv'
FinalDF.to_csv(filename, index=False)

print('\n')


########### Testing The Model With Test Dataset ###########

TestData = pd.read_csv('Test.csv')
print("Loading The Test Dataset.........")
print(TestData.head())

TestData['ID'] = range(len(TestData.index))
Test = TestData.to_dict('ID')

print('\n')
clustered_dupes = deduper.match(Test, threshold)
print('Making Cluster Of Similar Names..........')
print(clustered_dupes)

for (cluster_id, cluster) in enumerate(clustered_dupes):
    id_set, scores = cluster
    cluster_d = [Test[c] for c in id_set]
    print(cluster_d)
    print()

list1 = [] # list1 contains all the entries for duplicate record clusters for ex. (66, 67, 68, 69, 70, 71, 72, 73, 74)
list2 = [] # list2 contains the first entry of the duplicate record for each cluster we have found for ex.(66)
newlist = [] # newlist contains the entries except list2 which is for ex. (67, 68, 69, 70, 71, 72, 73, 74)
finallist = [] # finallist contains all the indexes except those present in newlist


for (cluster_id, cluster) in enumerate(clustered_dupes):
    list2.append(cluster[0][0])
    for i in cluster[0]:
        list1.append(i)

newlist = list(set(list1) - set(list2))

for i in range(TestData.shape[0]):
    finallist.append(i)

finallist = list(set(finallist) - set(newlist))

FinalDF = pd.DataFrame(columns=['ln','dob','gn','fn'])
for i in finallist:
    FinalDF = FinalDF.append(TestData.iloc[i])

FinalDF = FinalDF.drop(['ID'], axis=1)

filename = 'Test_Correct.csv'
FinalDF.to_csv(filename, index=False)

