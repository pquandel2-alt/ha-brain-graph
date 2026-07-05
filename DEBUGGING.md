# Debugging Guide — Brain Graph

Wenn die Graph-Seite leer/schwarz ist, folge diesem Guide.

## Step 1: Browser Console öffnen

Öffne den Browser Developer Tools:
- **Chrome/Edge**: `F12` oder `Ctrl+Shift+I`
- **Firefox**: `F12` oder `Ctrl+Shift+K`
- **Safari**: Enable via Settings → Advanced → "Show Develop menu", dann `Cmd+Option+I`

Klicke auf den **Console** Tab.

---

## Step 2: Auf Fehler prüfen

Suche nach roten Fehlern oder Warnungen. Typische Fehler:

### Fehler: "ForceGraph3D is not a function"
- Die 3d-force-graph Bibliothek wurde nicht geladen
- **Lösung**: Hard-Refresh: `Ctrl+Shift+R` (Chrome/Edge) oder `Cmd+Shift+R` (Mac)

### Fehler: "Cannot read property 'callWS' of null"
- Der `hass` Objekt ist nicht gesetzt
- **Lösung**: Panel wird von HA nicht korrekt initialisiert — Integration neu installieren

### Fehler: "ReferenceError: document is undefined"
- Code läuft in falschen Kontext
- **Lösung**: Sollte nicht passieren — melde Issue auf GitHub

---

## Step 3: Debug Logs prüfen

Wenn keine Fehler, suche nach `[BrainGraphPanel]` Logs:

```
[BrainGraphPanel] Initializing...
[BrainGraphPanel] Loading HA registries...
[BrainGraphPanel] Registries loaded: 150 states, 42 devices, 8 areas, 2 floors, 150 entities, 12 automations
[BrainGraphPanel] Graph data built: 217 nodes, 250 links
[BrainGraphPanel] Graph instance created
[BrainGraphPanel] Graph data set
[BrainGraphPanel] Event subscriptions active
[BrainGraphPanel] Animation loop started ✓
```

**Wenn alle Logs da sind aber Graph trotzdem blank:**
- Container-Größe wird nicht korrekt berechnet
- Three.js WebGL-Kontext konnte nicht initialisiert werden
- GPU/Browser-Kompatibilitätsproblem

---

## Step 4: Container-Größe prüfen

Gib in die Browser Console ein:

```js
const panel = document.querySelector('brain-graph-panel');
const container = panel.shadowRoot.getElementById('graph-container');
console.log('Container width:', container.clientWidth);
console.log('Container height:', container.clientHeight);
console.log('Graph instance:', panel._graph);
```

**Erwartet:**
- `Container width: 1920` (oder deine Bildschirmbreite)
- `Container height: 1080` (oder deine Bildschirmhöhe)
- `Graph instance: [Object]` (sollte nicht null sein)

**Wenn width/height = 0:**
- CSS Sizing-Problem
- **Lösung**: Cache leeren + Hard-Refresh

---

## Step 5: WebSocket Connection prüfen

Gib ein:

```js
const panel = document.querySelector('brain-graph-panel');
console.log('HASS connection:', panel._hass.connection);
```

Sollte ein WebSocket-Objekt ausgeben, nicht null.

---

## Step 6: Graph-Daten prüfen

```js
const panel = document.querySelector('brain-graph-panel');
console.log('Graph data nodes:', panel._graphData.nodes.length);
console.log('Graph data links:', panel._graphData.links.length);
console.log('Sample nodes:', panel._graphData.nodes.slice(0, 5));
```

**Erwartet:**
- `nodes.length: > 20` (mindestens HA Core + einige Entitäten)
- `links.length: > 20`
- Sample nodes zeigt z.B. `{id: 'ha-core', label: 'Home Assistant', ...}`

---

## Step 7: GPU/Renderer Status prüfen

```js
const panel = document.querySelector('brain-graph-panel');
if (panel._graph && panel._graph.renderer) {
  const renderer = panel._graph.renderer();
  console.log('Renderer:', renderer);
  console.log('WebGL supported:', !!window.WebGLRenderingContext);
}
```

Wenn `WebGL supported: false`, dein Browser unterstützt WebGL nicht.

---

## Common Issues & Fixes

### Issue: "Graph is completely black but container has correct size"

**Cause**: Three.js hat einen leeren Scene/keine Nodes
**Fix**: 
1. Check Step 6 (Graph-Daten)
2. Wenn `nodes.length: 0`, versuche Settings → Automations um sicherzustellen, dass HA reaktionsfähig ist
3. Restart HA

### Issue: "Only filter chips and legend visible, no graph"

**Cause**: Graph wird in Shadow DOM nicht gerendert
**Fix**:
1. `Ctrl+Shift+R` (Hard-Refresh) im Browser
2. HA Frontend Cache leeren: Hamburger Menu → Settings → Developer Tools → Storage → Clear all cookies/cache
3. Browser-Cache leeren

### Issue: "Error: WebGL context lost"

**Cause**: GPU/Browser-Problem (zu viele WebGL-Kontexte)
**Fix**:
- Schließe andere WebGL-Anwendungen (YouTube 3D, etc.)
- Reduziere Entitätsanzahl via Filter
- Nutze 2D-Version wenn verfügbar (kommende Version)

### Issue: "Crash nach 30 Sekunden"

**Cause**: Memory-Leak in Animation Loop
**Fix**:
- Überprüfe Anzahl der Glow-Overlays: 
  ```js
  console.log('Glow overlays:', document.querySelector('brain-graph-panel')._glowOverlays.size)
  ```
- Sollte < 50 sein. Wenn größer, ist es ein Speicherleck.
- Melde Issue mit Details auf GitHub

---

## Weitere Hilfe

Wenn keiner der oben genannten Punkte hilft:

1. **Öffne GitHub Issue**: https://github.com/pquandel2-alt/ha-brain-graph/issues
2. **Kopiere Browser Console Output** (rechts oben Screenshot-Icon)
3. **Gib folgende Info an**:
   - HA-Version (Settings → About)
   - Browser + Version
   - Anzahl der Entitäten (Developer Tools → States → Count)
   - GPU-Modell (task manager / system info)

---

## Remote Debugging (via SSH)

Wenn du HA remote laufen hast:

```bash
# SSH zu HA-Server
ssh user@ha-ip

# Prüfe HA Logs auf Fehler
journalctl -u homeassistant -f

# oder wenn Docker:
docker logs homeassistant -f --tail 50
```

Suche nach `pq_brain_graph` oder `panel_custom` Fehlern.
