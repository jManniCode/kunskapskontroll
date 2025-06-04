import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

plt.style.use("ggplot")


def clean_diamond_data(df):
    """
    Rensar diamant-dataset enligt följande:
    - Tar bort diamanter med saknade värden
    - Tar bort diamanter med "0"
    - Tar bort extrema mått (>15 mm)
    - Tar bort rader med mer än 1% avvikelse i depth
    Returnerar rensad dataframe samt rensningsrapport.
    """
    report = {}
    report['Antal från början'] = len(df)

    # Saknade värden
    before = len(df)
    df = df.dropna(subset=['cut', 'color', 'clarity', 'price', 'carat', 'x', 'y', 'z', 'depth'])
    report['Saknade värden'] = before - len(df)

    # Nollvärden i numeriska kolumner
    before = len(df)
    numeric_cols = ['carat', 'depth', 'table', 'price', 'x', 'y', 'z']
    for col in numeric_cols:
        df = df[df[col] > 0]
    report['Nollvärden i numeriska kolumner'] = before - len(df)

    # Extrema mått (>15 mm)
    before = len(df)
    df = df[(df['x'] <= 15) & (df['y'] <= 15) & (df['z'] <= 15)]
    report['Extrema mått (>15 mm)'] = before - len(df)

    # >1% avvikelse i depth
    df['depth_calc'] = (df['z'] / ((df['x'] + df['y']) / 2)) * 100
    df['depth_diff'] = abs(df['depth_calc'] - df['depth'])
    before = len(df)
    df = df[df['depth_diff'] <= 1]
    report['>1% avvikelse i depth'] = before - len(df)

    # Summering
    report['Totalt borttagna rader'] = report['Antal från början'] - len(df)
    report['Rader kvar efter rensning'] = len(df)

    # Ta bort temporära kolumner
    df = df.drop(columns=['depth_calc', 'depth_diff'])

    return df, report


def prisvarda_diamanter(df):
    """
    Filtrerar ut små prisvärda diamanter:
    - Carat < 0.5
    - Ideal cut
    - Färg G eller H
    - Klarhet VS1 eller VS2
    Returnerar filtrerad dataframe.
    """
    prisvarda = df[
        (df['carat'] < 0.5) &
        (df['cut'] == "Ideal") &
        (df['color'].isin(["G", "H"])) &
        (df['clarity'].isin(["VS1", "VS2"]))
    ]
    return prisvarda


# ----------- Streamlit UI -----------

st.title("💎 Diamantanalys")

# --- SIDOPANEL ---
st.sidebar.header("Inställningar")

uploaded_file = st.sidebar.file_uploader(
    "Ladda upp en Excel- eller CSV-fil med diamanter",
    type=["csv", "xlsx"]
)

grafer = st.sidebar.multiselect(
    "Välj vilka grafer du vill visa:",
    [
        "Fördelning av pris och carat",
        "Kvalitetsfördelning",
        "Prisvärda diamanter (scatter)"
    ],
    default=[
        "Fördelning av pris och carat",
        "Kvalitetsfördelning",
        "Prisvärda diamanter (scatter)"
    ]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success("Filen är uppladdad och inläst!")
else:
    st.warning("Ladda upp en fil för att se graferna")
    st.stop()

# Rensa bort indexkolumn om den finns
if "Unnamed: 0" in df.columns:
    df = df.drop(columns="Unnamed: 0")

# --------- DATARENISNG ----------
clean_df, rensningsinfo = clean_diamond_data(df)

cut_order = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
color_order = ['D', 'E', 'F', 'G', 'H', 'I', 'J']
clarity_order = ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF']

# --- Sammanfattning av hela datasettet ---
antal_diamanter = len(clean_df)
antal_cut = clean_df['cut'].value_counts().to_dict()
antal_color = clean_df['color'].value_counts().to_dict()
antal_clarity = clean_df['clarity'].value_counts().to_dict()
min_carat = clean_df['carat'].min()
max_carat = clean_df['carat'].max()
min_price = clean_df['price'].min()
max_price = clean_df['price'].max()
median_carat = clean_df['carat'].median()
median_price = clean_df['price'].median()

# --------- VISA TVÅ KORT BREDVID VARANDRA ---------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Rensningsrapport")
    st.markdown(
        f"""
        **Antal diamanter från början:** {rensningsinfo['Antal från början']}  
        **Saknade värden:** {rensningsinfo['Saknade värden']} borttagna  
        **Nollvärden i numeriska kolumner:** {rensningsinfo['Nollvärden i numeriska kolumner']} borttagna  
        **Extrema mått (>15 mm):** {rensningsinfo['Extrema mått (>15 mm)']} borttagna  
        **>1% avvikelse i depth:** {rensningsinfo['>1% avvikelse i depth']} borttagna  
        **Totalt borttagna rader:** {rensningsinfo['Totalt borttagna rader']}  
        **Rader kvar efter rensning:** {rensningsinfo['Rader kvar efter rensning']}  
        """
    )

with col2:
    st.subheader("Sammanfattning av uppladdat dataset efter rensning")
    st.markdown(
        f"""
        **Antal diamanter:** {antal_diamanter}  
        **Caratintervall:** {min_carat:.2f} – {max_carat:.2f} ct  
        **Prisintervall:** ${min_price:,.0f} – ${max_price:,.0f}  
        **Medianstorlek:** {median_carat:.2f} ct  
        **Medianpris:** ${median_price:,.0f}  

        **Antal diamanter per Cut:**  
        {", ".join([f"{cut}: {antal}" for cut, antal in antal_cut.items()])}

        **Antal diamanter per Color:**  
        {", ".join([f"{color}: {antal}" for color, antal in antal_color.items()])}

        **Antal diamanter per Clarity:**  
        {", ".join([f"{clar}: {antal}" for clar, antal in antal_clarity.items()])}
        """
    )

# -------- Prisvärda-funktionen --------------
prisvarda = prisvarda_diamanter(clean_df)
medianpris_kategori = prisvarda['price'].median()
median_carat_kategori = prisvarda['carat'].median()
prisvarda_below_median = prisvarda[prisvarda['price'] < medianpris_kategori]

# Nyckeltal – hela kategorin
antal_kategori = len(prisvarda)
min_carat_kategori = prisvarda['carat'].min()
max_carat_kategori = prisvarda['carat'].max()
min_pris_kategori = prisvarda['price'].min()
max_pris_kategori = prisvarda['price'].max()
median_carat_kategori = prisvarda['carat'].median()
median_pris_kategori = prisvarda['price'].median()

# Nyckeltal – fynden
antal_fynd = len(prisvarda_below_median)
min_carat_fynd = prisvarda_below_median['carat'].min()
max_carat_fynd = prisvarda_below_median['carat'].max()
min_pris_fynd = prisvarda_below_median['price'].min()
max_pris_fynd = prisvarda_below_median['price'].max()
median_carat_fynd = prisvarda_below_median['carat'].median()
median_pris_fynd = prisvarda_below_median['price'].median()

# ----- Visa valda grafer -----
if "Fördelning av pris och carat" in grafer:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(clean_df["price"], bins=60, kde=True, color="#2878B5", ax=axes[0])
    axes[0].set_title("Fördelning av diamantpriser")
    axes[0].set_xlabel("Pris (USD)")
    axes[0].set_ylabel("Antal")
    sns.histplot(clean_df["carat"], bins=60, kde=True, color="#F0A202", ax=axes[1])
    axes[1].set_title("Fördelning av carat")
    axes[1].set_xlabel("Carat")
    axes[1].set_ylabel("Antal")
    st.pyplot(fig)

if "Kvalitetsfördelning" in grafer:
    fig, ax = plt.subplots(1, 3, figsize=(16, 4))
    sns.countplot(x='cut', data=clean_df, order=cut_order, hue='cut', palette="Set2", legend=False, ax=ax[0])
    sns.countplot(x='color', data=clean_df, order=color_order, hue='color', palette="Spectral_r", legend=False, ax=ax[1])
    sns.countplot(x='clarity', data=clean_df, order=clarity_order, hue='clarity', palette="coolwarm", legend=False, ax=ax[2])
    for a, t in zip(ax, ["Cut", "Color", "Clarity"]):
        a.set_title(f"Fördelning av {t}")
    plt.tight_layout()
    st.pyplot(fig)

if "Prisvärda diamanter (scatter)" in grafer:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(prisvarda['carat'], prisvarda['price'], alpha=0.4, label="Alla i kategori", color='grey')
    ax.scatter(prisvarda_below_median['carat'], prisvarda_below_median['price'],
               color='orange', label='Under medianpris', s=70)
    ax.axhline(medianpris_kategori, color='red', linestyle='--', label='Medianpris (kategori)')
    ax.axhline(medianpris_kategori * 1.10, color='green', linestyle='--', label='+10% över median')
    ax.axvline(median_carat_kategori, color='blue', linestyle=':', label='Median carat (kategori)')
    ax.set_xlabel("Carat")
    ax.set_ylabel("Pris (USD)")
    ax.set_title("Prisvärda diamanter: <0.5ct, Ideal, G/H, VS1/VS2 clarity")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

    # Analys och nyckeltal efter scattergrafen
    st.subheader("Analys: Prisvärda diamanter")
    st.markdown(f"""
    **Hela kategorin** (<0.5 ct, Ideal, G/H, VS1/VS2):

    - Antal diamanter: **{antal_kategori}**
    - Caratintervall: **{min_carat_kategori:.2f}–{max_carat_kategori:.2f} ct**
    - Prisintervall: **${min_pris_kategori:,}–${max_pris_kategori:,} USD**
    - Medianstorlek: **{median_carat_kategori:.2f} ct**
    - Medianpris: **${median_pris_kategori:,.0f} USD**

    **Fynd under medianpris:**

    - Antal fynd: **{antal_fynd}**
    - Caratintervall: **{min_carat_fynd:.2f}–{max_carat_fynd:.2f} ct**
    - Prisintervall: **${min_pris_fynd:,}–${max_pris_fynd:,} USD**
    - Medianstorlek (fynd): **{median_carat_fynd:.2f} ct**
    - Medianpris (fynd): **${median_pris_fynd:,.0f} USD**
    """)

    st.subheader("Exempel på prisvärda diamanter under medianpris")
    st.dataframe(prisvarda_below_median.head(10))
