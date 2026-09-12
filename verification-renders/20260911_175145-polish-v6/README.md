# Long-form edit v6

Editable overlays: `build_photos.py`, `build_motion_refined.py`.
Timing and captions: `photo-events.json`, `motion-events-refined.json`, `captions.json`; `prepare_assembly.py` combines the overlay authoring inputs into `events.json` and regenerates the final composition and assembly script.

The presenter, inserted promo, original voice, slow camera and relighting use the verified v5 `assets/timeline-base.mp4`. This avoids another source retime or unnecessary generation. v5 remains unchanged.

Eight photos are used exactly once. Visible attribution strips have been removed; source URLs and license evidence remain in `assets/photos/assets.json` and `assets/photos/LICENSE-EVIDENCE.md`. Photo rotations are fixed per event for reproducible rendering.

Eight diagrams visualize the supplied narration only; they are explanatory graphics, not screenshots of actual student results. No statistics or performance claims have been added. Graphic labels are short extracts or faithful nominal forms of the existing transcript.

Render the overlay compositions with HyperFrames to alpha MOV and WebM, then run `prepare_assembly.py`, `assemble.py`, `verify_v6.py`, and `verify_sync.py`. Inspect actual final-video overlay states and caption exceptions before delivery.
