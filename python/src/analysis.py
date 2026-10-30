"""
Fonctions d'analyse statistique
"""
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
import prince


def descriptive_stats(df: pd.DataFrame, column: str) -> dict:
    """Statistiques descriptives pour une colonne"""
    series = df[column]

    if pd.api.types.is_numeric_dtype(series):
        return {
            "type": "numeric",
            "count": int(series.count()),
            "mean": float(series.mean()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
            "median": float(series.median()),
            "q25": float(series.quantile(0.25)),
            "q75": float(series.quantile(0.75)),
        }
    else:
        value_counts = series.value_counts()
        return {
            "type": "categorical",
            "count": int(series.count()),
            "unique": int(series.nunique()),
            "top": str(value_counts.index[0]) if len(value_counts) > 0 else None,
            "freq": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            "distribution": value_counts.to_dict(),
        }


def crosstab_analysis(df: pd.DataFrame, var1: str, var2: str) -> dict:
    """Tableau croisé avec test du chi2"""
    ct = pd.crosstab(df[var1], df[var2])
    chi2, p_value, dof, expected = stats.chi2_contingency(ct)

    return {
        "crosstab": ct.to_dict(),
        "chi2": float(chi2),
        "p_value": float(p_value),
        "dof": int(dof),
        "significant": p_value < 0.05,
    }


def group_comparison(df: pd.DataFrame, numeric_var: str, group_var: str) -> dict:
    """Comparaison de moyennes entre groupes"""
    groups = df.groupby(group_var)[numeric_var]

    result = {
        "means": groups.mean().to_dict(),
        "stds": groups.std().to_dict(),
        "counts": groups.count().to_dict(),
    }

    # ANOVA si plus de 2 groupes
    group_data = [group.dropna().values for name, group in groups]
    if len(group_data) >= 2:
        f_stat, p_value = stats.f_oneway(*group_data)
        result["anova"] = {
            "f_statistic": float(f_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
        }

    return result


# =============================================================================
# ANALYSES MULTIVARIEES
# =============================================================================

def run_acm(df: pd.DataFrame, columns: list, n_components: int = 5) -> dict:
    """
    Analyse des Correspondances Multiples (ACM).

    Args:
        df: DataFrame avec les variables catégorielles
        columns: Liste des colonnes à inclure dans l'ACM
        n_components: Nombre de dimensions à retenir

    Returns:
        dict avec coordonnées, inertie, contributions
    """
    # Sélectionner et nettoyer les données
    data = df[columns].dropna()

    # Lancer l'ACM
    mca = prince.MCA(n_components=n_components)
    mca = mca.fit(data)

    # Coordonnées des individus
    row_coords = mca.row_coordinates(data)

    # Coordonnées des modalités
    col_coords = mca.column_coordinates(data)

    return {
        "n_individuals": len(data),
        "n_variables": len(columns),
        "inertia": {
            "eigenvalues": mca.eigenvalues_.tolist(),
            "explained_inertia": mca.percentage_of_variance_.tolist(),
            "cumulative_inertia": mca.percentage_of_variance_.cumsum().tolist(),
        },
        "row_coordinates": {
            f"dim{i+1}": row_coords[i].tolist()
            for i in range(min(n_components, len(row_coords.columns)))
        },
        "column_coordinates": col_coords.to_dict(orient="index"),
        "contributions": {
            "rows": mca.row_contributions_.to_dict() if hasattr(mca, 'row_contributions_') else None,
            "columns": mca.column_contributions_.to_dict() if hasattr(mca, 'column_contributions_') else None,
        }
    }


def run_clustering(df: pd.DataFrame, columns: list, n_clusters: int = 5,
                   use_acm: bool = True, n_acm_components: int = 5) -> dict:
    """
    Clustering (K-means) sur les données.

    Args:
        df: DataFrame
        columns: Colonnes à utiliser
        n_clusters: Nombre de clusters
        use_acm: Si True, fait le clustering sur les coordonnées ACM (pour données catégorielles)
        n_acm_components: Nombre de dimensions ACM à utiliser

    Returns:
        dict avec labels, centroides, caractérisation des clusters
    """
    data = df[columns].dropna()

    if use_acm:
        # ACM puis clustering sur les coordonnées
        mca = prince.MCA(n_components=n_acm_components)
        mca = mca.fit(data)
        coords = mca.row_coordinates(data)
        X = coords.values
    else:
        # Clustering direct (données numériques)
        scaler = StandardScaler()
        X = scaler.fit_transform(data)

    # K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    # Ajouter les labels au DataFrame original
    data_with_clusters = data.copy()
    data_with_clusters["cluster"] = labels

    # Caractérisation des clusters
    cluster_profiles = {}
    for cluster_id in range(n_clusters):
        cluster_data = data_with_clusters[data_with_clusters["cluster"] == cluster_id]
        profile = {
            "size": int(len(cluster_data)),
            "percentage": float(len(cluster_data) / len(data) * 100),
        }
        # Distribution des modalités dans chaque cluster
        for col in columns:
            if col != "cluster":
                profile[col] = cluster_data[col].value_counts(normalize=True).to_dict()
        cluster_profiles[f"cluster_{cluster_id}"] = profile

    return {
        "n_clusters": n_clusters,
        "n_individuals": len(data),
        "labels": labels.tolist(),
        "inertia": float(kmeans.inertia_),
        "cluster_sizes": pd.Series(labels).value_counts().sort_index().to_dict(),
        "cluster_profiles": cluster_profiles,
        "centroids": kmeans.cluster_centers_.tolist() if not use_acm else None,
    }


def run_regression(df: pd.DataFrame, target: str, features: list,
                   regression_type: str = "linear") -> dict:
    """
    Régression (linéaire ou logistique).

    Args:
        df: DataFrame
        target: Variable dépendante
        features: Variables explicatives
        regression_type: "linear" ou "logistic"

    Returns:
        dict avec coefficients, p-values, R2, etc.
    """
    import statsmodels.api as sm

    # Préparer les données
    data = df[[target] + features].dropna()

    # Encoder les variables catégorielles
    X = pd.get_dummies(data[features], drop_first=True)
    y = data[target]

    # Ajouter constante
    X = sm.add_constant(X)

    if regression_type == "logistic":
        # Régression logistique
        model = sm.Logit(y, X)
        results = model.fit(disp=0)

        return {
            "type": "logistic",
            "n_observations": int(len(data)),
            "coefficients": results.params.to_dict(),
            "std_errors": results.bse.to_dict(),
            "z_values": results.tvalues.to_dict(),
            "p_values": results.pvalues.to_dict(),
            "odds_ratios": np.exp(results.params).to_dict(),
            "conf_int_lower": results.conf_int()[0].to_dict(),
            "conf_int_upper": results.conf_int()[1].to_dict(),
            "pseudo_r2": float(results.prsquared),
            "aic": float(results.aic),
            "bic": float(results.bic),
        }
    else:
        # Régression linéaire (OLS)
        model = sm.OLS(y, X)
        results = model.fit()

        return {
            "type": "linear",
            "n_observations": int(len(data)),
            "coefficients": results.params.to_dict(),
            "std_errors": results.bse.to_dict(),
            "t_values": results.tvalues.to_dict(),
            "p_values": results.pvalues.to_dict(),
            "conf_int_lower": results.conf_int()[0].to_dict(),
            "conf_int_upper": results.conf_int()[1].to_dict(),
            "r_squared": float(results.rsquared),
            "r_squared_adj": float(results.rsquared_adj),
            "f_statistic": float(results.fvalue),
            "f_pvalue": float(results.f_pvalue),
            "aic": float(results.aic),
            "bic": float(results.bic),
        }
