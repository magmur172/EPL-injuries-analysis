import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_excel('data/processed/player_injuries_impact(Edited).xlsx')

df['Date of return'] = pd.to_datetime(df['Date of return'], format='%d.%m.%Y', errors='coerce')
df['Date of Injury'] = pd.to_datetime(df['Date of Injury'], format='%d.%m.%Y', errors='coerce')
if 'Downtime (days)' not in df.columns:
    df['Downtime (days)'] = (df['Date of return'] - df['Date of Injury']).dt.days

df_no_poly = df[df['Injury Category'] != 'Polytrauma']

position_order = [
    'Goalkeeper',
    'Left Back',
    'Center Back',
    'Right Back',
    'Left Midfielder',
    'Defensive Midfielder',
    'Central Midfielder',
    'Attacking Midfielder',
    'Right Midfielder',
    'Left winger',
    'Center Forward',
    'Right winger'
]
df_no_poly['Position'] = pd.Categorical(
    df_no_poly['Position'],
    categories=position_order,
    ordered=True
)

st.title("EPL Injuries Analysis Dashboard")

st.markdown("""
Choose any chart from the dropdown below to explore different injury analytics in the English Premier League dataset!
""")

chart = st.selectbox(
    "Select a chart:",
    ["Average Downtime by Injury Category",
     "Mean and Median Downtime by Player Position",
     "Downtime Distribution by Position (Boxplot, log scale)",
     "Injury Count by Player Position",
    "Injury Type Frequency by Position (Heatmap)"
    ]
)

if chart == "Average Downtime by Injury Category":
    downtime_by_injury = df_no_poly.groupby('Injury Category')['Downtime (days)'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(12,6))
    downtime_by_injury.plot(kind='bar', color='steelblue', ax=ax)
    ax.set_title('Average Downtime by Injury Category (Polytrauma Excluded)')
    ax.set_ylabel('Average downtime (days)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

elif chart == "Mean and Median Downtime by Player Position":
    downtime_stats = df_no_poly.groupby('Position')['Downtime (days)'].agg(['mean', 'median']).reindex(position_order)
    downtime_stats = downtime_stats.reset_index()
    fig, ax = plt.subplots(figsize=(12,6))
    bar_width = 0.4
    positions = range(len(downtime_stats))
    ax.bar([p - bar_width/2 for p in positions], downtime_stats['mean'], width=bar_width, label='Mean', color='skyblue')
    ax.bar([p + bar_width/2 for p in positions], downtime_stats['median'], width=bar_width, label='Median', color='coral')
    ax.set_xticks(list(positions))
    ax.set_xticklabels(downtime_stats['Position'], rotation=45, ha='right')
    ax.set_ylabel('Downtime (days)')
    ax.set_title('Mean and Median Downtime by Player Position (Polytrauma Excluded)')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)

elif chart == "Downtime Distribution by Position (Boxplot, log scale)":
    fig, ax = plt.subplots(figsize=(12,6))
    sns.boxplot(
        data=df_no_poly,
        x='Position',
        y='Downtime (days)',
        palette='Set3',
        showfliers=False,
        whis=[5,95],
        ax=ax
    )
    sns.stripplot(
        data=df_no_poly,
        x='Position',
        y='Downtime (days)',
        size=3,
        color='gray',
        alpha=0.4,
        jitter=True,
        ax=ax
    )
    ax.set_yscale('log')
    ax.set_title('Downtime Distribution by Position (log scale)')
    ax.set_ylabel('Downtime (days), log scale')
    ax.set_xlabel('Position')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

elif chart == "Injury Count by Player Position":
    injury_counts = df_no_poly['Position'].value_counts().reindex(position_order).fillna(0)
    fig, ax = plt.subplots(figsize=(10,5))
    bars = ax.bar(injury_counts.index, injury_counts.values, color='teal')
    ax.set_title('Injury Count by Player Position')
    ax.set_xlabel('Position')
    ax.set_ylabel('Number of Injuries')
    plt.xticks(rotation=45, ha='right')
    for i, count in enumerate(injury_counts.values):
        ax.text(i, count + 0.5, int(count), ha='center', va='bottom', fontsize=9, color='black')
    plt.tight_layout()
    st.pyplot(fig)

elif chart == "Injury Type Frequency by Position (Heatmap)":
    injury_type_by_pos = pd.pivot_table(
        df_no_poly,
        index='Position',
        columns='Injury Category',
        values='Downtime (days)',
        aggfunc='count',
        fill_value=0
    ).reindex(position_order)
    fig, ax = plt.subplots(figsize=(14,6))
    sns.heatmap(injury_type_by_pos, annot=True, fmt='d', cmap='Blues', ax=ax)
    ax.set_title('Injury Type Frequency by Position')
    ax.set_xlabel('Injury Category')
    ax.set_ylabel('Position')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")
st.markdown("Data source: Kaggle (edited). App by Janibek Magmurov(https://github.com/magmur172).")