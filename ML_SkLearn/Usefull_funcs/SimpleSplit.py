

import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("4CHP_Data.csv")

_ , sample_20 = train_test_split(df,test_size=0.2,random_state=42,shuffle=True)

sample_20.to_csv("input.csv", index=False)

print("Saved 20% shuffled data to input.csv")
