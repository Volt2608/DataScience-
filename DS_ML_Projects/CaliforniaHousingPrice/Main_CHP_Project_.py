
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd


MODEL_FILENAME = 'model.pkl'
PIPELINE_FILENAME = 'pipeline.pkl'

def build_pipeline( num_cols, cat_cols ):
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("oneHot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    full_pipeline = ColumnTransformer([
        ("num", num_pipeline, num_cols),
        ("cat", cat_pipeline, cat_cols)
    ])
    return full_pipeline

if not os.path.exists(MODEL_FILENAME):
    CHPdata = pd.read_csv("4CHP_Data.csv")

    CHPdata["income_cat"] = pd.cut(
        CHPdata["median_income"],
        bins=[0, 1.5, 3.0, 4.5, 6.0, np.inf],
        labels=[1, 2, 3, 4, 5])

    Shuffled = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_index, _ in Shuffled.split(CHPdata, CHPdata["income_cat"]):
        CHPdata = CHPdata.loc[train_index].drop("income_cat", axis=1)

    CHPdata_feature = CHPdata.drop("median_house_value", axis=1)
    CHPdata_label = CHPdata["median_house_value"].copy()

    num_col = CHPdata_feature.drop("ocean_proximity", axis=1).columns.tolist()
    cat_col = ["ocean_proximity"]

    pipeline = build_pipeline(num_col, cat_col)
    CHPdata_prepared = pipeline.fit_transform(CHPdata_feature)

    model = RandomForestRegressor(random_state=26)
    model.fit(CHPdata_prepared, CHPdata_label)

    joblib.dump(model, MODEL_FILENAME)
    joblib.dump(pipeline, PIPELINE_FILENAME)

    print("Model is trained and saved successfully!")

else :
    model = joblib.load(MODEL_FILENAME)
    pipeline = joblib.load(PIPELINE_FILENAME)

    input_data = pd.read_csv("input.csv")
    transformed_input = pipeline.transform(input_data)
    predictions = model.predict(transformed_input)
    input_data["median_house_value"] = predictions

    input_data.to_csv("output.csv", index=False)
    print("Inference completed. Results saved to output.csv")


















