import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

plt.style.use("ggplot")

st.title("Diamantanalys – Guldfynds affärsbeslut")

# --- SIDOPANEL ---
st.sidebar.header("Inställningar")

uploaded_file = st.sidebar.file_uploader(
    "Ladda upp en Excel- eller CSV-fil med diamanter",
    type=["csv", "xlsx"]
)

grafer = st.sidebar.multiselect(
    "Välj vilka grafer du vill visa:",
    ["Fördelning av pris och carat", "Kvalitetsfördelning", "Prisvärda diamanter (scatter)"],
    default=["Fördelning av pris och carat", "Kvalitetsfördelning", "Prisvärda diamanter (scatter)"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success("Filen är uppladdad och inläst!")
else:
    st.warning("Ladda upp en fil för att börja. Exempel: diamonds.csv eller diamonds.xlsx")
    st.stop()

# Rensa bort indexkolumn om den finns
if "Unnamed: 0" in df.columns:
    df = df.drop(columns="Unnamed: 0")

cut_order = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
color_order = ['D', 'E', 'F', 'G', 'H', 'I', 'J']
clarity_order = ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF']

# --- Sammanfattning av hela datasettet ---
st.header("Sammanfattning av uppladdat dataset")

antal_diamanter = len(df)
antal_cut = df['cut'].value_counts().to_dict()
antal_color = df['color'].value_counts().to_dict()
antal_clarity = df['clarity'].value_counts().to_dict()
min_carat = df['carat'].min()
max_carat = df['carat'].max()
min_price = df['price'].min()
max_price = df['price'].max()
median_carat = df['carat'].median()
median_price = df['price'].median()

st.markdown(f"""
**Antal diamanter:** {antal_diamanter}  
**Caratintervall:** {min_carat:.2f} – {max_carat:.2f} ct  
**Prisintervall:** ${min_price:,.0f} – ${max_price:,.0f}  
**Medianstorlek:** {median_carat:.2f} ct  
**Medianpris:** ${median_price:,.0f}  

**Antal diamanter per Cut:**  
""" +  
", ".join([f"{cut}: {antal}" for cut, antal in antal_cut.items()]) +  
"""

**Antal diamanter per Color:**  
""" +  
", ".join([f"{color}: {antal}" for color, antal in antal_color.items()]) +  
"""

**Antal diamanter per Clarity:**  
""" +  
", ".join([f"{clar}: {antal}" for clar, antal in antal_clarity.items()])
)

# -------- Prisvärda-funktionen --------------
def prisvarda_diamanter(df):
    prisvarda = df[
        (df['carat'] < 0.5) &
        (df['cut'] == "Ideal") &
        (df['color'].isin(["G", "H"])) &
        (df['clarity'].isin(["VS1", "VS2"]))
    ]
    return prisvarda

prisvarda = prisvarda_diamanter(df)
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
    sns.histplot(df["price"], bins=60, kde=True, color="#2878B5", ax=axes[0])
    axes[0].set_title("Fördelning av diamantpriser")
    axes[0].set_xlabel("Pris (USD)")
    axes[0].set_ylabel("Antal")
    sns.histplot(df["carat"], bins=60, kde=True, color="#F0A202", ax=axes[1])
    axes[1].set_title("Fördelning av carat")
    axes[1].set_xlabel("Carat")
    axes[1].set_ylabel("Antal")
    st.pyplot(fig)

if "Kvalitetsfördelning" in grafer:
    fig, ax = plt.subplots(1, 3, figsize=(16, 4))
    sns.countplot(x='cut', data=df, order=cut_order, hue='cut', palette="Set2", legend=False, ax=ax[0])
    sns.countplot(x='color', data=df, order=color_order, hue='color', palette="Spectral_r", legend=False, ax=ax[1])
    sns.countplot(x='clarity', data=df, order=clarity_order, hue='clarity', palette="coolwarm", legend=False, ax=ax[2])
    for a, t in zip(ax, ["Cut", "Color", "Clarity"]): 
        a.set_title(f"Fördelning av {t}")
    plt.tight_layout()
    st.pyplot(fig)

if "Prisvärda diamanter (scatter)" in grafer:
    fig, ax = plt.subplots(figsize=(8,5))
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

    # Visa sample-tabell med fynden direkt efter analysen
    st.subheader("Exempel på prisvärda diamanter under medianpris")
    st.dataframe(prisvarda_below_median.head(10))
