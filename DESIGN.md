# Design tokens

## Colour
| Token | Value | Use |
|---|---|---|
| night | #0B0F19 | Background |
| panel | #111827 | Boxes and cards |
| accent | #FBBF24 | Connectors, headings, key outlines |
| ramp-1 | #F97316 | Foundations tier |
| ramp-2 | #F43F5E | Structures tier |
| ramp-3 | #7C3AED | Algorithms tier |
| text | #F9FAFB | Primary text |
| muted | #9CA3AF | Secondary text |

The ramp runs orange, rose, violet (Sunset).

## Type
1. Headings and labels: system UI (`system-ui, -apple-system, "Segoe UI", sans-serif`).
2. Code and complexity notes: monospace (`ui-monospace, Consolas, monospace`).

## Spacing and motion
1. Grid unit: 8 px. Box radius: 8 px. Stroke: 1.5 px, 2 px for accent.
2. Connectors are orthogonal. Only right angles.
3. Connectors animate with a dashed flow. Honour `prefers-reduced-motion` by turning the animation off.
