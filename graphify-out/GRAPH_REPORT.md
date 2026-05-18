# Graph Report - foodie  (2026-05-18)

## Corpus Check
- 5 files · ~1,310,851 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 15 nodes · 18 edges · 3 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]

## God Nodes (most connected - your core abstractions)
1. `setFormat()` - 5 edges
2. `init()` - 3 edges
3. `renderSteps()` - 3 edges
4. `handleSelect()` - 3 edges
5. `updateNutrition()` - 3 edges
6. `addToCart()` - 3 edges
7. `renderFormatSelector()` - 2 edges
8. `showToast()` - 2 edges

## Surprising Connections (you probably didn't know these)
- `init()` --calls--> `setFormat()`  [EXTRACTED]
  assets\js\food-lab.js → assets\js\food-lab.js  _Bridges community 0 → community 1_
- `addToCart()` --calls--> `setFormat()`  [EXTRACTED]
  assets\js\food-lab.js → assets\js\food-lab.js  _Bridges community 1 → community 2_

## Communities

### Community 0 - "Community 0"
Cohesion: 0.5
Nodes (2): init(), renderFormatSelector()

### Community 1 - "Community 1"
Cohesion: 0.67
Nodes (4): handleSelect(), renderSteps(), setFormat(), updateNutrition()

### Community 2 - "Community 2"
Cohesion: 1.0
Nodes (2): addToCart(), showToast()

## Knowledge Gaps
- **Thin community `Community 0`** (5 nodes): `food-lab.js`, `createStep()`, `init()`, `renderFormatSelector()`, `updateCartUI()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 2`** (2 nodes): `addToCart()`, `showToast()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `setFormat()` connect `Community 1` to `Community 0`, `Community 2`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `init()` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `addToCart()` connect `Community 2` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._