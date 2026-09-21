/* Supabase sync for Alfiery Workouts.
 *
 * Offline-first: localStorage stays the source of truth for the UI, and this
 * file reconciles it with the database whenever there's a connection. Logging a
 * set never waits on the network, so a gym basement with no signal behaves
 * exactly like being at home.
 *
 * Reconciliation is deliberately simple: push everything, pull everything,
 * last-write-wins per row id. At ~1,000 rows a year that is far cheaper than the
 * bug surface of incremental cursors.
 *
 * Exposes window.Sync.
 */

(function () {
  "use strict";

  const URL_KEY = "workouts.supabase.url";
  const KEY_KEY = "workouts.supabase.key";
  const LAST_SYNC_KEY = "workouts.sync.lastSyncedAt";
  const DIRTY_KEY = "workouts.sync.dirty";
  const TABLE = "entries";
  const PAGE = 1000; // Supabase caps a select at 1000 rows unless raised

  const store = {
    get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
    del: (k) => { try { localStorage.removeItem(k); } catch { /* ignore */ } },
  };

  let client = null;
  let session = null;
  let lastError = null;
  const listeners = new Set();

  /* ---------------------------------------------------------------- state */

  const state = {
    get configured() { return Boolean(config().url && config().key); },
    get email() { return session && session.user ? session.user.email : null; },
    get signedIn() { return Boolean(session && session.user); },
    get pending() { return store.get(DIRTY_KEY) === "1"; },
    get lastSyncedAt() { return store.get(LAST_SYNC_KEY); },
    get error() { return lastError; },
  };

  function emit() {
    for (const fn of listeners) {
      try { fn(state); } catch { /* a bad listener must not break sync */ }
    }
  }

  function config() {
    return { url: (store.get(URL_KEY) || "").trim(), key: (store.get(KEY_KEY) || "").trim() };
  }

  function saveConfig(url, key) {
    store.set(URL_KEY, (url || "").trim().replace(/\/+$/, ""));
    store.set(KEY_KEY, (key || "").trim());
    client = null; // force a rebuild against the new project
    session = null;
    connect();
    emit();
  }

  function markDirty() { store.set(DIRTY_KEY, "1"); emit(); }

  /* ---------------------------------------------------------------- client */

  function build() {
    const { url, key } = config();
    if (!url || !key) return null;
    if (typeof window.supabase === "undefined") {
      lastError = "Supabase library failed to load — reload the app.";
      return null;
    }
    try {
      // storageKey is pinned so switching projects can't pick up a stale session.
      return window.supabase.createClient(url, key, {
        auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, storageKey: "workouts.auth" },
      });
    } catch (err) {
      lastError = "Could not reach Supabase: " + (err && err.message ? err.message : String(err));
      return null;
    }
  }

  function connect() {
    client = build();
    if (!client) return null;

    // These only track the session. Kicking a sync from here would push an empty
    // row list (the app owns the rows), which would clear the dirty flag without
    // having uploaded anything — the app schedules the sync instead.
    client.auth.onAuthStateChange((_event, next) => {
      session = next;
      lastError = null;
      emit();
    });

    // Picks up an existing session, e.g. on return from a magic link.
    client.auth.getSession().then(({ data }) => {
      session = data ? data.session : null;
      emit();
    });

    return client;
  }

  /* ------------------------------------------------------------ conversion */

  function fromRemote(row) {
    return {
      id: row.id,
      date: row.date,
      exercise: row.exercise,
      weight: Number(row.weight_kg),
      reps: row.reps,
      sets: row.sets,
      notes: row.notes || "",
      deleted: Boolean(row.deleted),
      updatedAt: row.updated_at,
    };
  }

  function toRemote(row) {
    return {
      id: row.id,
      date: row.date,
      exercise: row.exercise,
      weight_kg: row.weight,
      reps: row.reps,
      sets: row.sets,
      notes: row.notes || "",
      deleted: Boolean(row.deleted),
      updated_at: row.updatedAt,
    };
  }

  const time = (v) => {
    const t = Date.parse(v);
    return Number.isFinite(t) ? t : 0;
  };

  /** Last-write-wins per id. Pure — exported so it can be tested directly. */
  function merge(local, remote) {
    const byId = new Map();
    for (const row of local) byId.set(row.id, row);

    let adopted = 0;
    for (const row of remote) {
      const incoming = fromRemote(row);
      const current = byId.get(incoming.id);
      if (!current) {
        byId.set(incoming.id, incoming);
        adopted++;
      } else if (time(incoming.updatedAt) > time(current.updatedAt)) {
        byId.set(incoming.id, incoming);
        adopted++;
      }
    }
    return { rows: [...byId.values()], adopted };
  }

  /* ---------------------------------------------------------------- network */

  async function pushAll(rows) {
    if (!rows.length) return 0;
    // Chunked so a large first sync doesn't become one enormous request.
    let sent = 0;
    for (let i = 0; i < rows.length; i += 500) {
      const chunk = rows.slice(i, i + 500).map(toRemote);
      const { error } = await client.from(TABLE).upsert(chunk, { onConflict: "id" });
      if (error) throw error;
      sent += chunk.length;
    }
    return sent;
  }

  async function pullAll() {
    const out = [];
    for (let from = 0; ; from += PAGE) {
      const { data, error } = await client
        .from(TABLE)
        .select("*")
        .order("updated_at", { ascending: true })
        .range(from, from + PAGE - 1);
      if (error) throw error;
      out.push(...data);
      if (data.length < PAGE) break;
    }
    return out;
  }

  /** Reconcile local rows with the database. Returns the merged row list. */
  async function sync(localRows) {
    if (!client) connect();
    if (!client) throw new Error("Not configured");
    if (!session) throw new Error("Not signed in");
    if (typeof navigator !== "undefined" && navigator.onLine === false) {
      throw new Error("Offline");
    }

    const rows = Array.isArray(localRows) ? localRows : [];
    try {
      const pushed = await pushAll(rows);
      const remote = await pullAll();
      const { rows: merged, adopted } = merge(rows, remote);

      store.set(LAST_SYNC_KEY, new Date().toISOString());
      store.del(DIRTY_KEY);
      lastError = null;
      emit();
      return { rows: merged, pushed, adopted, total: merged.length };
    } catch (err) {
      lastError = describe(err);
      emit();
      throw err;
    }
  }

  function describe(err) {
    if (!err) return "Unknown error";
    const parts = [err.message || String(err)];
    if (err.details) parts.push(err.details);
    if (err.hint) parts.push("hint: " + err.hint);
    if (err.code) parts.push("code " + err.code);
    return parts.filter(Boolean).join(" — ");
  }

  /* ------------------------------------------------------------------- auth */

  async function signIn(email) {
    if (!client) connect();
    if (!client) throw new Error("Add your project URL and key first");

    // Must be listed under Authentication → URL Configuration → Redirect URLs,
    // otherwise Supabase silently falls back to the project's Site URL.
    const emailRedirectTo = location.origin + location.pathname;
    const { error } = await client.auth.signInWithOtp({
      email,
      options: { emailRedirectTo, shouldCreateUser: true },
    });
    if (error) { lastError = describe(error); emit(); throw error; }
    lastError = null;
    emit();
  }

  async function signOut() {
    if (client) await client.auth.signOut({ scope: "local" });
    session = null;
    emit();
  }

  /** Cheap round-trip that proves URL, key, table and policies all line up. */
  async function testConnection() {
    try {
      if (!client) connect();
      if (!client) return { ok: false, error: "Add your project URL and key first" };
      const { error } = await client.from(TABLE).select("id").limit(1);
      if (error) return { ok: false, error: describe(error) };
      return { ok: true, signedIn: Boolean(session) };
    } catch (err) {
      return { ok: false, error: describe(err) };
    }
  }

  /* ------------------------------------------------------------------ export */

  window.Sync = {
    state,
    config,
    saveConfig,
    signIn,
    signOut,
    sync,
    testConnection,
    markDirty,
    onChange: (fn) => { listeners.add(fn); },
    // exposed for tests
    _merge: merge,
    _fromRemote: fromRemote,
    _toRemote: toRemote,
  };

  if (state.configured) connect();
})();
