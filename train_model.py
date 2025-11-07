import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score


def load_data(filename):
    print("loading data")
    return pd.read_csv(filename)


def prepare_data(df):
    print("preparing data")

    # Fill artist missed 0
    df["artist_popularity"] = df["artist_popularity"].fillna(0)
    df["artist_followers"] = df["artist_followers"].fillna(0)
    # from coerce fill NaN with 0
    df["release_year"] = df["release_year"].fillna(0)
    df["release_month"] = df["release_month"].fillna(0)
    df["release_day_of_week"] = df["release_day_of_week"].fillna(0)

    # features all numerical columns to predict, leave text like name
    feature_columns = [
        "is_collaboration",
        "num_artists",
        "track_name_length",
        "release_year",
        "release_month",
        "release_day_of_week",
        "is_explicit",
        "artist_popularity",
        "artist_followers",
    ]

    X = df[feature_columns]
    y = df["popularity"]  # target

    # split data to train/test; 80% train and 20% test; random_state same "shuffle" every run
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_and_evaluate(X_train, X_test, y_train, y_test):
    print("Data Split")
    print(f"Training set size: {len(X_train)} songs")
    print(f"Testing set size: {len(X_test)} songs")

    print("training model")
    model = RandomForestRegressor(
        n_estimators=100, random_state=42, n_jobs=-1
    )  # n estimate= n decision trees working together.
    model.fit(X_train, y_train)

    print("evaluating model")
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MSE: {mse:.2f}")
    print(f"R²: {r2:.2f}")
    return model


def plot_importances(model, X_train):
    print("plot feature importances")
    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame(
        {"feature": X_train.columns, "importance": importances}
    )
    feature_importance_df = feature_importance_df.sort_values(
        by="importance", ascending=False
    )

    plt.figure(figsize=(12, 8))
    sns.barplot(
        x="importance",
        y="feature",
        data=feature_importance_df,
        palette="viridis",
        hue="feature",
        legend=False,
    )
    plt.title("Which Features Matter Most?")
    plt.xlabel("Importance Score")
    plt.ylabel("Feature")
    plt.savefig("feature_importance.png")
    print("Saved feature importance plot to 'feature_importance.png'")


def main():
    df = load_data("model_ready_data.csv")

    # prepare training
    X_train, X_test, y_train, y_test = prepare_data(df)

    # train & evaluate
    model = train_and_evaluate(X_train, X_test, y_train, y_test)

    # plot results
    plot_importances(model, X_train)


if __name__ == "__main__":
    main()
