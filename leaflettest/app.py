# from flask import Flask, render_template, request

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/get_location", methods=["POST"])
# def get_location():
#     lat = request.form.get("latitude")
#     lng = request.form.get("longitude")
#     print("Received location:", lat, lng)
#     return "Location received"

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, request, jsonify, render_template_string
import folium
from folium.plugins import Draw
import geojson
from geojson import Feature, FeatureCollection, Point, Polygon
import json

app = Flask(__name__)


m = folium.Map(
        width=800,
        height=600,
    )
Draw(
        # export=True,
        filename="my_data.geojson",
        position="topleft",
        draw_options={"polyline": {"allowIntersection": False}},
        edit_options={"poly": {"allowIntersection": False}},
    ).add_to(m)

@app.route('/', methods=["GET"])
def start():
    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <body onload="init()">
                    <script>
                            function init(){
                                window.open("http://127.0.0.1:5000/open");
                            }
                    </script>
                </body>
            </html>
        """
    )



@app.route('/open', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        coords = request.get_json()
        print("got some stuff...")
        load = geojson.loads(json.dumps(coords))
        # print(load)
        print("\n\n\n\n")
        shape = Polygon(load['features'][0]['geometry']['coordinates'])
        print(shape)

        # print(load['features'][0]['geometry']['type'])
        # Do something with the coordinates, e.g. save to a database
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
                    <h1>Using components</h1>
                    {{ body_html|safe }}
                        <button id="Submit">Submit</button>
                    <script>
                        {{ script|safe }}
                         document.getElementById("Submit").addEventListener('click', async (e) => {
                           var data = drawnItems.toGeoJSON();
                           var convertedData = 'text/json;charset=utf-8,'
                             + encodeURIComponent(JSON.stringify(data));

                            const xhttp = new XMLHttpRequest()
                            xhttp.open('POST', '/open', false);
                            xhttp.setRequestHeader('Content-Type', 'application/json');
                            xhttp.send(JSON.stringify(data));
                            window.close( "_self");
                        });

                    </script>
                </body>
            </html>
        """,
        header=header,
        body_html=body_html,
        script=script,
    )

if __name__ == '__main__':
    # app.run(debug=True)
     app.run(host='0.0.0.0', port=8080)

    '''
    Couple options for integrating with the planning project:

    -> run flask app as seperate thread and use thread safe queue to pass data between threads
    --> after a user selects and option that get user input from the map we call a while loop that checks the queue for data
    --> assumming this doesn't fail we should always return something, even it its nothing
    --> then take this data and process it

    --> use Flask-SocketIO to send data to the planning project

    --> have the planning proj live inside the web app and make the UI a webpage,
    --> then just generate a new page with the map for input when required

    '''

# import subprocess
# import time
# from selenium import webdriver

# # define the command to start the Flask app
# cmd = "python app.py"

# # start the Flask app as a separate process
# p = subprocess.Popen(cmd, shell=True)

# # wait for the Flask app to start up
# time.sleep(2)

# # set up the webdriver for Chrome
# driver = webdriver.Chrome()

# # navigate to the local Flask app
# driver.get("http://127.0.0.1:5000/")

# # wait for some actions to be completed
# time.sleep(5) # wait for 5 seconds

# # perform some actions on the page
# title = driver.title
# print(f"The title of the page is '{title}'")

# # wait for some more actions to be completed
# time.sleep(5) # wait for 5 seconds

# # close the window
# driver.quit()

# # stop the Flask app process
# p.terminate()