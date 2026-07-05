# Brain Graph for Home Assistant

A live 3D force-directed graph visualization of your Home Assistant entities, devices, automations, and their connections — styled after the Brain knowledge graph.

## Features

- **3D Graph Visualization**: All HA entities, devices, areas, floors, and automations as an interactive 3D force-directed graph
- **Live Updates**: Real-time state changes and automation triggers visualized with glowing nodes
- **Data Flow Animation**: Particle streams flow along connections when automations trigger or services are called
- **Auto-Rotation**: The graph continuously rotates for an engaging visualization
- **Interactive**: Click entities to see details in HA's native More-Info dialog
- **Domain Filtering**: Show/hide entity types (lights, switches, sensors, etc.)

## Installation (HACS)

1. Add this repository to HACS as a custom repository
2. Click Install
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Integrations
5. Click "Create Automation" → Select "Brain Graph"
6. A new sidebar entry "Brain Graph" will appear

## Usage

Click on the "Brain Graph" icon in the Home Assistant sidebar to open the 3D visualization.

## License

MIT
