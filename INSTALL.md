# Installation & Testing Guide — Brain Graph

## Quick Install

1. **Copy to HA config directory:**
   ```bash
   cp -r /home/philipp/ha-brain-graph/custom_components/pq_brain_graph \
         <your-ha-config>/custom_components/
   ```

2. **Restart Home Assistant:**
   - Settings → System → Restart

3. **Add Integration:**
   - Settings → Devices & Services → Integrations
   - Click "Create Automation" button (or search "Brain Graph")
   - Select "Brain Graph"
   - Click Submit

4. **Open the Panel:**
   - A new sidebar entry "Brain Graph" (icon: `mdi:graph-outline`) appears
   - Click to open the 3D visualization

## What You Should See

### On First Load
- 3D graph slowly rotating (OrbitControls autoRotate)
- Orange central node labeled "Home Assistant" — pulsing golden glow
- Hierarchical layers: Floors → Areas → Devices → Entities
- Colored node particles flowing along edges (1 per link, slow ambient flow)

### Interactive Testing

**Test 1: Turn on a light**
- Click a light entity's switch in HA
- In the Brain Graph panel, watch the light node:
  - Flash white briefly (state_changed event)
  - Amber glow appears and pulses

**Test 2: Open a door/motion sensor**
- Trigger a binary sensor (door open, motion detected)
- Watch the sensor node flash white and glow in sensor color

**Test 3: Trigger an Automation**
- Create a simple automation or trigger one manually
- Pink particle stream flows: Trigger-Entity → Automation node (immediately)
- After 800ms, amber particle stream flows: Automation → Target-Entity
- Both flows last ~3-4 seconds, then fade

**Test 4: Filter by Domain**
- Click "Lights" chip at top-left
- Only light nodes appear in full color; all others dim to ~20% opacity
- Click "All" to reset

**Test 5: Click Entity**
- Click on any entity node
- HA's native More-Info dialog pops up
- Close it and the panel remains

**Test 6: Click Device/Area/Floor**
- Click on a Device/Area/Floor node
- Info panel slides in from right with node details
- Click ✕ to close

## Browser Console Debugging

```js
// In browser's Developer Tools (F12):
// Check if the panel is mounted
document.querySelector('brain-graph-panel')

// Check active flows
document.querySelector('brain-graph-panel')._activeFlows

// Check active states (glowing nodes)
document.querySelector('brain-graph-panel')._activeStates

// Force re-render
document.querySelector('brain-graph-panel')._graph.graphData(
  document.querySelector('brain-graph-panel')._graphData
)
```

## Troubleshooting

### Panel doesn't appear in sidebar
- Check browser console for JS errors (F12)
- Verify HA config directory has `custom_components/pq_brain_graph/`
- Clear HA frontend cache: Developer Tools → Restart → Frontend
- Hard-refresh browser (Ctrl+Shift+R on most browsers)

### Graph is blank/all white
- Check HA WebSocket connection: Settings → Automations (should list automations)
- Verify entity registry has entities: Developer Tools → States
- Check browser console for `callWS` errors

### Flows don't animate
- Trigger an automation manually: Developer Tools → Automations → Test
- Check browser console for `_onAutomationTriggered` errors
- Verify automation has valid entity_id in trigger/action

### Performance is slow
- Disable particle flow during testing (comment out `_subscribeAutomationTriggered()` in `_init()`)
- Reduce number of entities by using domain filter
- Check: Glow overlays limit is ~50 simultaneous glows; if you have 500+ active lights, performance will degrade

## Build & Rebundle

After editing `pq_brain_graph_panel/src/brain-graph-panel.js`:

```bash
cd /home/philipp/ha-widgets
node build-brain-graph.mjs
cp pq_brain_graph_panel/dist/brain-graph-panel.js \
   /home/philipp/ha-brain-graph/custom_components/pq_brain_graph/www/
```

Then in HA: Settings → System → Restart.

## File Sizes

- `brain-graph-panel.js` (bundled, minified): ~1.3 MB
  - 3d-force-graph: ~400 KB
  - Three.js: ~350 KB
  - D3-force: ~50 KB
  - Custom code: ~100 KB

Load time on local network: <2 seconds over HTTP.
