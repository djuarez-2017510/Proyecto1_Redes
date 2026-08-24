import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class PropertyStore:
    def __init__(self, properties_file, appointments_file):
        self.properties_file = Path(properties_file)
        self.appointments_file = Path(appointments_file)
        self.properties = self.load_properties()
        self.properties_by_id = {
            item["property_id"]: item for item in self.properties
        }

        if not self.appointments_file.exists():
            self.appointments_file.write_text("[]\n", encoding="utf-8")

    def load_properties(self):
        properties = []

        with self.properties_file.open("r", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                row["price"] = int(row["price"])
                row["area_m2"] = float(row["area_m2"])
                row["bedrooms"] = int(row["bedrooms"])
                row["bathrooms"] = float(row["bathrooms"])
                row["parking_spaces"] = int(row["parking_spaces"])
                row["furnished"] = row["furnished"].lower() == "true"
                row["pets_allowed"] = row["pets_allowed"].lower() == "true"
                row["year_built"] = int(row["year_built"])
                properties.append(row)

        return properties

    def search(self, filters):
        results = []
        limit = min(max(int(filters.get("limit", 10)), 1), 50)

        for property_data in self.properties:
            if property_data["status"] != "available":
                continue

            if filters.get("municipality"):
                if filters["municipality"].lower() != property_data["municipality"].lower():
                    continue

            if filters.get("neighborhood"):
                if filters["neighborhood"].lower() not in property_data["neighborhood"].lower():
                    continue

            if filters.get("property_type"):
                if property_data["property_type"] != filters["property_type"]:
                    continue

            if filters.get("operation"):
                if property_data["operation"] != filters["operation"]:
                    continue

            if filters.get("currency"):
                if property_data["currency"] != filters["currency"]:
                    continue

            if "max_price" in filters and property_data["price"] > float(filters["max_price"]):
                continue

            if "min_price" in filters and property_data["price"] < float(filters["min_price"]):
                continue

            if "bedrooms" in filters and property_data["bedrooms"] < int(filters["bedrooms"]):
                continue

            if "bathrooms" in filters and property_data["bathrooms"] < float(filters["bathrooms"]):
                continue

            results.append(property_data)

        results.sort(key=lambda item: item["price"])
        return results[:limit]

    def schedule_visit(self, data):
        property_id = str(data.get("property_id", "")).strip()
        name = str(data.get("client_name", "")).strip()
        email = str(data.get("client_email", "")).strip()
        visit_at = str(data.get("visit_at", "")).strip()
        notes = str(data.get("notes", "")).strip()

        if property_id not in self.properties_by_id:
            raise ValueError("Property was not found")

        if self.properties_by_id[property_id]["status"] != "available":
            raise ValueError("Property is not available")

        if len(name) < 2:
            raise ValueError("Client name is too short")

        if not re.match(EMAIL_PATTERN, email):
            raise ValueError("Client email is invalid")

        try:
            parsed_date = datetime.fromisoformat(visit_at.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("visit_at must use ISO 8601 format") from error

        if parsed_date.tzinfo is None:
            raise ValueError("visit_at must include a timezone, for example -06:00")

        appointments = json.loads(self.appointments_file.read_text(encoding="utf-8"))
        appointment = {
            "appointment_id": f"APT-{len(appointments) + 1:04d}",
            "property_id": property_id,
            "client_name": name,
            "client_email": email,
            "visit_at": visit_at,
            "notes": notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "scheduled",
        }
        appointments.append(appointment)
        self.appointments_file.write_text(
            json.dumps(appointments, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return appointment
