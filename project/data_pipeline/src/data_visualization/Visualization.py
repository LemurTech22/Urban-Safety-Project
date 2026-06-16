import folium
import webbrowser
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans,DBSCAN
from sklearn.preprocessing import StandardScaler

from folium.plugins import MarkerCluster


class Visualization: 
    def __init__(self,df: pd.DataFrame):
        self.df = df
        self.cluster_data = None
    def __enter__(self):
        return self

    #use if need to relinquish resources.
    def __exit__(self,exc_type, exc_val, exc_tb):
        self
        
    def visualize(self):
        print("Printing the basic plots \n")

        sns.pairplot(self.df)
        plt.show()

        sns.boxplot(self.df)
        plt.show()

        sns.countplot(self.df)
        plt.show()

    def correlation_analysis(self):
        # Selecting only numeric features
        numeric_df = self.df.select_dtypes(include=['number'])

        # Compute correlation matrix
        correlation_matrix = numeric_df.corr()

        # Print correlation values
        print("Correlation Matrix:\n", correlation_matrix)

        # ** Heatmap for Visualization**
        plt.figure(figsize=(20, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
        plt.title("Feature Correlation Heatmap")
        plt.show()

    def cluster_analysis(self):
        self.cluster_data = self.df[['avg_latitude', 'avg_longitude', 'speed_limit']].dropna().copy()
        self.cluster_data = self.cluster_data.rename(columns={
            'avg_latitude': 'latitude',
            'avg_longitude': 'longitude'
    })
        scaler = StandardScaler()
        scaled_clustered_data = scaler.fit_transform(self.cluster_data)

        # KMeans — was missing in your refactor
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        self.cluster_data = self.cluster_data.copy()  # avoid SettingWithCopyWarning
        self.cluster_data['KMeans_Cluster'] = kmeans.fit_predict(scaled_clustered_data)

        # DBSCAN
        dbscan = DBSCAN(eps=.2, min_samples=100)
        self.cluster_data['DBSCAN_Cluster'] = dbscan.fit_predict(scaled_clustered_data)

    
    def visualize_map(self):
        # Find the center of the map (mean of all lat/lon)
        center_lat = self.cluster_data['latitude'].mean()
        center_lon = self.cluster_data['longitude'].mean()
        accident_map = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB positron')
        marker_cluster = MarkerCluster().add_to(accident_map)

        for idx, row in self.cluster_data.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Cluster: {row['KMeans_Cluster']}",
                icon=folium.Icon(color="red" if row['KMeans_Cluster'] == 0 else "blue")
            ).add_to(marker_cluster)

        accident_map.save("accident_clusters_map.html")
        return accident_map

    def visualize_w_map(self):
        sns.pairplot(self.cluster_data)
        plt.show()
        sns.boxplot(self.cluster_data)
        plt.show()

        fig, axes = plt.subplots(1, 2, figsize=(10, 5))

        sns.scatterplot(x=self.cluster_data['longitude'], y=self.cluster_data['latitude'],
                        hue=self.cluster_data['KMeans_Cluster'], ax=axes[0])
        axes[0].set_title('KMeans Cluster')
        axes[0].set_xlabel('Longitude')
        axes[0].set_ylabel('Latitude')

        sns.scatterplot(x=self.cluster_data['longitude'], y=self.cluster_data['latitude'],
                        hue=self.cluster_data['DBSCAN_Cluster'], ax=axes[1])
        axes[1].set_title('DBSCAN Cluster')
        axes[1].set_xlabel('Longitude')
        axes[1].set_ylabel('Latitude')

        plt.show()

    def generate_visuals(self):
        self.visualize()
        self.correlation_analysis()
        self.cluster_analysis()
        self.visualize_w_map()
        access_map=self.visualize_map()
        map_path = "accident_cluster_map.html"
        access_map.save(map_path)
        webbrowser.open_new_tab(map_path)
