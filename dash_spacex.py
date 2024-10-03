# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import seaborn as sns

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

deep_colors = sns.color_palette("deep").as_hex()

site_options = [{"label": "All Sites", "value": "All Sites"}] + [
    {"label": site, "value": site} for site in spacex_df["Launch Site"].unique()
]

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        dcc.Dropdown(
            id="site-dropdown",
            options=site_options,
            placeholder="Select a Launch Site",
            value="All Sites",
            searchable=True,
        ),
        html.Br(),
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        # Payload range slider
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={i: f"{i}" for i in range(0, 10001, 1000)},
            value=[min_payload, max_payload],
        ),
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(launch_site):
    if launch_site == "All Sites":
        success_data = spacex_df.groupby("Launch Site")["class"].mean()
        fig = px.pie(
            values=success_data,
            names=success_data.index,
            title="Total Success Launches by Site",
            color_discrete_sequence=deep_colors,
        )
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == launch_site]
        success_rate = filtered_df["class"].value_counts(normalize=True)
        fig = px.pie(
            values=success_rate,
            names=success_rate.index.map({1: "Success", 0: "Failure"}),
            title=f"Success vs Failure for {launch_site}",
            color_discrete_sequence=deep_colors[:2],
        )
    return fig


@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_payload_chart(launch_site, payload_mass):
    filtered_df = spacex_df[
        spacex_df["Payload Mass (kg)"].between(payload_mass[0], payload_mass[1])
    ]

    if launch_site != "All Sites":
        filtered_df = filtered_df[filtered_df["Launch Site"] == launch_site]

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site"],
        title=f"Correlation Between Payload and Success for {'All Sites' if launch_site == 'All Sites' else launch_site}",
        color_discrete_sequence=deep_colors,
    )

    return fig


if __name__ == "__main__":
    app.run_server()
