# Architecture — pq_brain_graph

## Overview

```
Home Assistant Instance
├── Custom Component: pq_brain_graph
│   ├── __init__.py
│   │   ├── async_setup_entry(): Register panel + static assets
│   │   └── _async_register_frontend(): Panel registration via panel_custom
│   ├── config_flow.py: Minimal (no config options)
│   ├── manifest.json: Dependencies = ["http", "frontend", "panel_custom"]
│   └── www/brain-graph-panel.js (1.3 MB minified bundle)
│
└── Frontend: brain-graph-panel.js (ES module)
    ├── BrainGraphPanel (HTMLElement)
    │   ├── Shadow DOM shell (CSS + HTML)
    │   ├── Graph instance (3d-force-graph)
    │   ├── HA WebSocket subscriptions
    │   └── Animation loop (requestAnimationFrame)
    │
    ├── State Management
    │   ├── _activeStates: Set<entity_id> — which entities are "on"
    │   ├── _recentlyChanged: Map<entity_id, expiresAt> — white flash effect (3s TTL)
    │   ├── _activeFlows: Map<linkId, {expiresAt, color}> — particle animation on flows
    │   └── _filterDomains: Set<domain> — which domains to display
    │
    ├── Graph Data Model
    │   ├── buildGraphData() — transforms HA registries into { nodes, links }
    │   ├── Nodes: 7 types (ha-core, floor, area, device, entity-domain, automation, script)
    │   └── Links: 3 types (contains, triggers, controls)
    │
    ├── Real-time Updates
    │   ├── subscribeMessage(state_changed) — node glow updates
    │   ├── subscribeMessage(automation_triggered) — flow particle animation
    │   └── subscribeMessage(call_service) — future: service-level flows
    │
    └── Visual Effects
        ├── Glow Animation (requestAnimationFrame loop)
        │   ├── ha-core: Golden pulse (Math.sin-based)
        │   ├── Active nodes: Colored pulse per entity type
        │   └── Recently-changed: White fade-out (linear)
        │
        ├── Particle Flow Animation (3d-force-graph built-in)
        │   ├── linkDirectionalParticles: 1 (ambient) → 6 (active flows)
        │   ├── linkDirectionalParticleSpeed: 0.004 (ambient) → 0.012 (active)
        │   ├── linkDirectionalParticleColor: Dimmed → Pink/Amber/Violet
        │   └── Sequencing: Trigger-edges immediately, Action-edges +800ms
        │
        └── Graph Layout
            ├── 3D Force-Directed Layout (D3-force simulation)
            ├── Link Distances: ha-core=180, floor=120, area=80, entity=40
            ├── Charge Strength: -120 (repulsion)
            └── Auto-Rotation: OrbitControls.autoRotate = true, speed = 0.4
```

---

## Data Flow — State Change Example

```
1. Light toggled in HA UI or via automation
2. HA core emits: event_type="state_changed", entity_id="light.kitchen", new_state="on"
3. BrainGraphPanel._onStateChanged(event) receives:
   ├── Add "light.kitchen" to _activeStates
   ├── Set _recentlyChanged["light.kitchen"] = now + 3000ms
   └── Call graph.nodeColor() to refresh colors
4. _updateGlows() next animation frame:
   ├── Find node id="light.kitchen" in _graphData.nodes
   ├── Get 3D coordinates via graph.graph2ScreenCoords(x, y, z)
   ├── Create CSS blur div in document.body at (screenX, screenY)
   ├── Background = "rgba(251,191,36,opacity)" (amber from NODE_COLORS.light)
   └── Filter = "blur(22px)" (size * 0.55)
5. Glow pulses for 3s, then fades via requestAnimationFrame
6. After 3s: _recentlyChanged.get("light.kitchen") expires
   ├── _updateGlows() removes the div from DOM
   └── Node reverts to base NODE_COLORS.light color
```

---

## Data Flow — Automation Trigger Example

```
1. Binary sensor triggers:
   - event: state_changed, entity_id="binary_sensor.door", state="on"
   → Same as above (node glows)

2. Automation executes:
   - event: automation_triggered, entity_id="automation.door_light"
   → BrainGraphPanel._onAutomationTriggered(event) receives

3. Parse automation trigger/action links:
   - Find all links: source=entity_id, target="automation.door_light", rel_type="triggers"
   - Find all links: source="automation.door_light", target=*, rel_type="controls"
   → Activate Trigger-Edges immediately:
     _activeFlows.set("binary_sensor.door→automation.door_light", {
       expiresAt: now + 3000,
       color: "rgba(244,114,182,0.9)" // pink
     })

4. After 800ms delay:
   → Activate Action-Edges:
     _activeFlows.set("automation.door_light→light.kitchen", {
       expiresAt: now + 3800,
       color: "rgba(251,191,36,0.9)" // amber
     })

5. Animation loop (every frame):
   - linkDirectionalParticles():
     - If flow.expiresAt > now: return 6 (show particles)
     - Else: return 1 (ambient)
   - linkDirectionalParticleSpeed():
     - If flow.expiresAt > now: return 0.012 (fast)
     - Else: return 0.004 (slow)
   - linkDirectionalParticleColor():
     - If flow exists & not expired: return flow.color
     - Else: return 'rgba(100,130,180,0.4)' (dimmed blue)

6. Visually: 6 pink particles rush down "door→automation" edge,
   pause 800ms, then 6 amber particles rush down "automation→light" edge.
   Both disappear after 3-4 seconds.
```

---

## Build & Deployment

### Development Loop

```bash
# Edit source
nano ha-widgets/pq_brain_graph_panel/src/brain-graph-panel.js

# Rebuild
cd ha-widgets && node build-brain-graph.mjs

# Copy to integration
cp pq_brain_graph_panel/dist/brain-graph-panel.js \
   ../ha-brain-graph/custom_components/pq_brain_graph/www/

# Test in HA
# → Settings → System → Restart → Clear browser cache → Reload panel
```

### Bundle Contents

- **3d-force-graph**: Force-directed graph layout engine (Three.js-based)
- **Three.js**: 3D rendering library (minimal WebGL canvas)
- **D3-force**: Physics simulation for node repulsion/link attraction
- **Custom Code**: BrainGraphPanel class, glow overlays, subscriptions (~100 KB source → ~50 KB minified)

Total: ~1.3 MB minified.

---

## Key Decisions

1. **3D vs 2D**: 3D chosen for visual impact. 2D would be ~150 KB but less engaging.
2. **Glow Overlays**: CSS blur divs in document.body (not in shadow DOM) for viewport-relative positioning. Z-index=3 to stay below HA modals.
3. **Particle Flow**: Driven by `linkDirectionalParticles` callback (dynamic per frame) not by separate animation. Leverages 3d-force-graph's built-in particle engine.
4. **Sequencing**: Automation flows delayed 800ms between trigger→action to show causal sequence.
5. **Auto-Rotation**: Keeps the graph engaging even when idle (OrbitControls.autoRotate = true).

---

## Future Enhancements

1. **2D/3D Toggle**: Lazy-load force-graph (2D) if user toggles off 3D
2. **Script Flows**: Parse script configs same as automations
3. **Scene Flows**: Parse scene activation chains
4. **Search**: Filter graph by entity name / state / tag
5. **Persistence**: Save graph layout to browser localStorage
6. **Performance**: Virtual node rendering for 500+ entities (not all visible)
7. **Context Menu**: Right-click on node → toggle automation, call service, etc.
