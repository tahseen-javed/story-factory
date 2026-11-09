TITLE: 3 Buttons, 4 Minutes of Air. The Clean One Is a Trap
LENGTH_MIN: 1
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=plum, hair=short, skin=tan)
- hale = rig_hero(outfit=teal, hair=bun, age=old, skin=light)
LOCATIONS:
- elevator: small old apartment elevator cabin interior, dim warm ceiling light, brushed metal walls, closed sliding doors, a wall panel with three big round buttons, wooden handrail
- lobby: bright apartment building hallway with an open elevator door, fresh daylight from a tall window, potted plant, tiled floor, wooden doors
MUSIC_MOODS:
- CH1: calm

## CH1 | FOUR MINUTES OF AIR
// TEST VIDEO (owner-approved exception to the 4-minute format). Narration is the owner's script, word for word.
// ACT hook
@ elevator.night | hero:stand/worried | ov:elevator_panel("all") | fr:wide | sfx:ticking_clock | track:{air:"4:00"}
You have three buttons and four minutes of air. One was never pressed.
@ elevator.night | hero:back_away/scared | hale:stand/worried | fr:ots | fx:flicker | sfx:impact,rustle | track:{air:"4:00"}
The elevator jolts between floors. "They taped eight last week," whispers Mrs. Hale, your neighbour.
@ elevator.night | hero:stand/worried | ov:elevator_panel("red") | fr:wide | sfx:ticking_clock | track:{air:"3:00"}
Three minutes of air. The red button is spotless.
@ elevator.night | hero:stand/worried | ov:elevator_panel("seven") | fr:wide | sfx:click | track:{air:"3:00"}
Seven is worn smooth.
@ elevator.night | hero:stand/scared | hale:stand/worried | ov:elevator_panel("eight") | fr:wide | sfx:rustle | track:{air:"3:00"}
Eight hides under fresh tape.
@ elevator.night | hero:stand/worried | hale:stand/worried | ov:option_cards("red","seven","eight") | fr:ots | sfx:click | track:{air:"3:00"}
Freeze. Option one, red. Option two, seven. Option three, eight.
@ elevator.night | hero:stand/worried | hale:stand/worried | ov:option_cards("red","seven","eight") | fr:wide | sfx:click | track:{air:"3:00"}
Pause the video. Decide now.
@ elevator.night | hero:stand/scared | hale:stand/worried | ov:option_cards("red","seven","eight") | fr:wide | track:{air:"3:00"}
Your clock keeps running.
// HOLD decision 4.5
// ACT resolution
@ elevator.night | hero:reach/determined | ov:elevator_panel("seven","pressed") | fr:wide | sfx:click | track:{air:"2:54"}
You press seven.
@ lobby.day | hero:stand/relieved | hale:stand/relieved | fr:medium | sfx:ding,door_creak | track:{air:"2:50"}
Doors open. Fresh air.
@ insert.night | ov:loose_cable("red","NEVER WIRED") | sfx:spark | track:{air:"2:50"}
Red was spotless because it was never wired.
@ lobby.day | hero:stand/relieved | hale:stand/relieved | fr:wide | track:{air:"2:50"}
The cleanest button was the one nobody trusted.
@ lobby.day | hero:stand/relieved | hale:stand/relieved | cta:subscribe | fr:wide | track:{air:"2:50"}
Subscribe. The next door lies too.
