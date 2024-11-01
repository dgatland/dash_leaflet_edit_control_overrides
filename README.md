# Overriding the Edit Control Functionality in Dash Leaflet
This is a demo Dash Leaflet app (built in Python 3.12) that shows how to programmatically implement the 
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

Here is a screenshot of the demo app:
![screenshot](assets/screenshot.png?raw=True)