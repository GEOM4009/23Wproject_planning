from flask import Flask, request, render_template_string
import folium
from folium.plugins import Draw
import geojson
from geojson import Point, Polygon
import json
import queue
import webbrowser
from defs import *
import geopandas as gpd


app = Flask(__name__)
job_queue = queue.Queue()

m = folium.Map(
        width=800,
        height=600,
    )
user_title = "Please Make A Selection"


def get_input_from_map(layers: list[gpd.GeoDataFrame] = [], title: str = user_title) -> any:

    global user_title
    user_title = title

    map = folium.Map(
        width=800,
        height=600,
        location=(69.25,-88),
        zoom_start=5,
        tiles="Stamen Terrain"
    )

    for layer in layers:
        folium.GeoJson(data=layer["geometry"]).add_to(map)

    Draw(
            # export=True,
            filename="my_data.geojson",
            position="topleft",
            draw_options={"polyline": {"allowIntersection": False}},
            edit_options={"poly": {"allowIntersection": False}},
        ).add_to(map)

    global m
    m = map

    webbrowser.open_new(URL_INPUT)
    job_data = job_queue.get()
    job_queue.task_done()
    return job_data


@app.route('/', methods=["GET"])
def start():
    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <body onload="init()">
                    <h1>You can close this tab at any time</h1>
                </body>
            </html>
        """
    )


@app.route('/input', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        coords = request.get_json()
        load = geojson.loads(json.dumps(coords))
        shape = Polygon(load['features'][0]['geometry']['coordinates']) if len(load['features']) else None
        job_queue.put(shape)
        return "", 200

    # Render the map template
    elif request.method == 'GET':
        m.get_root().render()
        header = m.get_root().header.render()
        body_html = m.get_root().html.render()
        script = m.get_root().script.render()

        return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                    {{ header|safe }}
                </head>
                <body>
                    <h1>{{ title | safe}}</h1>
                    {{ body_html|safe }}
                        <button id="Submit">Submit</button>
                    <script>
                        {{ script|safe }}
                         document.getElementById("Submit").addEventListener('click', async (e) => {
                           var data = drawnItems.toGeoJSON();
                           var convertedData = 'text/json;charset=utf-8,'
                             + encodeURIComponent(JSON.stringify(data));

                            const xhttp = new XMLHttpRequest()
                            xhttp.open('POST', '/input', false);
                            xhttp.setRequestHeader('Content-Type', 'application/json');
                            xhttp.send(JSON.stringify(data));
                            window.location.replace("http://127.0.0.1:5000/");
                            close();
                        });

                    </script>
                </body>
            </html>
        """,
        header=header,
        body_html=body_html,
        script=script,
        title = user_title

    )


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug=True)
