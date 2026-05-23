🚧 Urban Safety Insights (In Progress)

Welcome to the Urban Safety Insights project!
This project is currently under development, so some components may still be incomplete or in progress.
🎯 Project Goal

The goal of this project is to build an interactive data visualization platform that identifies areas with high concentrations of vehicle accidents — such as intersections, highways, regions affected by severe weather, or incidents involving impaired driving (DUI).

By analyzing and visualizing these patterns, the project aims to:

    Raise public awareness about dangerous driving conditions

    Inform state and local officials on where infrastructure improvements may be needed

    Support proactive safety measures to reduce accident frequency and severity

Ultimately, the project seeks to enhance public safety, reduce vehicle repair costs, and improve quality of life by contributing to safer, more informed urban planning. After all, ensuring people return safely to their loved ones is what matters most.


## **Technology**
In this project i used **Python, Pandas, Matplotlib, Seaborn, Scikit-Learn, and Folium**. I used these as my tech stack with the experience and versitility the project is needed.

## **Methodology**

When researching into this project the main issue i had to attack was cleaning and preparing the data for visualization. The dataset im working with is from the State of Maryland the link is provided in the **resources** section.
The dataset contains 38 columns/features:
```
Report Number
Local Case Number
Agency Name
ACRS Report Type
Crash Date/Time
Route Type
Road Name
Cross-Street Name
Off-Road Description
Municipality
Related Non-Motorist
Collision Type
Weather
Surface Condition
Light
Traffic Control
Driver Substance Abuse
Non-Motorist Substance Abuse
Person ID
Driver At Fault
Injury Severity
Circumstance
Driver Distracted By
Drivers License State
Vehicle ID
Vehicle Damage Extent
Vehicle First Impact Location
Vehicle Body Type
Vehicle Movement
Vehicle Going Dir
Speed Limit
Driverless Vehicle
Parked Vehicle
Vehicle Year
Vehicle Make
Vehicle Model
Latitude
Longitude
Location
```

When beginning the data cleaning process, I first removed irrelevant features such as vehicle ID, report number, vehicle information, police logistics, and other metadata. These features were excluded because they did not contribute meaningful insights for our analysis or modeling objectives.

Next, I assessed missing values across the dataset. Since the volume of missing data was negligible relative to the overall dataset size, I opted to remove those rows entirely rather than impute them.

While exploring the data, I discovered inconsistencies in categorical values — for example:

    "Snow", "SNOW"

    "Ice", "ICE", "ICE/FROST"

To address this, I standardized all categorical values by mapping them using a custom dictionary created from .unique() outputs for each relevant column. This ensured consistency in the dataset, which is crucial for clustering and analysis.

Once the data was cleaned, I shifted focus to visualizing distributions and identifying patterns using histograms, bar charts, and box plots. These helped me better understand the spread of variables and potential feature groupings.
🔍 Unsupervised Learning & Clustering

Based on the nature of the dataset and lack of labels, I determined that this would be best approached as an unsupervised learning problem. I experimented with both KMeans and DBSCAN clustering algorithms.

    KMeans was initially tested, but it struggled with outliers and spatial irregularities, especially at the street level. Inconsistent cluster results and the need to manually determine the optimal number of clusters (K) made it inefficient for this use case.

    DBSCAN, on the other hand, proved to be more effective. As a density-based clustering algorithm, it dynamically adapts to changes in zoom level or geographic scale — an ideal characteristic for mapping accident hotspots. It also handled noise and outliers better without requiring a predefined number of clusters.

By leveraging latitude and longitude coordinates in the dataset, I was able to plot precise accident locations on a map, enhancing both interpretability and visual impact of the results.

Using Folium to Create the Interactive Map

Folium, a Python wrapper for Leaflet.js, was utilized to plot DBSCAN clustering results on an interactive map. Each data point was geolocated using latitude and longitude, with cluster membership and outliers color-coded. This integration allowed for dynamic visual inspection of density-based clusters, which helped highlight high-risk zones for vehicle accidents based on spatial patterns.

Resources
Dataset: https://catalog.data.gov/dataset/crash-reporting-drivers-data
