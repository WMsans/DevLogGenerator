## Updates

(emotion: confused)  
Merging the 'fix/steaming' branch introduced a major refactor to how the terrain editor handles brush interactions. The code now uses a hitVolume to determine if we're editing world terrain or debris objects, which prevents accidental edits to the wrong areas. This change adds a broad-phase filtering step to efficiently find all intersecting volumes, ensuring seamless chunk boundary edits without performance hits.  

(emotion: happy)  
The key innovation is using a List to collect intersecting volumes and applying the brush iteratively—this makes the system more robust, especially for large brushes. By separating world vs debris logic, we avoid unintended terrain modifications. The structural analyzer now uses the hitVolume instead of the original targetVolume, which aligns with the context-aware logic.  

(emotion: confused)  
The addition of `System.Collections.Generic` was a subtle but necessary fix—without it, the List<VoxelVolume> would throw errors. This change highlights how even small code tweaks can unlock more flexible, context-aware tools. The refactored code feels more maintainable, and the step-by-step volume filtering makes the editor's behavior clearer to debug.  

(emotion: look_right_up)  
This merge resolved a long-standing issue where debris objects could accidentally alter terrain. By making the editor "smart" about its context, we’ve improved both stability and user control. The code now balances precision with performance, and the step-by-step approach makes it easier to extend later—like adding support for custom volume types.

(emotion: happy)
- Fixed oak tree brick smoothness
