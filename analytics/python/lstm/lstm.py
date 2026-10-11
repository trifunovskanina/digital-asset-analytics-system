import psycopg2
import numpy as np
import pandas as pd

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)

from sklearn.model_selection import train_test_split

LOOKBACK = 30
lags = list(range(LOOKBACK, 0, -1))

def load_ohlcv(symbol: str) -> pd.DataFrame:
    conn = psycopg2.connect(
        host="postgres",
        database="analytics",
        user="postgres",
        password="admin",
        port=5432,
    )

    query = """
        SELECT date, close
        FROM ohlcv
        WHERE symbol = %s
        ORDER BY date;
    """

    df = pd.read_sql_query(query, conn, params=(symbol,))
    conn.close()
    return df

def prepare_features(df: pd.DataFrame):
    df["date"] = pd.to_datetime(df["date"])
    df.head()
    df = df.set_index(keys="date")
    df = df.sort_index()
    return df


def create_lags(df):
    for lag in lags:
        df[f'close_{lag}'] = df["close"].shift(lag)
    df = df.dropna()
    return df


def split_data(df: pd.DataFrame):
    X, y = df.drop(columns="close"), df["close"].values

    train_X, test_X, train_y, test_y = train_test_split(
        X, y, test_size=0.3, shuffle=False
    )
    train_X, val_X, train_y, val_y = train_test_split(
        train_X, train_y, test_size=0.3, shuffle=False
    )

    scaler_x = StandardScaler()
    train_X = scaler_x.fit_transform(train_X)
    val_X = scaler_x.transform(val_X)
    test_X = scaler_x.transform(test_X)

    scaler_y = StandardScaler()
    train_y = scaler_y.fit_transform(train_y.reshape(-1, 1))
    val_y = scaler_y.transform(val_y.reshape(-1, 1))
    test_y = scaler_y.transform(test_y.reshape(-1, 1))

    # (samples, timesteps, features)
    train_X = train_X.reshape(train_X.shape[0], len(lags), train_X.shape[1] // len(lags))
    val_X = val_X.reshape(val_X.shape[0], len(lags), val_X.shape[1] // len(lags))
    test_X = test_X.reshape(test_X.shape[0], len(lags), test_X.shape[1] // len(lags))

    train_X = torch.tensor(train_X, dtype=torch.float32)
    train_y = torch.tensor(train_y, dtype=torch.float32).reshape(-1, 1)

    val_X = torch.tensor(val_X, dtype=torch.float32)
    val_y = torch.tensor(val_y, dtype=torch.float32).reshape(-1, 1)

    test_X = torch.tensor(test_X, dtype=torch.float32)
    test_y = torch.tensor(test_y, dtype=torch.float32).reshape(-1, 1)

    return train_X, val_X, test_X, train_y, val_y, test_y, scaler_x, scaler_y

class LSTMRegressor(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.lstm1 = nn.LSTM(input_dim, 32, batch_first=True)
        self.dropout1 = nn.Dropout(0.2)
        self.lstm2 = nn.LSTM(32, 16, batch_first=True)
        self.dropout2 = nn.Dropout(0.2)
        self.fc = nn.Linear(16, 1)

    def forward(self, x):
        x, _ = self.lstm1(x)  # (batch, 30, 32)
        x = self.dropout1(x)
        x, _ = self.lstm2(x)  # (batch, 30, 16)
        x = x[:, -1, :]  # last timestep (batch, 16)
        x = self.dropout2(x)
        return self.fc(x)  # (batch, 1)

def train_one_epoch(model, train_loader, criterion, optimizer):
    model.train()

    training_loss = 0.0

    for xb, yb in train_loader:
        logits = model(xb)
        loss = criterion(logits, yb)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        training_loss += loss.item()

    return training_loss / len(train_loader)


def evaluate(model, val_loader, criterion):
    model.eval()

    val_loss = 0.0
    predictions = []
    targets = []

    with torch.no_grad():
        for xb, yb in val_loader:
            logits = model(xb)
            loss = criterion(logits, yb)

            predictions.append(logits)
            targets.append(yb)

            val_loss += loss.item()

    val_loss /= len(val_loader)
    predictions = torch.cat(predictions)
    targets = torch.cat(targets)

    return val_loss, targets, predictions


def train_and_evaluate(model, train_loader, val_loader, criterion, optimizer, num_epochs):
    train_losses, val_losses = [], []

    for epoch in range(1, num_epochs + 1):
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer)
        val_loss, true_y, pred_y = evaluate(model, val_loader, criterion)

        train_losses.append(train_loss)
        val_losses.append(val_loss)

        if epoch % 2 == 0:
            print(f"Epoch {epoch:3d}/{num_epochs} | train_loss={train_loss:.4f} val_loss={val_loss:.4f}")

    return train_losses, val_losses

def predict_future_prices(model, last_closes, scaler_x, scaler_y, n_steps):
    model.eval()

    # keep closing prices in original scale
    window = np.asarray(last_closes, dtype=float).copy()

    future = []
    for _ in range(n_steps):
        # standardize all lag features before each prediction
        scaled_window = scaler_x.transform(window.reshape(1, -1))

        # (batch, timesteps, features) -> (1, 30, 1)
        next_day = torch.tensor(scaled_window, dtype=torch.float32).reshape(1, LOOKBACK, 1)

        with torch.no_grad():
            prediction_scaled = model(next_day).item()

        prediction = scaler_y.inverse_transform(
            np.array([[prediction_scaled]])
        )[0, 0]

        future.append(float(prediction))

        # drop the oldest value and append new prediction
        window = window[1:]
        window = np.append(window, prediction)

    return np.array(future)

def main(symbol="bitcoin", n_epochs=20):
    global train_X, val_X, test_X, train_y, val_y, test_y
    global train_loader, val_loader, test_loader

    df = load_ohlcv(symbol)
    df = prepare_features(df)
    df = create_lags(df)

    (train_X, val_X, test_X,
     train_y, val_y, test_y, scaler_x, scaler_y) = split_data(df)

    train_dataset = TensorDataset(train_X, train_y)
    val_dataset = TensorDataset(val_X, val_y)
    test_dataset = TensorDataset(test_X, test_y)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=False)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    # train_X.shape[1] // len(lags)
    input_dim = train_X.shape[2]

    model = LSTMRegressor(input_dim)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    train_and_evaluate(
        model,
        train_loader,
        val_loader,
        criterion,
        optimizer,
        num_epochs=n_epochs,
    )

    return model

if __name__ == "__main__":
    model = main()



