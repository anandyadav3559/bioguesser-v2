-- =============================================================
-- pg_cron: Delete temporary (guest) users inactive for 2+ hours
-- =============================================================
-- Prerequisites:
--   1. pg_cron extension must be enabled in postgresql.conf:
--        shared_preload_libraries = 'pg_cron'
--   2. Run this ONCE as a superuser (or an admin with cron privilege):
--        CREATE EXTENSION IF NOT EXISTS pg_cron;
--
-- Schema cascade order (all have ON DELETE CASCADE or are handled below):
--   users (is_guest=True, last_active_at < now()-2h)
--     └── user_profiles       (CASCADE via OneToOne)
--     └── players             (CASCADE via FK)
--         └── guesses         (CASCADE via FK)
--     └── rooms (host → SET NULL; but single-player rooms must be purged)
--         └── rounds          (CASCADE via FK)
--         └── multiplayer_games (CASCADE via FK → Room)
-- =============================================================

-- Step 1: Create a stored procedure that does the cleanup
CREATE OR REPLACE PROCEDURE cleanup_expired_guests()
LANGUAGE plpgsql
AS $$
DECLARE
    affected_rooms UUID[];
    v_stale_guest_ids UUID[];
BEGIN
    -- ----------------------------------------------------------------
    -- 1. Collect stale guest user IDs (inactive > 2 hours)
    -- ----------------------------------------------------------------
    SELECT ARRAY_AGG(user_id)
    INTO v_stale_guest_ids
    FROM users
    WHERE is_guest = TRUE
      AND last_active_at < NOW() - INTERVAL '2 hours';

    -- Nothing to do?
    IF v_stale_guest_ids IS NULL OR ARRAY_LENGTH(v_stale_guest_ids, 1) = 0 THEN
        RAISE NOTICE 'cleanup_expired_guests: no stale guests found.';
        RETURN;
    END IF;

    RAISE NOTICE 'cleanup_expired_guests: found % stale guest(s).', ARRAY_LENGTH(v_stale_guest_ids, 1);

    -- ----------------------------------------------------------------
    -- 2. Purge rooms that should be deleted outright:
    --    A room is safe to delete when ALL of its permanent (non-guest)
    --    players are NOT present — i.e. the only players are from our
    --    stale guest set.
    -- ----------------------------------------------------------------
    SELECT ARRAY_AGG(DISTINCT p.room_id)
    INTO affected_rooms
    FROM players p
    WHERE p.user_id = ANY(v_stale_guest_ids);

    IF affected_rooms IS NOT NULL THEN
        -- Delete rooms where no permanent player exists outside the stale set
        DELETE FROM rooms r
        WHERE r.id = ANY(affected_rooms)
          AND NOT EXISTS (
              SELECT 1
              FROM players p2
              WHERE p2.room_id = r.id
                AND p2.user_id <> ALL(v_stale_guest_ids)
                AND EXISTS (
                    SELECT 1 FROM users u2
                    WHERE u2.user_id = p2.user_id
                      AND u2.is_guest = FALSE
                )
          );
        -- Rounds, guesses, multiplayer_games cascade automatically.

        -- For rooms that still survive (have permanent players),
        -- just orphan the host reference if the host is a stale guest.
        UPDATE rooms
        SET host_id = NULL
        WHERE host_id = ANY(v_stale_guest_ids);
    END IF;

    -- ----------------------------------------------------------------
    -- 3. Delete the stale guest users.
    --    Cascades automatically delete:
    --      • user_profiles  (OneToOneField CASCADE)
    --      • players        (ForeignKey CASCADE)  → guesses cascade from there
    -- ----------------------------------------------------------------
    DELETE FROM users
    WHERE user_id = ANY(v_stale_guest_ids);

    RAISE NOTICE 'cleanup_expired_guests: deleted % guest user(s) and related data.', ARRAY_LENGTH(v_stale_guest_ids, 1);
END;
$$;


-- =============================================================
-- Step 2: Schedule the procedure with pg_cron
--         Runs every 30 minutes (adjust as needed).
--         Cron syntax: minute hour dom month dow
-- =============================================================

-- Remove any existing job with the same name first (idempotent re-runs)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'cleanup_expired_guests') THEN
        PERFORM cron.unschedule('cleanup_expired_guests');
    END IF;
END;
$$;

SELECT cron.schedule(
    'cleanup_expired_guests',          -- job name
    '*/30 * * * *',                    -- every 30 minutes
    'CALL cleanup_expired_guests();'
);

-- =============================================================
-- Verification queries (run manually to confirm)
-- =============================================================

-- Check registered jobs:
-- SELECT * FROM cron.job;

-- Check recent execution history:
-- SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 10;

-- Preview which guests would be deleted right now:
-- SELECT user_id, username, last_active_at
-- FROM users
-- WHERE is_guest = TRUE
--   AND last_active_at < NOW() - INTERVAL '2 hours';
