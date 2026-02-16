
import ingest_Data
import json

# Sample data from user request
animal_json = [
    {
        "name": "Red Panda",
        "taxonomy": {
            "kingdom": "Animalia",
            "phylum": "Chordata",
            "class": "Mammalia",
            "order": "Carnivora",
            "family": "Ailuridae",
            "genus": "Ailurus",
            "scientific_name": "Ailurus fulgens"
        },
        "locations": [
            "Asia"
        ],
        "characteristics": {
            "prey": "Bamboo, Berries, Eggs",
            "name_of_young": "Cub",
            "group_behavior": "Solitary",
            "estimated_population_size": "less than 3,000",
            "biggest_threat": "Habitat loss",
            "most_distinctive_feature": "Rusty coloured thick fur and striped face",
            "other_name(s)": "Lesser Panda, Fire Fox",
            "gestation_period": "4 months",
            "habitat": "High-altitude mountain forest",
            "predators": "Snow Leopard, Marten, Human",
            "diet": "Omnivore",
            "average_litter_size": "3",
            "lifestyle": "Nocturnal",
            "common_name": "Red Panda",
            "number_of_species": "1",
            "location": "Himalayas",
            "slogan": "There are less than 3,000 left in the wild!",
            "group": "Mammal",
            "color": "BrownRedWhite",
            "skin_type": "Fur",
            "top_speed": "24 mph",
            "lifespan": "8 - 12 years",
            "weight": "3kg - 6.2kg (7lbs - 14lbs)",
            "length": "60cm - 120cm (24in - 47in)",
            "age_of_sexual_maturity": "18 months",
            "age_of_weaning": "5 months"
        }
    }
]

observations_json = {
    "total_results": 326517323,
    "page": 1,
    "per_page": 30,
    "results": [
        {
            "location": "-33.922333,150.837203", # Sydney 1
            "id": 1
        },
        {
            "location": "-33.922500,150.837500", # Sydney 2 (very close, should cluster with 1)
            "id": 2
        },
        {
            "location": "27.1751,78.0421", # Agra, India (far away, new cluster)
            "id": 3
        },
        {
            "location": "27.1755,78.0425", # Agra, India (close to 3, should cluster)
            "id": 4
        },
        {
             "location": "40.7128,-74.0060", # New York (far away, new cluster)
             "id": 5
        }
    ]
}

def run_test():
    print("Connecting to DB...")
    conn = ingest_Data.get_db_connection()
    if not conn:
        print("Failed to connect.")
        return

    print("Creating Schema...")
    ingest_Data.create_schema(conn)

    print("Inserting Data...")
    ingest_Data.insert_animal_data(conn, animal_json, observations_json)
    
    conn.close()
    print("Test Complete.")

if __name__ == "__main__":
    run_test()
