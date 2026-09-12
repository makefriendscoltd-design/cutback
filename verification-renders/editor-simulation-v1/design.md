# Editor simulation design

1920×1080 dark desktop NLE modeled on the density and restraint of current consumer/pro editors. The interface uses flat charcoal layers (`#151618`, `#191a1c`, `#202124`), thin `#303236` dividers, cool gray type, blue video clips, and teal audio waveforms. The project title is `aixscool_컷편집`; the only simulation disclosure is the small top-right `2× · 편집 과정 재현` badge.

The layout is fixed: 350px media bin at left, 960×540 program monitor in the center, 286px inspector at right, and a timeline below y=668. Timeline content begins at x=220 and maps the 24-second source interval 28:00–52:00 at exactly 60px per second.

Every silence edit is represented in both linked tracks. Cut boundaries appear only after blade clicks. Selected silence receives a restrained red tint. Ripple delete fades that exact span and translates all later source segments by the measured gap width, with a brief magnetic snap guide at the join. The final seam interaction offsets only the audio segment briefly, then snaps it back to its linked video position before adding a short fade curve.

Motion is functional: cursor travel, click rings, razor pointer, cut lines, linked selections, measured ripple closures, trim handles, snap guides, transport state, playhead motion, and audio meters. There are no promotional cards, large captions, glow effects, or invented editor branding.
