TITLE: The Water You Fear Is The Only Way Out
LENGTH_MIN: 8
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=cobalt, hat=cap, hair=curly, skin=brown)
- walt = rig_hero(outfit=olive, hair=short, age=old, skin=light)
LOCATIONS:
- mouth: sea cave entrance chamber with a fallen slab of rock blocking a bright opening, wet stones, a thin film of water on the floor, cold blue-teal rock walls
- passage: narrow natural sea cave passage with wet rock walls, a level white salt crust line running along both walls at chest height, shallow water on the floor, cold blue-teal light
- fork: cave junction where one passage splits into three tunnels, a wide left tunnel with a dry floor and a white chalk arrow painted on the wall, a narrow wet middle tunnel, a right tunnel sloping downward, ankle deep water, cold blue-teal rock
- deadend: smooth dead-end cave wall covered in white chalk scribbles, tally marks and old dates, wet floor, cold blue-teal rock
- narrow: very narrow wet cave tunnel with tight rock walls pinching into a small gap the width of a mailbox slot, dripping water, cold blue-teal rock
- chamber: huge sea cave chamber with a high ceiling, a clear level white salt line all the way around the walls at chest height, water filling the floor, a low arch on the far side with a soft green glow, a dark chimney shaft above and a rock ledge, cold blue-teal rock
- beach: silver moonlit beach in front of a sea cave mouth, wet sand, waves pulled far back, a sky full of stars, calm night, cold blue-teal and silver tones
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: mystery
- CH4: hopeful

## CH1 | FIVE HOURS OF LIGHT
// ACT hook
@ mouth.day | hero:stand/neutral | walt:stand/neutral | fx:beam | fr:wide | track:{lamp:"5h",tide:"SHALLOW"}
You have five hours of lamp light, three tunnels, and water rising behind you. By the end, you will be grateful for that water.
@ mouth.day | hero:stand/neutral | walt:stand/neutral | fr:medium
It starts as a quiet Sunday walk. Your neighbour Walt, seventy-one, a retired map maker with a slow smile, wants to see the sea cave he sketched as a young man.
@ mouth.day | hero:stand/neutral | walt:point/neutral | fr:ots
"Twenty minutes in, twenty minutes out," he said. "There used to be a wooden ladder up the back chimney. Rotten even then."
@ mouth.day | hero:back_away/scared | walt:back_away/shocked | cam:shake_medium | fr:wide
Then the rock above the entrance groans.
@ mouth.blackout | hero:stand/scared | walt:stand/shocked | fx:dust | fr:wide
A slab slides down with a sound like a closing door, and the daylight is gone.
@ mouth.night | hero:stand/worried | fx:beam,dust | fr:ots
Your headlamp clicks on. The battery reads five hours.
@ passage.night | hero:stand/worried | fx:beam | fr:low
Under your boots, cold water slides over the stones, and when a drop hits your lip, it tastes of salt.
@ passage.night | hero:stand/worried | walt:stand/neutral | fx:beam | fr:medium
Walt puts his palm flat on the wall. "Water always knows the way out," he said. "And air never lies. Follow the cold breath."
@ passage.night | hero:walk/determined | walt:walk/neutral | fx:beam | fr:back
You walk. Along both walls runs a strange white crust, chest high, perfectly level, like the ring around an old bathtub.
@ fork.night | hero:stand/worried | walt:stand/worried | fx:beam | fr:wide | track:{tide:"ANKLES"}
The passage splits. The water is at your ankles now. Walt is breathing hard.
@ fork.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("LEFT TUNNEL","MIDDLE TUNNEL","RIGHT TUNNEL","1","chalk,draught,wind") | fr:ots
Freeze. Option one, the wide left tunnel, with a dry floor and a white chalk arrow painted at eye level.
@ fork.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("LEFT TUNNEL","MIDDLE TUNNEL","RIGHT TUNNEL","2","chalk,draught,wind") | fr:wide
Option two, the narrow middle tunnel, wet and tight, where a cold draught touches your face.
@ fork.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("LEFT TUNNEL","MIDDLE TUNNEL","RIGHT TUNNEL","3","chalk,draught,wind") | fr:medium
Option three, the right tunnel, sloping downward, with a soft sound like wind.
@ fork.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("LEFT TUNNEL","MIDDLE TUNNEL","RIGHT TUNNEL","0","chalk,draught,wind") | fr:wide
Pause the video. Decide now.
@ fork.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("LEFT TUNNEL","MIDDLE TUNNEL","RIGHT TUNNEL","0","chalk,draught,wind") | fr:ots
Your light keeps burning.
// HOLD decision 4.5
@ deadend.night | hero:walk/neutral | walt:walk/neutral | fx:beam | fr:back
You follow the arrow. Anyone would. Forty steps later the tunnel ends at a smooth wall covered in chalk names and dates.
@ deadend.night | hero:stand/sad | walt:stand/sad | fx:beam | fr:wide | track:{lamp:"4h30"}
Visitors drew that arrow years ago to point people in, not out. You turn back. Four and a half hours of light.
@ fork.night | hero:point/determined | walt:stand/neutral | fx:beam | fr:medium
The middle tunnel was the answer, because moving air on your face means an opening somewhere ahead, and the wind in the right tunnel was only water echoing.
## CH2 | THE NARROW WAY
// ACT act2a
@ narrow.night | hero:walk/neutral | walt:walk/neutral | fx:beam | fr:back
Inside the middle tunnel the air smells fresher. Small win.
@ narrow.night | hero:crouch/worried | walt:crouch/worried | fx:beam | fr:ots
You squeeze forward, Walt's hand on your shoulder, until the rock pinches into a gap the width of a mailbox slot. Your backpack will not fit. Neither will his.
@ narrow.night | hero:stand/worried | walt:point/neutral | fx:beam | fr:medium
"One thing goes through with us," Walt said. "Just one."
@ narrow.night | hero:crouch/worried | fx:beam | fr:insert | track:{tide:"KNEES"}
You empty your bag onto a wet stone. The water is at your knees.
@ narrow.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("SPARE BATTERY","ROPE","WATER BOTTLE","1","battery,rope,bottle") | fr:ots
Freeze. Option one, the spare battery, worth two more hours of light.
@ narrow.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("SPARE BATTERY","ROPE","WATER BOTTLE","2","battery,rope,bottle") | fr:wide
Option two, the rope, thirty metres, heavy and soaked.
@ narrow.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("SPARE BATTERY","ROPE","WATER BOTTLE","3","battery,rope,bottle") | fr:medium
Option three, the full water bottle, because thirst is real.
@ narrow.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("SPARE BATTERY","ROPE","WATER BOTTLE","0","battery,rope,bottle") | fr:wide
Pause the video. Decide now.
@ narrow.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("SPARE BATTERY","ROPE","WATER BOTTLE","0","battery,rope,bottle") | fr:ots
The tide does not wait.
// HOLD decision 4.5
@ narrow.night | hero:reach/worried | walt:reach/shocked | fx:beam | fr:insert
Your fingers close around the battery. Walt's hand stops yours.
@ narrow.night | hero:stand/sad | walt:stand/neutral | fx:beam | fr:ots
"The ladder's gone," he said quietly. "Two more hours of light just means two more hours staring at a wall we can't climb."
@ narrow.night | hero:stand/determined | fx:beam | fr:medium
You keep the rope. Light only helps you see the cave, but rope is the one thing that changes where you can go.
@ narrow.night | hero:crouch/worried | fx:beam | fr:back
You push through the gap. Rock scrapes your back.
@ narrow.blackout | hero:stand/shocked | fx:flicker | fr:closeup
Then your lamp flickers. Once. Twice. Black.
@ narrow.blackout | hero:stand/scared | fr:silhouette
Nothing. No sound at all.
@ narrow.night | hero:stand/relieved | walt:stand/relieved | fx:beam | fr:medium | track:{lamp:"4h"}
You slap the lamp. It blinks back on. Four hours. Walt lets out a laugh that echoes for a long time, and you both stand there, dripping, grinning like kids.
@ narrow.night | hero:stand/relieved | walt:stand/relieved | cta:subscribe | fx:beam | fr:wide
If you kept the rope, you already think like a survivor. If you grabbed the battery, so did I the first time. Stay close, and subscribe so the next cave finds you.
## CH3 | THE WHITE LINE
// ACT midpoint
@ chamber.night | hero:stand/scared | walt:stand/worried | fx:beam | fr:wide
The new chamber is huge. Water pours in from somewhere low, filling the floor, climbing the walls. You panic. The whole cave is going to fill.
@ chamber.night | hero:stand/worried | walt:point/determined | fx:beam | fr:ots
Then Walt points his lamp at the wall. That white crust again. Chest high. All the way around, perfectly level.
@ chamber.night | hero:stand/neutral | walt:point/neutral | fx:beam | fr:medium
"That's a waterline," he said. "Salt. Hundreds of years of it. The water stops right there. It always has."
@ chamber.night | hero:stand/shocked | walt:stand/neutral | fx:beam | fr:closeup
Everything you believed flips. This is not a flood. It is the tide. It comes in, and it goes out.
@ chamber.night | hero:stand/worried | walt:point/worried | fx:beam | fr:wide | track:{tide:"WAIST"}
But the water is at your waist now, and across the chamber, under a low arch, a soft green glow shimmers like daylight.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("GREEN GLOW","DARK CHIMNEY","WAIT ON LEDGE","1","glow,chimney,ledge") | fr:ots | track:{lamp:"3h40"}
Freeze. Option one, swim for the green glow under the arch.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("GREEN GLOW","DARK CHIMNEY","WAIT ON LEDGE","2","glow,chimney,ledge") | fr:wide
Option two, climb the dark chimney now, using the rope.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("GREEN GLOW","DARK CHIMNEY","WAIT ON LEDGE","3","glow,chimney,ledge") | fr:medium
Option three, climb onto the ledge above the white line, switch off your lamp, and wait.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("GREEN GLOW","DARK CHIMNEY","WAIT ON LEDGE","0","glow,chimney,ledge") | fr:wide
Pause the video. Decide now.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("GREEN GLOW","DARK CHIMNEY","WAIT ON LEDGE","0","glow,chimney,ledge") | fr:ots
Three hours and forty minutes of light.
// HOLD decision 4.5
@ chamber.night | hero:walk/determined | fx:beam | fr:back
You wade toward the glow. Two strokes. Three. And the glow moves with you. It slides left when you slide left.
@ chamber.night | hero:stand/neutral | walt:stand/neutral | fx:beam | fr:medium
It is your own headlamp, reflected in a still pool on the ceiling of the arch. You turn back.
@ chamber.night | hero:point/neutral | walt:stand/neutral | fx:beam | fr:wide
The ledge was right, because the white line already told you where the water stops, and waiting in the dark costs no light at all.
@ chamber.night | hero:reach/determined | walt:reach/worried | fx:beam | fr:wide
You climb. Walt follows. You click off the lamp.
@ chamber.blackout | hero:sit/neutral | walt:sit/neutral | fr:silhouette | track:{lamp:"OFF"}
Darkness. Real darkness. Just the slow lap of water and Walt's breathing beside you.
@ chamber.blackout | hero:sit/neutral | walt:sit/sad | fr:silhouette
"I was lost in this cave once," he said. "I was twelve. My father found me. He came in from the sea, not the land. I never understood how."
@ chamber.blackout | hero:sit/worried | walt:sit/neutral | fr:silhouette | track:{tide:"SALT LINE"}
The water touches the white line. And stops.
@ chamber.blackout | hero:sit/relieved | walt:sit/relieved | fr:wide | track:{tide:"DRAINING"}
Then, slowly, it begins to fall.
## CH4 | THE TIDE TURNS
// ACT resolution
@ chamber.night | hero:stand/relieved | walt:stand/neutral | fx:beam | fr:medium | track:{lamp:"2h"}
When you switch the lamp back on, it reads two hours. The chamber floor is draining fast, and the tide will turn again before your light runs out. Three ways open in front of you.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("CHIMNEY","LOW ARCH","BACK TO GAP","1","star,arch,gap") | fr:ots
Freeze. Option one, the chimney, where your rope can reach a tiny point of starlight far above.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("CHIMNEY","LOW ARCH","BACK TO GAP","2","star,arch,gap") | fr:wide
Option two, the low arch where all the water is rushing away, down into the dark.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("CHIMNEY","LOW ARCH","BACK TO GAP","3","star,arch,gap") | fr:medium
Option three, back through the gap, toward the chalk arrow and the sealed entrance.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("CHIMNEY","LOW ARCH","BACK TO GAP","0","star,arch,gap") | fr:wide
Pause the video. Decide now.
@ chamber.night | hero:stand/worried | walt:stand/worried | fx:beam | ov:option_cards("CHIMNEY","LOW ARCH","BACK TO GAP","0","star,arch,gap") | fr:ots
The sea is already thinking about coming back.
// HOLD decision 4.5
@ chamber.night | hero:look_up/worried | walt:look_up/neutral | fx:beam | fr:ots
Up always feels like out. But the starlight is a crack no wider than a coin.
@ chamber.night | hero:walk/determined | walt:walk/neutral | fx:beam | fr:back
You choose the arch. You follow the water.
@ beach.night | hero:run/relieved | walt:walk/relieved | fr:wide
You crawl, then walk, then run on wet sand, and the arch opens onto a beach, silver under the moon, the waves pulled far back. Walt stops at the mouth of the cave and stares at the stars for a long time.
@ beach.night | hero:stand/relieved | walt:stand/neutral | fr:medium
"This is how he got me out," he said. "He waited for the tide."
@ beach.night | hero:stand/relieved | walt:stand/relieved | fr:wide
The slab that trapped you never mattered. This cave has a second door, and it opens only twice a day, when the sea steps back.
@ beach.night | hero:stand/neutral | walt:stand/neutral | fr:ots
You spent hours running from the water. It was showing you the way the entire time. You tasted the answer on your lip in the first minute.
@ beach.night | hero:look_up/neutral | walt:look_up/neutral | fr:back
So tell me honestly. At the last freeze, did you climb toward the stars, or follow the water?
// LASTLINE
@ beach.night | hero:stand/relieved | walt:stand/relieved | fr:wide
The water you feared was the only door out.
@ beach.night | hero:stand/relieved | walt:stand/relieved | cta:subscribe | fr:wide
Next time, the clock is shorter and the wrong answers are smarter. Subscribe, and walk in with us.
