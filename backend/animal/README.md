# `animal` App

The `animal` app is the central data layer for all animal-related information in BioGuesser. It exposes read-only API endpoints for fetching animals, their geographic sighting locations, and biological characteristics.

---

## Models

All models in this app are **unmanaged** (`managed = False`) — they map to tables managed externally by the data extraction pipeline.

### `Animal`

The core animal record.

| Field             | Type            | Description                                                                 |
| ----------------- | --------------- | --------------------------------------------------------------------------- |
| `id`              | `UUIDField`     | Primary key                                                                 |
| `name`            | `TextField`     | Common name                                                                 |
| `scientific_name` | `TextField`     | Scientific name (unique)                                                    |
| `image_url`       | `TextField`     | URL to species image                                                        |
| `max_probability` | `FloatField`    | Max H3-cell probability across all sightings (used for score normalisation) |
| `entropy`         | `FloatField`    | Distribution entropy of sightings                                           |
| `created_at`      | `DateTimeField` | Ingestion timestamp                                                         |

### `AnimalLocation`

Geographic sighting records, aggregated into H3 hexagonal grid cells.

| Field       | Type                 | Description                      |
| ----------- | -------------------- | -------------------------------- |
| `id`        | `UUIDField`          | Primary key                      |
| `animal`    | `ForeignKey(Animal)` | Parent animal                    |
| `h3_index`  | `TextField`          | H3 cell index (resolution 2)     |
| `latitude`  | `FloatField`         | Cell centre latitude             |
| `longitude` | `FloatField`         | Cell centre longitude            |
| `count`     | `IntegerField`       | Number of sightings in this cell |

### `AnimalCharacteristic`

Static biological traits for a given animal.

| Field                                                                                 | Type                 | Description         |
| ------------------------------------------------------------------------------------- | -------------------- | ------------------- |
| `id`                                                                                  | `UUIDField`          | Primary key         |
| `animal`                                                                              | `ForeignKey(Animal)` | Parent animal       |
| `prey`, `habitat`, `predators`                                                        | `TextField`          | Ecological data     |
| `top_speed`, `lifespan`, `weight`, `length`                                           | `TextField`          | Physical stats      |
| `skin_type`, `color`                                                                  | `TextField`          | Physical appearance |
| `gestation_period`, `average_litter_size`, `age_of_sexual_maturity`, `age_of_weaning` | `TextField`          | Reproductive data   |

---

## API Endpoints

All endpoints require authentication (`IsAuthenticated`). Requests must include a valid JWT in the `Authorization: Bearer <token>` header.

### `GET /api/animal/batch/`

Returns a batch of animals for use in the game menu / card selection.

**Query params:**
| Param | Default | Description |
|---|---|---|
| `limit` | `10` | Number of animals to return |
| `ordering` | `random` | `random` or `alphabetical` |

**Response** (array of `AnimalBasicSerializer`):

```json
[
  {
    "id": "uuid",
    "name": "Lion",
    "scientific_name": "Panthera leo",
    "image_url": "https://...",
    "characteristics": [ { "habitat": "Savanna", "lifespan": "10-14 years", ... } ]
  }
]
```

> **Note:** Random ordering uses `random.sample()` over the full queryset count for efficiency, avoiding the costly `ORDER BY RANDOM()` SQL pattern.

---

### `GET /api/animal/<uuid:animal_id>`

Returns the full detail for a single animal, including all sighting locations and characteristics.

**Response** (single `AnimalDetailSerializer`):

```json
{
  "id": "uuid",
  "name": "Lion",
  "scientific_name": "Panthera leo",
  "locations": [
    { "latitude": -1.3, "longitude": 36.8, "h3_index": "82...", "count": 42 }
  ],
  "characteristics": [ { ... } ]
}
```

---

## Serializers

| Serializer                       | Used for             | Fields                                                          |
| -------------------------------- | -------------------- | --------------------------------------------------------------- |
| `AnimalBasicSerializer`          | Batch list view      | `id`, `name`, `scientific_name`, `image_url`, `characteristics` |
| `AnimalDetailSerializer`         | Single animal detail | `id`, `name`, `scientific_name`, `locations`, `characteristics` |
| `AnimalLocationSerializer`       | Nested in detail     | `latitude`, `longitude`, `h3_index`, `count`                    |
| `AnimalCharacteristicSerializer` | Nested in both       | All fields                                                      |

---

## Dependencies

- **`authentication`** — `CustomJWTAuthentication` for JWT validation
- **`extraction`** — Populates the underlying database tables (`animals`, `animal_locations`, `animal_characteristics`)
- **`game`** — Reads `AnimalLocation` data to evaluate guesses in `GameService`
