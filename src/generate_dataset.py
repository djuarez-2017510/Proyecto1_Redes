import csv
import random
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "properties.csv"

AREAS = [
    ("Zona 10", "Guatemala"),
    ("Zona 14", "Guatemala"),
    ("Zona 15", "Guatemala"),
    ("Zona 16", "Guatemala"),
    ("Carretera a El Salvador", "Fraijanes"),
    ("Antigua Centro", "Antigua Guatemala"),
]

PROPERTY_TYPES = ["apartment", "house", "townhouse", "land"]
AMENITIES = ["parking", "balcony", "garden", "security", "pool", "gym"]
FIELDS = [
    "property_id", "property_type", "operation", "price", "currency",
    "area_m2", "bedrooms", "bathrooms", "parking_spaces", "furnished",
    "pets_allowed", "year_built", "neighborhood", "municipality",
    "status", "amenities", "description",
]


def create_properties(amount=100):
    random.seed(2026)
    properties = []

    for number in range(1, amount + 1):
        neighborhood, municipality = random.choice(AREAS)
        property_type = random.choice(PROPERTY_TYPES)
        operation = random.choice(["sale", "rent"])

        if property_type == "land":
            area = round(random.uniform(200, 1800), 1)
            bedrooms = 0
            bathrooms = 0
        else:
            area = round(random.uniform(60, 450), 1)
            bedrooms = random.randint(1, 5)
            bathrooms = random.choice([1, 1.5, 2, 2.5, 3, 4])

        if operation == "sale":
            price = int(area * random.uniform(1100, 2200) / 500) * 500
            currency = "USD"
        else:
            price = int(max(3500, area * random.uniform(35, 75)) / 500) * 500
            currency = "GTQ"

        amenities = ",".join(sorted(random.sample(AMENITIES, random.randint(2, 4))))
        status = random.choices(
            ["available", "reserved", "sold"],
            weights=[75, 10, 15],
        )[0]
        description = (
            f"{property_type.title()} in {neighborhood}, {municipality}; "
            f"{area} square meters and {bedrooms} bedrooms."
        )

        properties.append({
            "property_id": f"GT-{number:04d}",
            "property_type": property_type,
            "operation": operation,
            "price": price,
            "currency": currency,
            "area_m2": area,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "parking_spaces": random.randint(0, 4),
            "furnished": random.choice([True, False]),
            "pets_allowed": random.choice([True, False]),
            "year_built": random.randint(1995, 2025),
            "neighborhood": neighborhood,
            "municipality": municipality,
            "status": status,
            "amenities": amenities,
            "description": description,
        })

    return properties


def main():
    DATA_FILE.parent.mkdir(exist_ok=True)
    with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(create_properties())
    print(f"Dataset created: {DATA_FILE}")


if __name__ == "__main__":
    main()
