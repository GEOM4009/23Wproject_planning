Troubshooting and Frequently Asked Questions (FAQ)

Why is the processing time so long?
  - There are many factors that can contribute to long processing times with this code
  - Creating a grid with a resolution that is very small or covers a large extent can result in long load times
  - Intersecting these large grids with the conservation features can also be a time intesive process and may take more than an hour
  - Using a multiple overlapping conservation features could also result in longer processing time during overlaps
  - As long as you can see the scrolling dots indicating something is happening the process is still working and may just need to wait

I entered the incorrect file or variable input during one of the steps, how do I fix this?
  - The step can be repeated by returning to the main menu and doing the same process again
  - Some steps can be aborted with ‘crtl+c’ (this will be indicated in the console) if you do not want to wait for the operation to complete. For example if an incorrect unit was entered and resulted in a very small hexagon size that will take a long time to generate.
  - Note: that it may be a better option to start the script over depending on the situation, for example, a new target CRS cannot be entered after the beginning

What units are the variable inputs for the manual grid generation?
  - The units of any input directly related to a CRS will be in the units of the CRS. However some inputs can be given in different units if the correct suffix is entered as indicated during the input prompt. The default is meters, and all calculations that occur will be performed in meters.

Can this tool be applied to regions outside of Nunavut?
  - Any coordiante reference system that can be input into the code can have its area studied
  - Polygon shapefiles that don't have the same fields as the Nunavut conservation features can also be used as the code allows for the selection of any attribute within the features, simply use the “Choose Attribute” options to avoid errors
  - However, it is important to note that if the naming of columns is not consistent across loaded Conservation Feature files then filtering them will be ineffective as all files will be filtered by the single attribute.
  - The script relies on the Conservation feature files having the correct column name for the “id” so that it can access it as expected. The input data should either be updated to be correct or the “ID” column name could be updated in the defs.py file

What coordinate reference systems can be used with this application?
  - Any CRS used for this function must be a projected coordinate system and not a geographic projection systems
  - Any coordinate system with an EPSG code can be entered if it is not the default option provided (Albers Equal Area)
  - If the CRS does not have an EPSG code it can be loaded from a file that has the desired CRS

Can I use a pre-existing Planning Unit Grid?
 - Yes, simply select the option "Load existing Grid from File" to load a grid from file
 - However, If you use a prexisting grid it must contain a column "GRID_ID" with a unique value for each cell, the column name can be updated in the def.py file if desired.
 - Note: Loading a pre-existing planning unit grid will (if it is projected) override the target CRS to avoid distortion, this CRS will then be used for all files

