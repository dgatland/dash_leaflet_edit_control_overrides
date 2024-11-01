from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash_extensions.javascript import assign
import dash_leaflet as dl


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dash Leaflet Example"

# Map to select region
leaflet_map = dl.Map(
    [
        dl.TileLayer(attribution="© <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>"),
        dl.FeatureGroup(
            [
                dl.EditControl(
                    draw={"polygon": False, "polyline": False, "rectangle": False, "circle": False, "circlemarker": False},
                    edit={"edit": False},
                    id="edit-control",
                ),
            ],
            id="feature-group-edit-control"
        ),
        dcc.Store(data="", id="clicked-marker-latlng"), # Store clicked marker coords for us during "delete mode"
    ],
    center=[-40.75, 173.03], 
    zoom=5, 
    style={"height": "60vh"},
    id="location-map",
)

# Javascript handler to activate delete mode (note, this will automatically get loaded into `assets/dashExtensions_default.js`)
delete_event_handler = assign(
    """
        function(e, ctx) {
            if (e.layer instanceof L.Marker) {
                // Store the latlng in the dcc Store element, so we can delete the marker from the geojson data
                dash_clientside.set_props("clicked-marker-latlng", {data: e.latlng});

                // Remove the clicked marker from the Leaflet map, which we can't do from Python
                e.layer.remove();
            }
        }
    """
)

### App layout
app.layout = dbc.Container(
    [
        html.H1("Overriding the Edit Control Functionality in Dash Leaflet", style={"textAlign": "center"}),
        
        # Map and control buttons
        leaflet_map,
        html.Div(
            [
                html.P("Use the following controls to add or remove custom markers.", style={"marginBottom": "0.5rem"}),
                
                dbc.Button("Add marker", style={"margin": "5px"}, id="map-add-marker"),
                dbc.Tooltip("After clicking me, click on the map to add a marker. You must click me in between each marker added.", target="map-add-marker"),
                
                dbc.Checklist(
                    options=["Delete mode"], 
                    value=[], 
                    switch=True, 
                    input_checked_style={"backgroundColor": "var(--bs-danger)","borderColor": "var(--bs-danger)"}, 
                    style={"display": "inline-block", "margin": "5px"},
                    id="map-delete-marker-mode",
                ),
                dbc.Tooltip("When activated, click markers on the map to delete them", target="map-delete-marker-mode"),
                
                dbc.Button("Clear all markers", color="danger", style={"margin": "5px", "float": "right"}, id="map-clear-markers"),
                dbc.Tooltip("Delete all custom markers that you have added", target="map-clear-markers"),                
            ],
        ),
        
        # Description  
        html.Hr(),      
        dcc.Markdown(
            """
            **Why did I build this?**\n
            
            This is a demo Dash Leaflet app that shows how to programmatically implement the 
            [EditControl](https://www.dash-leaflet.com/components/controls/edit_control) functionality. This is a 
            somewhat simplified example, but you could of course mix and match the controls I've implemented here and
            extend it to include draw modes other than just markers.
            
            The advantages I obtained from this implementation are:
            
            * The EditControl buttons may not be obvious to some users, and for an app whose primary purpose is not to
            be a map viewer/editor, I didn't want to 'train' the user in how to interact with the map. By creating
            standard buttons, there is a very obvious route for how to interact with the map.
            * The "Delete Mode" switch allows you to delete markers without having to also click "Save", as is required 
            in the native EditControl button (this was important for my project, where a user was dealing with a small 
            number of markers, and the added button click was intrusive to the workflow).
            * We also had an associated [`DivMarker`](https://www.dash-leaflet.com/components/ui_layers/div_marker#a-divmarker)
            for each marker, to display a number alongside the marker, and when using Dash Leaflet's EditControl to 
            delete markers, we couldn't delete the associated `DivMarker` until the user *saved* their deletion changes,
            which was confusing to the users.
            * For completeness, I included the "Clear all markers" button, although this only slightly simplifies that
            action compared to the native EditControl workflow (by reducing from two button clicks to one, although it's
            still nice to have a big standout button for this).
            """
        ),
    ]
)


### Callbacks

# Trigger "add marker" mode
@app.callback(
    Output("edit-control", "drawToolbar"), 
    Input("map-add-marker", "n_clicks"),
    prevent_initial_call=True,
)
def trigger_add_marker_mode(n_clicks):
    return dict(mode="marker", n_clicks=n_clicks) # include n_click to ensure prop changes

# Delete all markers
@app.callback(
    Output("edit-control", "editToolbar"), 
    Input("map-clear-markers", "n_clicks"),
)
def trigger_clear_all_action(n_clicks):
    return dict(mode="remove", action="clear all", n_clicks=n_clicks)  # include n_click to ensure prop changes

# Toggle delete mode, this effectively activates the JS in `delete_event_handler`, which updates the `"clicked-marker-latlng"` store when a user clicks on a marker
@app.callback(
    Output("feature-group-edit-control", "eventHandlers"),
    Input("map-delete-marker-mode", "value"),
    prevent_initial_call=True,
)
def toggle_delete_mode(delete_mode):
    if "Delete mode" in delete_mode:
        return {"click": delete_event_handler}
    else:
        return {}
    
# Delete marker when clicked
@app.callback(
    Output("edit-control", "geojson"),
    Input("clicked-marker-latlng", "data"),
    State("edit-control", "geojson"),
    prevent_initial_call=True
)
def handle_latlng_change(latlng, geojson):
    # Remove the selected marker
    for feature in geojson["features"]:
        if feature["geometry"]["coordinates"] == [latlng["lng"], latlng["lat"]]:
            geojson["features"].remove(feature)
    return geojson


### Main
if __name__ == "__main__":
    app.run(debug=True)
