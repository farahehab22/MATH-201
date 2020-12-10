import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv("Dataset/MoviesSurvey.csv")

x = df[["Age", "Gender"]]
x["Gender"] = x["Gender"].apply(lambda x: 0 if x == "Male" else 1)
y = df["Genre 1"]

X_Train, X_Test, Y_Train, Y_Test = train_test_split(x, y,
                                                    test_size=0.1)  # X_Train , Y_Train the choosen data , X_Test,Y_Test the unchoosen one

model = DecisionTreeClassifier()
model.fit(X_Train, Y_Train)
predictions = model.predict(X_Test)
score = accuracy_score(Y_Test, predictions)
print("Accuracy Score is : ", score)


def getSuggestedGeneresFromAgeAndGender(Age, Gender):
    return model.predict([[Age, (0 if Gender == "Male" else 1)]])
