# Import libraries
import pandas as pd
import pycountry
import datetime

# Function to convert country name to ISO country code
def country_to_iso(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except:
        return None

# Function to process a geographic reference
def process_geo_reference(geo_reference):
    if pd.isnull(geo_reference) or not isinstance(geo_reference, str):
        return [], []

    countries = []
    regions_cities = []

    parts = [part.strip() for part in geo_reference.split(',')]

    for part in parts:
        # Split the part by ' and ' to handle cases where the geographic reference contains multiple locations
        subparts = [subpart.strip() for subpart in part.split(' and ')]

        for subpart in subparts:
            # If the subpart contains a country name in parentheses, remove the parentheses and use the country name inside
            if '(' in subpart and ')' in subpart:
                subpart = subpart[subpart.index('(') + 1:subpart.index(')')]

            iso = country_to_iso(subpart)
            if iso is not None:
                countries.append(iso)
                if iso == 'HK':
                    regions_cities.append('Hong Kong')
            else:
                # Handle special cases
                if subpart.lower() == 'laos':
                    countries.append('LA')
                elif subpart.lower() == 'usa':
                    countries.append('US')
                elif subpart.lower() == 'taiwan':
                    countries.append('TW')
                elif subpart.lower() in ['u.k., england', 'u.k.', 'u.k., british', 'great britain']:
                    countries.append('GB')
                    if subpart.lower() == 'u.k., england':
                        regions_cities.append('England')
                elif subpart.lower() == 'england':
                    regions_cities.append('England')
                elif subpart.lower() == 'malacca':
                    countries.append('MY')
                    regions_cities.append('Malacca')
                elif subpart.lower() == 'penang':
                    countries.append('MY')
                    regions_cities.append('Penang')
                elif subpart.lower() == 'north vietnam':
                    countries.append('VN')
                elif subpart.lower() == 'singapore/uk':
                    countries.extend(['SG', 'GB'])
                elif subpart.lower() == 'singapore, great britain':
                    countries.extend(['SG', 'GB'])
                elif subpart.lower() == 'singapore, malaya':
                    countries.extend(['SG', 'MY'])
                elif subpart.lower() == 'british':
                    pass  # Do nothing as 'British' is not a region/city
                elif subpart.lower() == 'malaya':
                    countries.append('MY')  # Map 'Malaya' to 'MY'
                elif subpart.lower() == 'brunei':
                    countries.append('BN')  # Map 'Brunei' to 'BN'
                elif subpart.lower() == 'burma':
                    countries.append('MM')  # Map 'Burma' to 'MM'
                else:
                    regions_cities.append(subpart)

    if len(countries) == 0 and len(regions_cities) > 0:
        for region_city in regions_cities:
            iso = country_to_iso(region_city)
            if iso is not None:
                countries.append(iso)
                regions_cities.remove(region_city)

    return countries, regions_cities

def main():
    # Load data
    data = pd.read_excel('raw_data/artworks.xlsx')

    # Apply the function to process geographic references to the original data
    data['Country'], data['Region/City'] = zip(*data['Geo. Reference'].apply(process_geo_reference))

    # Define the test cases
    test_cases = [
        ('Singapore', (['SG'], [])),  # Single country with no region
        ('Bali, Indonesia', (['ID'], ['Bali'])),  # Single country with region
        ('France and Singapore', (['FR', 'SG'], [])),  # Multiple countries with no region
        ('U.K., England', (['GB'], ['England'])),  # Single country with region
        ('Singapore and Penang', (['SG', 'MY'], ['Penang'])),  # Multiple countries with region
        ('U.K., British', (['GB'], [])),  # Single country with no region, special case
        ('Singapore, Great Britain', (['SG', 'GB'], [])),  # Multiple countries with no region, special case
        ('Singapore, Malaya', (['SG', 'MY'], [])),  # Multiple countries with no region, special case
        ('Malacca', (['MY'], ['Malacca'])),  # Single region (should be mapped to country)
        ('Penang', (['MY'], ['Penang'])),  # Single region (should be mapped to country)
        ('North Vietnam', (['VN'], [])),  # Single country with no region, special case
        ('Hong Kong', (['HK'], ['Hong Kong'])),  # Single country with no region, special case
        ('Laos', (['LA'], [])),  # Single country with no region, special case
        ('USA', (['US'], [])),  # Single country with no region, special case
        ('Taiwan', (['TW'], []))  # Single country with no region, special case
    ]

    # Run the tests
    for i, (input_value, expected_output) in enumerate(test_cases):
        actual_output = process_geo_reference(input_value)
        assert actual_output == expected_output, f'Test case {i+1} failed: expected {expected_output}, got {actual_output}'

    print('All test cases passed')

    # Save the processed DataFrame as an Excel file
    today = datetime.date.today()
    data.to_excel(f'raw_data/artworks_cleaned_{today.strftime("%d%m%Y")}.xlsx', index=False)

if __name__ == "__main__":
    main()
