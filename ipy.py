from ipyleaflet import Map, Marker

import folium
from folium.plugins import Draw

center = (52.204793, 360.121558)

# m = Map(center=center, zoom=15)

# marker = Marker(location=center, draggable=True)
# m.add(marker)

# # display(m)

# # Now that the marker is on the Map, you can drag it with your mouse,
# # it will automatically update the `marker.location` attribute in Python

# # You can also update the marker location from Python, that will update the
# # marker location on the Map:
# marker.location = (50, 356)

# m = folium.Map()
# Draw(
#     export=True,
#     filename="my_data.geojson",
#     position="topleft",
#     draw_options={"polyline": {"allowIntersection": False}},
#     edit_options={"poly": {"allowIntersection": False}},
# ).add_to(m)


# m.show_in_browser()


""" flask_example.py

    Required packages:
    - flask
    - folium

    Usage:

    Start the flask server by running:

        $ python flask_example.py

    And then head to http://127.0.0.1:5000/ in your browser to see the map displayed

"""

from flask import Flask, render_template_string

import folium

app = Flask(__name__)

m = folium.Map(
        width=800,
        height=600,
    )
print(m.get_root().to_json())



@app.route("/")
def fullscreen():
    """Simple example of a fullscreen map."""
    m = folium.Map()
    return m.get_root().render()


@app.route("/iframe")
def iframe():
    """Embed a map as an iframe on a page."""
    m = folium.Map()
    Draw(
        export=True,
        filename="my_data.geojson",
        position="topleft",
        draw_options={"polyline": {"allowIntersection": False}},
        edit_options={"poly": {"allowIntersection": False}},

    ).add_to(m)

    # set the iframe width and height
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head></head>
                <body>
                    <h1>Using an iframe</h1>
                    {{ iframe|safe }}
                </body>
            </html>
        """,
        iframe=iframe,
    )


@app.route("/components")
def components():
    """Extract map components and put those on a page."""
    m = folium.Map(
        width=800,
        height=600,
    )

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
                    <h1>Using components</h1>
                    {{ body_html|safe }}
                    <script>
                        {{ script|safe }}
                    </script>
                </body>
            </html>
        """,
        header=header,
        body_html=body_html,
        script=script,
    )


if __name__ == "__main__":

    import webbrowser

    # webbrowser.open("http://127.0.0.1:5000/iframe", new=0)
    app.run(debug=True)
