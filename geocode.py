import polars as pl
from geopy.geocoders import Nominatim
from functools import partial


# defining geolocator
geolocator = Nominatim(user_agent="myApp")


def reverse_geocode(coordinates: str):
    location = geolocator.reverse(coordinates)
    return location.raw["address"]


# preparing the reverse geocode for polars dataframes
def get_address(df: pl.DataFrame, identifier: str, latitude: str, longitude: str):

    lat = pl.col(latitude)
    lon = pl.col(longitude)
    id = pl.col(identifier)
    str_type = pl.String

    # preparing latitude and longitude for inverse geocoding
    locations = df.select(id, lat.cast(str_type), lon.cast(str_type))
    df_to_geocode = locations.select(identifier, coord_str=(lat + pl.lit(", ") + lon))
    return df_to_geocode


def apply_reverse_geocode(df):
    return df.with_columns(pl.col("coord_str").map_elements(reverse_geocode))


def get_attribute(geo_dict, feature):
    return geo_dict[feature]


def extract_information(df):
    keys = [
        "shop",
        "road",
        "neighbourhood",
        "suburb",
        "city",
        "ISO3166-2-lvl4",
        "region",
        "postcode",
        "country",
        "country_code",
        "man_made",
        "locality",
        "city_district",
        "county",
        "state_district",
        "state",
        "house_number",
        "amenity",
        "quarter",
        "town",
        "office",
        "farm",
        "tourism",
        "building",
        "hamlet",
        "municipality",
        "village",
        "residential",
        "city_block",
        "highway",
        "aeroway",
        "club",
        "healthcare",
        "leisure",
        "craft",
        "place",
        "historic",
    ]

    for feature in keys:
        func = partial(get_attribute, feature=feature)
        df = df.with_columns(
            pl.col("coord_str")
            .map_elements(func, return_dtype=pl.String)
            .alias(feature)
        )

    return df.drop("coord_str")


def final_get_address(**kwargs):
    return extract_information(apply_reverse_geocode(get_address(**kwargs)))


path = r"C:\Users\abrah\OneDrive\Desktop\casoCAS\archivo\data\Competencia de Casos CAS + Addactis 2024 - Datos.xlsx"
locs = pl.read_excel(path, sheet_name="Ubicaciones Aseguradas")

final_geocode_df = final_get_address(
    df=locs, identifier="Loc ID", latitude="Latitud", longitude="Longitud"
)

final_geocode_df.write_excel(
    r"C:\Users\abrah\OneDrive\Desktop\casoCAS\archivo\data\geocodinginfo.xlsx"
)
