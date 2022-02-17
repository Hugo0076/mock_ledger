import socket
import sys
from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dash_table
from dash.dependencies import Input, Output, State

from data_types import Order


class Server:
    def __init__(self) -> None:
        self.order_book = []

    def handle_order(self, order):
        self.order_book.append(order)
        print(self.order_book)
        return 0

    def main(self, type=0):
        ClientSocket = socket.socket()
        host = socket.gethostname()
        port = 10016
        print("Waiting for connection")

        try:
            ClientSocket.connect((host, port))
            print("Connected")
        except socket.error as e:
            print(str(e))

        es = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
        app = Dash(__name__, external_stylesheets=es)

        bid_quote_input = [
            html.Div(dcc.Input(id="input-on-submit-bid", type="text")),
            html.Button("Submit Bid", id="bid-quote-val"),
            html.Div(
                id="container-button-basic-bid", children="Enter a bid and press submit"
            ),
        ]
        ask_quote_input = [
            html.Div(dcc.Input(id="input-on-submit-ask", type="text")),
            html.Button("Submit Ask", id="ask-quote-val"),
            html.Div(
                id="container-button-basic-ask",
                children="Enter an offer and press submit",
            ),
        ]

        data_dict = OrderedDict(
            [
                ("Bids Qty", [0, 0, 0, 0, 1, 2, 4, 2]),
                ("Price", [i for i in range(200, 280, 10)]),
                ("Asks Qty", [1, 2, 4, 2, 0, 0, 0, 0]),
            ]
        )

        data = pd.DataFrame(data_dict)

        # x0 = np.random.randn(500)
        ## Add 1 to shift the mean of the Gaussian distribution
        # x1 = np.random.randn(500) + 1
        #
        # fig = go.Figure()
        # fig.add_trace(go.Histogram(x=x0))
        # fig.add_trace(go.Histogram(x=x1))
        #
        ## Overlay both histograms
        # fig.update_layout(barmode='overlay')
        ## Reduce opacity to see both histograms
        # fig.update_traces(opacity=0.75)
        # fig.show()

        app.layout = html.Div(
            children=[
                html.Div(
                    [
                        dcc.Interval(id="interval1", interval=500, n_intervals=0),
                        html.H1(id="label1", children=""),
                    ]
                ),
                html.H1(children="Mock Ledger"),
                html.Div(
                    children="""
                Dash: A web application framework for your data.
            """
                ),
                dcc.Graph(id="graph"),
                html.Div(
                    [
                        dash_table.DataTable(
                            id="table",
                            style_data={
                                "width": "10px",
                                "maxWidth": "10px",
                                "minWidth": "10px",
                            },
                            columns=[{"name": i, "id": i} for i in data.columns],
                            data=data.to_dict("records"),
                            style_cell=dict(textAlign="left"),
                            style_header=dict(backgroundColor="paleturquoise"),
                        )
                    ],
                    style={"width": "50%", "align": "center", "flex": 1},
                ),
                html.Div(bid_quote_input + ask_quote_input),
            ]
        )

        @app.callback(Output("graph", "figure"), Input("bid-quote-val", "n_clicks"))
        def display_color(mean=0):
            data_bid = np.random.normal(200, 15, size=500)
            data_ask = np.random.normal(100, 15, size=500)
            fig = go.Figure()
            bins = dict(start=0, end=475, size=15)
            fig.add_trace(go.Histogram(x=data_bid, xbins=bins, autobinx=False))
            fig.add_trace(go.Histogram(x=data_ask, xbins=bins, autobinx=False))

            # Overlay both histograms
            fig.update_layout(barmode="overlay")
            return fig

        @app.callback(
            Output("container-button-basic-bid", "children"),
            Input("bid-quote-val", "n_clicks"),
            State("input-on-submit-bid", "value"),
        )
        def update_output_bid(n_clicks, value):
            if not value == None:
                print(f"Sending buy request at ${value}")
                ClientSocket.send(str.encode(str(value)))
                Response = ClientSocket.recv(1024)
                print(f"Response: {Response.decode('utf-8')}")
            return 'Input "{}"'.format(value)

        @app.callback(
            Output("container-button-basic-ask", "children"),
            Input("ask-quote-val", "n_clicks"),
            State("input-on-submit-ask", "value"),
        )
        def update_output_ask(n_clicks, value):
            if not value == None:
                print(f"Sending ask request at ${value}")
                ClientSocket.send(str.encode(str(value)))
                Response = ClientSocket.recv(1024)
                print(f"Response: {Response.decode('utf-8')}")
            return 'Input "{}"'.format(value)

        @app.callback(Output("label1", "children"), [Input("interval1", "n_intervals")])
        def update_interval(n):
            print(f"query:{n}")

            response = ClientSocket.recv(1024)
            if response:
                print(f"Response: {response.decode('utf-8')}")
                self.handle_order(response.decode("utf-8"))
            return ""

        app.run_server(debug=True)


if __name__ == "__main__":
    serv = Server()
    serv.main()
    # main(int(sys.argv[1]))
