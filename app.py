import os
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import random
import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Historical data for temperature monitoring
historical_data = {
    "Temperature (\u00b0C)": [],
    "temp_lag1": [],
    "temp_lag2": [],
    "temp_lag3": [],
    "temp_roll_mean": [],
    "temp_roll_std": []
}
time_stamps = []

# Generate simulated temperature data
recent_temps = [random.uniform(24, 26) for _ in range(3)]

def generate_temperature_data():
    new_temp = round(random.uniform(24, 32), 2)
    recent_temps.append(new_temp)
    if len(recent_temps) > 3:
        recent_temps.pop(0)

    temp_lag1 = recent_temps[-2]
    temp_lag2 = recent_temps[-3] if len(recent_temps) > 2 else recent_temps[-2]
    temp_lag3 = recent_temps[-3] if len(recent_temps) > 2 else recent_temps[-2]

    temp_roll_mean = round(sum(recent_temps) / len(recent_temps), 2)
    temp_roll_std = round((sum((x - temp_roll_mean)**2 for x in recent_temps) / len(recent_temps))**0.5, 2)

    return {
        "Temperature (°C)": new_temp,
        "temp_lag1": temp_lag1,
        "temp_lag2": temp_lag2,
        "temp_lag3": temp_lag3,
        "temp_roll_mean": temp_roll_mean,
        "temp_roll_std": temp_roll_std
    }

app.layout = dbc.Container([
    dbc.Row([dbc.Col(html.H1("Temperature Monitoring Dashboard"), width=12)], className="mt-4"),

    dbc.Row([dbc.Col(dcc.Graph(id="live-temp-chart"), width=12)], className="mt-4"),

    dbc.Row([dbc.Col(dcc.Graph(id="temp-time-series"), width=12)], className="mt-4"),

    dbc.Row([dbc.Col(html.Div(id="status-div", style={"fontSize": "20px", "marginTop": "20px"}), width=12)]),

    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id="temp-table",
            columns=[{"name": col, "id": col} for col in ["Time"] + list(historical_data.keys())],
            style_table={'overflowX': 'auto'}
        ), width=12)
    ], className="mt-4"),

    dcc.Interval(id="interval-component", interval=5000, n_intervals=0)
], fluid=True)

@app.callback(
    [Output("live-temp-chart", "figure"),
     Output("temp-time-series", "figure"),
     Output("status-div", "children"),
     Output("temp-table", "data")],
    Input("interval-component", "n_intervals")
)
def update_dashboard(n):
    data = generate_temperature_data()

    time_stamps.append(datetime.datetime.now().strftime("%H:%M:%S"))
    for key in data:
        historical_data[key].append(data[key])

    # Live bar chart
    bar_fig = go.Figure(data=[
        go.Bar(name=key, x=[key], y=[value]) for key, value in data.items()
    ])
    bar_fig.update_layout(barmode='group', title='Live Temperature Data')

    # Time series chart
    line_fig = go.Figure()
    for key in historical_data:
        line_fig.add_trace(go.Scatter(x=time_stamps, y=historical_data[key], mode='lines+markers', name=key))
    line_fig.update_layout(title="Temperature Data Over Time", xaxis_title="Time", yaxis_title="Value")

    # Check for anomaly
    anomaly_text = "Anomaly Detected: High Temperature!" if data["Temperature (°C)"] > 28 else "Temperature is Normal."

    # Table data
    table_data = [{"Time": time_stamps[i], **{key: historical_data[key][i] for key in historical_data}} for i in range(len(time_stamps))]

    return bar_fig, line_fig, html.Div(anomaly_text), table_data

if __name__ == "__main__":
    app.run_server(debug=True)
