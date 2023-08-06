import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pycountry

def main():
    # Load the data
    data = pd.read_excel("../raw_data/artworks_final_07082023.xlsx")

    # Clean the country codes and compute frequency of artworks per country
    country_counts = {}
    def clean_and_add_country_counts_v2(countries):
        cleaned_countries = countries.replace("[", "").replace("]", "").replace("'", "").split(",")
        for country_code in cleaned_countries:
            country_code = country_code.strip()
            if country_code:
                country_name = pycountry.countries.get(alpha_2=country_code).alpha_3
                country_counts[country_name] = country_counts.get(country_name, 0) + 1

    data['Country'].dropna().apply(clean_and_add_country_counts_v2)

    # Display frequency count
    for country, count in country_counts.items():
        print(f"{country}: {count}")

    # Read in the world map data
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Merge the world map data with the country counts
    world = world.merge(pd.DataFrame.from_dict(country_counts, orient='index', columns=['Count']), left_on='iso_a3', right_index=True, how='left').fillna(0)

    # Plotting
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.boundary.plot(ax=ax, linewidth=1)
    world.plot(column='Count', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

    # Annotate countries with their 3-letter codes
    for _, row in world.iterrows():
        if row['iso_a3'] in country_counts:
            ax.text(row['geometry'].centroid.x, row['geometry'].centroid.y, row['iso_a3'], fontsize=8, ha='center')

    # Adjustments for Singapore to make it more visible
    if 'SGP' in country_counts:
        sg_x, sg_y = 103.8, 1.3  # Approximate centroid for Singapore
        ax.text(sg_x, sg_y, 'SGP', fontsize=8, ha='center', color='black', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

    ax.set_title('Heatmap of Artworks by Country')
    ax.set_xlim(60, 160)
    ax.set_ylim(-20, 60)

    # Save the figure
    plt.tight_layout()
    plt.savefig("../raw_data/artworks_heatmap.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    main()
