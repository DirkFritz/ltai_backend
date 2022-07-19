import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


class BestPerformer:
    def find_perfomrer(self, data, group_no):

        X = data[["Performance", "Draw-Down"]].to_numpy()
        X = np.nan_to_num(X)
        scaler = StandardScaler()
        cluster_dataset = scaler.fit_transform(X)

        # costs = []
        # for i in range(1, 12):
        #     k_means = KMeans(init="k-means++", n_clusters=i, n_init=12)
        #     k_means.fit(cluster_dataset)
        #     labels = k_means.labels_
        #     costs.append(k_means.inertia_)
        # labels

        k_means = KMeans(init="k-means++", n_clusters=group_no)
        k_means.fit(cluster_dataset)
        labels = k_means.labels_

        data[["Performance", "Draw-Down"]] = data[["Performance", "Draw-Down"]].round(2)

        labeled_data = pd.DataFrame(
            data, columns=["Symbol", "Performance", "Draw-Down"]
        )
        labeled_data["Labels"] = labels

        return labeled_data
