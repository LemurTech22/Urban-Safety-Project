
"""
Goal is to cluster all values based on location and find hotspots where accidents occur.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import folium
from folium.plugins import MarkerCluster
import webbrowser

def print_basic_info(car_df):
    print("First 5 rows in the dataset: \n", car_df.head())

    print("Last 5 rows in the dataset: \n", car_df.tail())

    print("Summary of the dataset: \n", car_df.describe())

def clean_basic_data(car_df):
    print(car_df.info())
    car_df.drop_duplicates(inplace=True)
    car_df.drop(['Report Number', 'Local Case Number', 'Agency Name', 'Vehicle ID','Person ID', 'Drivers License State',
                 'Circumstance', 'Off-Road Description' ,'Municipality', 'Location', 'Related Non-Motorist', 'Driverless Vehicle','Non-Motorist Substance Abuse',],axis =1 , inplace =True)

    print("Dataset after removing unecessary features: ", car_df.info())

    print("Five number summary of the Car Accident dataset",car_df.describe())

def visualize(car_df):
    print("Printing the basic plots \n")

    sns.pairplot(car_df)
    plt.show()

    sns.boxplot(car_df)
    plt.show()

    sns.countplot(car_df)
    plt.show()

def missing_data(car_df):
    print("Printing the number of missing data: \n")
    print(car_df.isnull().sum())

    car_df.dropna(subset=['Route Type','Road Name', 'Cross-Street Name','Driver At Fault','Weather'], inplace=True)

    print("After dropping rows:\n",car_df.isnull().sum())

def find_unique_data(car_df):
    print("Finding all the unique values in each columns \n")

    for col in car_df.columns:
        print(f"Column: {col}" )
        print(car_df[col].unique(),'\n')
#test
def map_values(car_df):
    weather_mapping = {'CLEAR': 'Clear',
                       'CLOUDY': 'Cloudy',
                       'RAINING':'Rain',
                       'SNOW':'Snow','BLOWING SNOW': 'Snow', 'Blowing Snow': 'Snow',
                       'SEVERE WINDS': 'Severe Winds', 'Severe Crosswinds': 'Severe Winds',
                       'FOGGY': 'Fog', 'SLEET': 'Sleet','Sleet Or Hail': 'Sleet'
                       }
    car_df = car_df[~car_df['Weather'].astype(str).str.lower().isin(['unknown', 'nan'])]

    surface_conditions = {'DRY': 'Dry',
                     'ICE': 'Ice','Ice/Frost': 'Ice',
                     'WET': 'Wet',
                     'SLUSH': 'Slush',
                     'WATER(STANDING/MOVING)': 'Water','Water (standing, moving': 'Water',
                     'SNOW': 'Snow',
                     'MUD': 'Mud','DIRT': 'Dirt', 'GRAVEL': 'Gravel'
                     }
    car_df= car_df[~car_df['Surface Condition'].astype(str).str.lower().isin(['unknown', 'nan'])]

    substance_mapping = {'NONE DETECTED': 0,'Not Suspect of Alcohol Use, Not Suspect of Drug Use': 0,
                         'OTHER': 1, 'ALCOHOL CONTRIBUTED': 1, 'ALCOHOL PRESENT': 1, 'COMBINED SUBSTANCE PRESENT': 1, 'ILLEGAL DRUG CONTRIBUTED': 1,
                         'MEDICATION CONTRIBUTED': 1, 'ILLEGAL DRUG PRESENT':1, 'MEDICATION PRESENT':1,'COMBINATION CONTRIBUTED':1,
                         'Suspect of Alcohol Use, Not Suspect of Drug Use': 1, 'Suspect of Alcohol Use, Unknown': 1, 'Suspect of Alcohol Use, Suspect of Drug Use':1,'Not Suspect of Alcohol Use, Suspect of Drug Use':1
    }

    car_df= car_df[~car_df['Driver Substance Abuse'].astype(str).str.lower().isin(['unknown', 'nan'])]

    car_df['Weather'] = car_df['Weather'].map(weather_mapping)
    car_df['Surface Condition'] = car_df['Surface Condition'].map(surface_conditions)
    car_df['Driver Substance Abuse'] = car_df['Driver Substance Abuse'].map(substance_mapping)

    car_df.dropna(subset=['Weather'], inplace=True)
    print("Mapping and Cleaning up the data: \n")
    for col in car_df.columns:
        print(f"Column: {col}" )
        print(car_df[col].unique(),'\n')


    print(car_df.info())

    print("Prints the 5 number summary of the Car Accident dataset\n")
    print(car_df.describe())
def correlation_analysis(car_df):
    # Selecting only numeric features
    numeric_df = car_df.select_dtypes(include=['number'])

    # Compute correlation matrix
    correlation_matrix = numeric_df.corr()

    # Print correlation values
    print("Correlation Matrix:\n", correlation_matrix)

    # **📊 Heatmap for Visualization**
    plt.figure(figsize=(20, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title("Feature Correlation Heatmap")
    plt.show()

def cluster_analysis(car_df):
    cluster_data = car_df[['Latitude', 'Longitude','Speed Limit']].dropna()

    scaler = StandardScaler()
    scaled_clustered_data = scaler.fit_transform(cluster_data)

    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    cluster_data['KMeans_Cluster'] = kmeans.fit_predict(scaled_clustered_data)

    dbscan = DBSCAN(eps = .2, min_samples=100)

    cluster_data['DBSCAN_Cluster'] = dbscan.fit_predict(scaled_clustered_data)

    return cluster_data
def visualize_map(cluster_data):
    # Find the center of the map (mean of all lat/lon)
    center_lat = cluster_data['Latitude'].mean()
    center_lon = cluster_data['Longitude'].mean()

    # Create a Folium map centered on the accident locations
    accident_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Create a Marker Cluster (group nearby points)
    marker_cluster = MarkerCluster().add_to(accident_map)

    # Add accident locations as markers
    for idx, row in cluster_data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"Cluster: {row['KMeans_Cluster']}",
            icon=folium.Icon(color="red" if row['KMeans_Cluster'] == 0 else "blue")
        ).add_to(marker_cluster)

    # Save and display the map
    accident_map.save("accident_clusters_map.html")

    return accident_map

def visualize_w_map(cluster_df):
    sns.pairplot(cluster_df)
    plt.show()

    sns.boxplot(cluster_df)
    plt.show()

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    sns.scatterplot(x=cluster_df['Longitude'], y=cluster_df['Latitude'], hue=cluster_df['KMeans_Cluster'], ax=axes[0])
    axes[0].set_title('KMeans Cluster')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')

    sns.scatterplot(x=cluster_df['Longitude'], y=cluster_df['Latitude'], hue=cluster_df['DBSCAN_Cluster'], ax=axes[1])
    axes[1].set_title('DBSCAN Cluster')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    plt.show()

def main():
    car_df = pd.read_csv('Cars_Reporting_Data.csv', low_memory=False)
    #print_basic_info(car_df)
    #visualize(car_df)
    clean_basic_data(car_df)
    missing_data(car_df)
    #find_unique_data(car_df)
    map_values(car_df)
    correlation_analysis(car_df)
    cluster_data = cluster_analysis(car_df)
    visualize_w_map(cluster_data)
    access_map=visualize_map(cluster_data)
    map_path = "accident_cluster_map.html"
    access_map.save(map_path)
    webbrowser.open_new_tab(map_path)

if __name__ == '__main__':
    main()
