"""
Admin FastAPI server for the animal staging review panel.
Run: uvicorn server:app --port 8001 --reload
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from admin.db import get_conn

app = FastAPI(title="BioGuesser Admin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def row_to_dict(cursor, row):
    return {cursor.description[i].name: row[i] for i in range(len(row))}

def _approve_single_animal(cur, animal_id: str):
    """
    Core logic to promote a single staging animal to the main tables.
    Requires an active cursor `cur`.
    """
    cur.execute("SELECT * FROM staging_animals WHERE id = %s", (animal_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, f"Animal {animal_id} not found in staging")
    sa = row_to_dict(cur, row)

    if sa["status"] == "approved":
        return sa  # Already approved, silently skip

    # Insert into main animals (upsert on scientific_name)
    cur.execute(
        """
        INSERT INTO animals (id, name, scientific_name, image_url, max_probability, entropy, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (scientific_name) DO UPDATE
            SET image_url = EXCLUDED.image_url,
                max_probability = EXCLUDED.max_probability,
                entropy = EXCLUDED.entropy
        RETURNING id
        """,
        (
            sa["id"], sa["name"], sa["scientific_name"],
            sa["image_url"], sa["max_probability"],
            sa["entropy"], sa["created_at"]
        )
    )
    main_id = cur.fetchone()[0]

    # Copy characteristics
    cur.execute(
        "SELECT * FROM staging_animal_characteristics WHERE animal_id = %s",
        (animal_id,)
    )
    chars_row = cur.fetchone()
    if chars_row:
        chars = row_to_dict(cur, chars_row)
        cur.execute(
            """
            INSERT INTO animal_characteristics (
                animal_id, prey, gestation_period, habitat, predators,
                average_litter_size, top_speed, lifespan, weight, length,
                skin_type, color, age_of_sexual_maturity, age_of_weaning
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
            """,
            (
                main_id,
                chars.get("prey"), chars.get("gestation_period"),
                chars.get("habitat"), chars.get("predators"),
                chars.get("average_litter_size"), chars.get("top_speed"),
                chars.get("lifespan"), chars.get("weight"),
                chars.get("length"), chars.get("skin_type"),
                chars.get("color"), chars.get("age_of_sexual_maturity"),
                chars.get("age_of_weaning"),
            )
        )

    # Copy locations
    cur.execute(
        "SELECT h3_index, latitude, longitude, count FROM staging_animal_locations WHERE animal_id = %s",
        (animal_id,)
    )
    for loc in cur.fetchall():
        cur.execute(
            """
            INSERT INTO animal_locations (animal_id, h3_index, latitude, longitude, count)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (main_id, loc[0], loc[1], loc[2], loc[3])
        )

    # Mark staging row as approved
    cur.execute(
        "UPDATE staging_animals SET status = 'approved' WHERE id = %s",
        (animal_id,)
    )
    return sa

# ── Routes ───────────────────────────────────────────────────────────────────
from pydantic import BaseModel
from typing import List

class BatchRequest(BaseModel):
    animal_ids: List[str]

@app.get("/animals")
def list_animals(status: str = "pending"):
    """List staging animals filtered by status (pending | approved | rejected)."""
    valid = {"pending", "approved", "rejected"}
    if status not in valid:
        raise HTTPException(400, f"status must be one of {valid}")

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Auto-cleanup data older than 2 days
            cur.execute("DELETE FROM staging_animals WHERE created_at < NOW() - INTERVAL '2 days'")
            
            cur.execute(
                """
                SELECT id, name, scientific_name, image_url,
                       max_probability, entropy, status, created_at
                FROM staging_animals
                WHERE status = %s
                ORDER BY created_at DESC
                """,
                (status,)
            )
            rows = cur.fetchall()
            result = [row_to_dict(cur, r) for r in rows]
        conn.commit()
    return result


@app.get("/animals/{animal_id}")
def get_animal(animal_id: str):
    """Full detail: animal + characteristics + locations."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Animal
            cur.execute(
                "SELECT * FROM staging_animals WHERE id = %s", (animal_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "Animal not found in staging")
            animal = row_to_dict(cur, row)

            # Characteristics
            cur.execute(
                "SELECT * FROM staging_animal_characteristics WHERE animal_id = %s",
                (animal_id,)
            )
            chars = cur.fetchone()
            animal["characteristics"] = row_to_dict(cur, chars) if chars else {}

            # Locations
            cur.execute(
                """SELECT h3_index, latitude, longitude, count
                   FROM staging_animal_locations WHERE animal_id = %s""",
                (animal_id,)
            )
            animal["locations"] = [row_to_dict(cur, r) for r in cur.fetchall()]

    return animal


@app.post("/animals/{animal_id}/approve")
def approve_animal(animal_id: str):
    """Promotes a single staging animal into the main tables."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            sa = _approve_single_animal(cur, animal_id)
        conn.commit()
    return {"message": f"Animal '{sa['name']}' approved."}


@app.post("/animals/batch-approve")
def batch_approve_animals(req: BatchRequest):
    """Promotes multiple staging animals."""
    approved_names = []
    with get_conn() as conn:
        with conn.cursor() as cur:
            for aid in req.animal_ids:
                sa = _approve_single_animal(cur, aid)
                approved_names.append(sa["name"])
        conn.commit()
    return {"message": f"Approved {len(approved_names)} animals successfully."}


@app.post("/animals/{animal_id}/reject")
def reject_animal(animal_id: str):
    """Marks staging animal as rejected (stays in staging, excluded from game)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE staging_animals SET status = 'rejected' WHERE id = %s RETURNING id",
                (animal_id,)
            )
            if not cur.fetchone():
                raise HTTPException(404, "Animal not found in staging")
        conn.commit()
    return {"message": "Animal rejected."}


@app.post("/animals/batch-reject")
def batch_reject_animals(req: BatchRequest):
    """Marks multiple staging animals as rejected."""
    if not req.animal_ids:
        return {"message": "No animals selected."}
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE staging_animals SET status = 'rejected' WHERE id = ANY(%s)",
                (req.animal_ids,)
            )
            count = cur.rowcount
        conn.commit()
    return {"message": f"Rejected {count} animals."}


@app.delete("/animals/{animal_id}")
def delete_animal(animal_id: str):
    """Hard-delete animal from staging (cascades to locations + characteristics)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM staging_animals WHERE id = %s RETURNING id",
                (animal_id,)
            )
            if not cur.fetchone():
                raise HTTPException(404, "Animal not found in staging")
        conn.commit()
    return {"message": "Animal deleted from staging."}
