"""
Telco Churn - Kampanya Hedefleme MVP
Pipeline: veri temizliği -> feature engineering -> model -> segment/kampanya kural motoru
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report
import joblib
import json

import os
RAW_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "WA_Fn-UseC_-Telco-Customer-Churn.csv")


def load_and_clean(path=RAW_PATH):
    df = pd.read_csv(path)

    # TotalCharges bosluk karakterli 11 satir -> numeric'e cevir, NaN olanlari tenure=0 olan yeni musteriler
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].str.strip(), errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0)

    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})

    return df


def add_derived_features(df):
    """Feature engineering: mevcut sutunlardan turetilen yeni kolonlar."""
    df = df.copy()

    # 1) EstimatedCLV - basit varsayimsal yasam boyu deger
    # (tenure suresince odenen + gelecek 12 ay projeksiyonu)
    df["EstimatedCLV"] = df["TotalCharges"] + (df["MonthlyCharges"] * 12)

    # 2) ChurnReasonSegment - kural tabanli, notebook'taki EDA bulgularina dayanarak
    def assign_reason(row):
        # Her segment icin bir "guc skoru" hesapla, en yuksek skorlu segment secilir.
        # Bu, tek bir kuralin (orn. Month-to-month) her seyi ezmesini engeller.
        scores = {}

        scores["Fiyat Duyarli"] = (
            (2 if row["MonthlyCharges"] > 80 else (1 if row["MonthlyCharges"] > 65 else 0))
            + (1 if row["Contract"] == "Month-to-month" else 0)
        )
        scores["Hizmet Memnuniyetsizligi"] = (
            (2 if row["InternetService"] == "Fiber optic" and row["TechSupport"] == "No" else 0)
            + (1 if row["StreamingTV"] == "No" and row["StreamingMovies"] == "No" and row["InternetService"] != "No" else 0)
        )
        scores["Guvenlik/Yedekleme Eksikligi"] = (
            (1 if row["OnlineSecurity"] == "No" else 0)
            + (1 if row["OnlineBackup"] == "No" else 0)
            + (1 if row["DeviceProtection"] == "No" else 0)
        )
        scores["Sozlesme Esnekligi Ariyor"] = (
            (2 if row["Contract"] == "Month-to-month" and row["tenure"] < 12 else 0)
            + (1 if row["Contract"] == "Month-to-month" else 0)
        )
        scores["Odeme Surtunmesi"] = (
            (2 if row["PaymentMethod"] == "Electronic check" else 0)
            + (1 if row["PaperlessBilling"] == "No" else 0)
        )

        best_segment = max(scores, key=scores.get)
        if scores[best_segment] == 0:
            return "Genel Risk"
        return best_segment

    df["ChurnReasonSegment"] = df.apply(assign_reason, axis=1)

    return df


def add_campaign_recommendation(df):
    """Segment -> onerilen kampanya kurallari (varsayimsal is mantigi)."""
    campaign_map = {
        "Sozlesme Esnekligi Ariyor": "12 Aylik Sozlesmeye Gecis Indirimi (%15)",
        "Hizmet Memnuniyetsizligi": "3 Ay Ucretsiz TechSupport + Fiber Bakim Kontrolu",
        "Guvenlik/Yedekleme Eksikligi": "OnlineSecurity + OnlineBackup Paketi 1 Ay Ucretsiz Deneme",
        "Fiyat Duyarli": "Sadakat Indirimi (%10, 6 ay)",
        "Odeme Surtunmesi": "Otomatik Odemeye Gecis Tesviki (ilk ay %5 indirim)",
        "Genel Risk": "Kisisellestirilmis Musteri Temsilcisi Aramasi",
    }
    # Varsayimsal donusum orani (gercek A/B test verisi geldiginde guncellenecek)
    conversion_map = {
        "Sozlesme Esnekligi Ariyor": 0.28,
        "Hizmet Memnuniyetsizligi": 0.22,
        "Guvenlik/Yedekleme Eksikligi": 0.19,
        "Fiyat Duyarli": 0.24,
        "Odeme Surtunmesi": 0.15,
        "Genel Risk": 0.10,
    }
    # Varsayimsal kampanya maliyeti (musteri basi, USD) - kampanya turune gore farklilastirilmis
    # Indirim kampanyalari daha maliyetli, aramalar/deneme paketleri daha ucuz
    cost_map = {
        "Sozlesme Esnekligi Ariyor": 18,   # %15 indirim, 12 ay - orta maliyet
        "Hizmet Memnuniyetsizligi": 12,    # 3 ay ucretsiz TechSupport - operasyonel maliyet
        "Guvenlik/Yedekleme Eksikligi": 8, # 1 ay deneme paketi - dusuk maliyet
        "Fiyat Duyarli": 15,               # %10 indirim, 6 ay
        "Odeme Surtunmesi": 5,             # kucuk tesvik indirimi
        "Genel Risk": 10,                  # musteri temsilcisi arama maliyeti (zaman/iscilik)
    }
    df["CampaignCostPerCustomer"] = df["ChurnReasonSegment"].map(cost_map)
    df["_IsSimulated_CampaignCost"] = True

    df["RecommendedCampaign"] = df["ChurnReasonSegment"].map(campaign_map)
    df["SimulatedConversionRate"] = df["ChurnReasonSegment"].map(conversion_map)
    df["_IsSimulated_ConversionRate"] = True  # dashboard'da acikca etiketlemek icin
    return df


def train_model(df):
    """Churn risk skoru icin model egitimi."""
    model_df = df.copy()

    target = model_df["Churn"].map({"Yes": 1, "No": 0})
    drop_cols = ["customerID", "Churn", "ChurnReasonSegment", "RecommendedCampaign",
                 "SimulatedConversionRate", "_IsSimulated_ConversionRate", "EstimatedCLV",
                 "CampaignCostPerCustomer", "_IsSimulated_CampaignCost"]
    features = model_df.drop(columns=[c for c in drop_cols if c in model_df.columns])

    cat_cols = features.select_dtypes(include="object").columns.tolist()
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        features[col] = le.fit_transform(features[col])
        encoders[col] = le

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )

    rf = RandomForestClassifier(n_estimators=300, max_depth=8, class_weight="balanced", random_state=42)
    rf.fit(X_train, y_train)

    y_pred_proba = rf.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    report = classification_report(y_test, (y_pred_proba > 0.5).astype(int), output_dict=True)

    print(f"AUC: {auc:.4f}")
    print(classification_report(y_test, (y_pred_proba > 0.5).astype(int)))

    # tum veri seti icin risk skoru uret
    full_proba = rf.predict_proba(features)[:, 1]
    df["ChurnRiskScore"] = full_proba

    return df, rf, encoders, {"auc": auc, "report": report, "feature_columns": features.columns.tolist()}


def run_pipeline():
    df = load_and_clean()
    df = add_derived_features(df)
    df = add_campaign_recommendation(df)
    df, model, encoders, metrics = train_model(df)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    df.to_csv(os.path.join(base_dir, "enriched_telco.csv"), index=False)
    joblib.dump(model, os.path.join(base_dir, "churn_model.pkl"))
    joblib.dump(encoders, os.path.join(base_dir, "encoders.pkl"))
    with open(os.path.join(base_dir, "metrics.json"), "w") as f:
        json.dump({"auc": metrics["auc"]}, f)

    print("\n--- Segment Dagilimi ---")
    print(df["ChurnReasonSegment"].value_counts())
    print("\n--- Ornek Zenginlestirilmis Satirlar ---")
    cols = ["customerID", "Churn", "ChurnRiskScore", "ChurnReasonSegment",
            "RecommendedCampaign", "EstimatedCLV"]
    print(df[cols].head(10).to_string(index=False))

    return df


if __name__ == "__main__":
    run_pipeline()
