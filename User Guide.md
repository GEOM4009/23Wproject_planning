User Guide:

1.	Loading the program

•	Once the program has begun the user will first be prompted to enter the Coordinate Reference System (CRS) that they will be using for their analysis. Throughout the code this will be used as the target crs to ensure any data that is loaded or created is within the same projections.

2.	Main Menu

•	The user will then go to the main menu, here they can chose which of the steps they would like to proceed with first, including creating the planning unit grid, loading conservation features, filters conservation features, visualizing the current data on a map, intersecting the features, and finally saving the various outputs that had been created.

3. Select grid generation method

•	When a user selects input grid generation method they will then have to choose one of the three grid generation methods that are available. 

4. Create grid from shape file extents

•	The user can create a grid that is defined by a shapefile of their choice. The entered shapefile will have its bounds used to define the bounds of the grid after it has been reprojected to the target crs. The user will also be prompted to enter the area of each individual hexagonal cell. A unique planning unit id is assigned to each hexagon that is created so they can be identified during the intersection.

5. Create grid from shape file extents and clip to shape

•	After the grid is created it can then be clipped to the exact dimensions of the shapefile rather than its bounds, this speeds up the processing time as it eliminates cells that will not intersect with any conservation features during the overlay process. 


6. Load existing grid from file

•	A grid can also be loaded from a file, this could be done to ensure consistency with past research that has been done, as well as speeding up the loading time of the code if the grid has a fine resolution and a large extent. 

7. Create grid from user input

•	Lastly a grid can be created entirely with manual inputs, with the user entering the central x and y coordinate, the length and width of the grid, and the area of the hexagon cells. The coordinate and x/y coordinates will be entered in the same units as the coordinate reference system, with the area being in those units squared.

8.	Loading the conservation features

•	Once the grid is generated the user will be taken back to the main menu where they can choose to load their conservation features. These features are input using a path provided by the user or by utilizing a pop up window that will allow them to select the file directly. The file is then projected to the target crs and the user then returns back to the main menu. 

9.	Filtering features 

•	If the conservation features that are loaded contain features the user is not interested in examining they are then able to filter it based on the various attributes of the file. This could be fields such as group, id, name, class or another attribute if other files are used.

10.	Plotting 

•	If the user selects Layer to Plot from the main menu these layers can then be plotted to allow the user to visualize them. 

11.	Creating the CSV

•	The layers will now be ready for the most important step in the process which is the intersection between the two planning unit grid and conservation features. The user can select Calculate Area Overlap, the two layers will be overlaid and intersected with one another. This creates a csv that contains three columns, a species column for the unique ID associated with the conservation features, a pu column that has the ID for each individual hexagon in the planning unit that intersects with a conservation feature, and the area of overlap between the two features.

12.	Saving the Results

•	Finally in the main menu the user can select Save Results, this will allow them to save the planning unit grid and filtered conservation features so they can save time on potential future work. They will also save the final csv that will be used input into marxan.
