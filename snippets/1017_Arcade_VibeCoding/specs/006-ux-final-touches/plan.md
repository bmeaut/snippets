# Implementation Plan: UX Végső Simítások

**Branch**: `006-ux-final-touches` | **Date**: 2026-06-02 | **Spec**: [spec.md](./spec.md)

## Summary

Négy független, kis terjedelmű változtatás: (1) Snake gép arrébb tolása, (2) [E] prompt Y-pozíció bugfix, (3) gépfeliratok a canvas-on, (4) amőba difficulty screen redesign.

## Technical Context

**Language/Version**: TypeScript 5.x strict, React 18  
**Graphics**: HTML5 Canvas (hub), CSS (amőba screen)  
**Érintett fájlok**:
- `src/hub/entities/machine.ts` — Snake x koordináta
- `src/hub/systems/interaction.ts` — prompt pozíció korrekció + gép-specifikus szöveg
- `src/hub/scene/HubScene.tsx` — stageHeight átadása az interaction rendszernek
- `src/hub/rendering/drawHub.ts` — gépfeliratok kirajzolása
- `src/games/ameoba/AmoebaGame.tsx` — difficulty section stílus
- `src/games/ameoba/AmoebaGame.css` — difficulty section CSS

## Constitution Check

- ✅ Modul izoláció megmarad: csak hub és ameoba érintett
- ✅ TypeScript strict: nincs `any` bevezetés
- ✅ Nincs változás a `GameModuleContract`-ban

## Phases

### Phase 1 — Snake gép pozíció fix + gépfeliratok
`machine.ts`: `createSnakeMachine` x koordinátája `728 → 520`.  
`drawHub.ts`: minden gép alá (machine alján kívül, ~14px-rel) kis felirat kerül a `kind` alapján:
- `snake` → "SNAKE"
- `amoba` → "AMŐBA"  
- `door` → "KASZINÓ"

Betűstílus: kis méret (10–11px scaled), nagy betű, halványan látható (nem zajos).

### Phase 2 — [E] prompt Y-pozíció bugfix
**Probléma**: `hub-stage` `place-items: center` → canvas vertikálisan centrizálva. A `screenY = machine.y * scale` a canvas tetejétől méri a távolságot, de a prompt a stage tetejétől pozícionálódik.

**Megoldás**:
1. `HubScene.tsx`: a `useHubResize` hook visszaadja a `width/height/scale`-t. Az `stageHeight` a `stageRef.current.clientHeight`. A canvas magassága `viewport.height`. Az offset: `canvasOffsetY = (stageHeight - viewport.height) / 2`.
2. `createInteractionPrompt` kap egy `canvasOffsetY: number` paramétert és hozzáadja `screenY`-hoz.

### Phase 3 — Gép-specifikus prompt szöveg
`interaction.ts`: `createInteractionPrompt`-ban a `text` mező a `machine.kind` alapján:
- `amoba` → `"[E] Amőba indítása"`
- `snake` → `"[E] Snake indítása"`
- `door` → `"[E] Belépés a kaszinóba"`

### Phase 4 — Amőba difficulty screen redesign
`AmoebaGame.css`: új `.ameoba-difficulty` osztályok:
- Háttér: sötét panel, enyhe rácsháttér (CSS `repeating-linear-gradient` vagy `background-image` SVG-inline rács)
- Sarokban vagy fejlécben kis X/O motívum (CSS pseudo-element vagy inline SVG szöveg)
- Három gomb: a meglévő `primary-button` stílus megtartva, de az amőba palettába illeszkedő hover

`AmoebaGame.tsx`: a difficulty section div-je kapja az új CSS osztályokat.

## Deliverables

```text
src/hub/entities/machine.ts           # Snake x: 728 → 520
src/hub/systems/interaction.ts        # canvasOffsetY param + gép-specifikus szöveg  
src/hub/scene/HubScene.tsx            # canvasOffsetY számítás, átadás
src/hub/rendering/drawHub.ts          # gépfeliratok
src/games/ameoba/AmoebaGame.tsx       # difficulty section új osztályok
src/games/ameoba/AmoebaGame.css       # .ameoba-difficulty stílusok
```

## Risks & Mitigations

- **canvasOffsetY 0 ha teljes képernyő**: Ha `stageHeight == viewport.height`, offset = 0, prompt pozíció változatlan. ✓
- **Felirat átfedés géppel**: A felirat a gép ALATT jelenik meg (machine.y + machine.height + gap), így nem takarja a képernyőt.
- **Casino scene**: A casino scene saját `InteractionPrompt`-ot használ, de `createInteractionPrompt` ugyanonnan importál — a casino exitdoor szövegét is frissíteni kell ("[E] Vissza a hubba").
