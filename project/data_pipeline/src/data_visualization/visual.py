import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import folium
from folium.plugins import MarkerCluster
import webbrowser

def visualize(car_df):
    print("Printing the basic plots \n")

    sns.pairplot(car_df)
    plt.show()

    sns.boxplot(car_df)
    plt.show()

    sns.countplot(car_df)
    plt.show()

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
