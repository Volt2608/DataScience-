from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
import warnings

from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings("ignore", category=RuntimeWarning)


# Step 1. Loading the DataSet - California Housing Price, Source : Kaggle
CHPdata = pd.read_csv("4CHP_Data.csv")

# Step 2. Creating stratified shuffled set Train and Test
CHPdata["income_cat"] = pd.cut(
    CHPdata["median_income"],
    bins=[0, 1.5, 3.0, 4.5, 6.0, np.inf],
    labels=[1, 2, 3, 4, 5]
)

Shuffled = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_index, test_index in Shuffled.split(CHPdata, CHPdata["income_cat"]):
    strat_train_set = CHPdata.loc[train_index].drop("income_cat", axis=1)
    strat_test_set = CHPdata.loc[test_index].drop("income_cat", axis=1)

# Copy full training data
CHPdata = strat_train_set.copy()

# Step 3. Separating features & labels
data_feature = CHPdata.drop("median_house_value", axis=1)
data_label = CHPdata["median_house_value"].copy()

# Step 4. attribute lists, later to use in the pipeline :
num_cols = data_feature.drop("ocean_proximity", axis=1).columns.tolist()
cat_cols = ["ocean_proximity"]

# Step 5. pipelines
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

# Step 6. Transform the data
housing_prepared = full_pipeline.fit_transform(data_feature)

# Train the model
lin_reg = LinearRegression()   # Linear Regression
lin_reg.fit(housing_prepared, data_label)
lin_preds = lin_reg.predict(housing_prepared)
lin_mse = (mean_squared_error(data_label, lin_preds))

# Decision Tree
tree_reg = DecisionTreeRegressor()
tree_reg.fit(housing_prepared, data_label)
tree_preds = tree_reg.predict(housing_prepared)
tree_mse = (mean_squared_error(data_label, tree_preds))

# Random Forest
rf_reg = RandomForestRegressor()
rf_reg.fit(housing_prepared, data_label)
rf_preds = rf_reg.predict(housing_prepared)
rf_mse = (mean_squared_error(data_label, rf_preds))

print(f"Linear Regression MSE: {lin_mse}")
print(f"Random Forest MSE: {rf_mse}")
print(f"Decision Tree MSE: {tree_mse}")



