TITLE: The Ticket That Should Not Exist
LENGTH_MIN: 8
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=red, hair=curly, skin=dark)
- rosa = rig_hero(outfit=navy, hat=cap, hair=bun, skin=light)
- okafor = rig_hero(outfit=plum, hair=bun, age=old, skin=dark)
- theo = rig_hero(outfit=olive, hat=beanie, hair=short, skin=tan)
- vane = rig_hero(outfit=grey, hair=short, age=old, skin=light)
LOCATIONS:
- snow: night train stopped in deep snow in a whiteout, amber carriage lights glowing in the white, buried track ahead, cold blue-white night
- window: close view of a frosted train window from inside, frost patterns on the glass, dim amber light, wooden window frame
- corridor: narrow train carriage corridor at night with frosted windows, dim amber ceiling lights, wooden panels
- cab: conductor alcove at the end of a carriage with a small battery panel with dials, a radio handset and a torch, dim amber light
- coach2: seating carriage of an old night train with wooden benches, knitted blankets, frosted windows, dim amber light
- compartment: tiny train compartment with two facing benches, wool blankets, small heater under the window, frost on the glass, warm dim light
- luggage: back of an old carriage with a luggage rack and a plywood panel on the wall, dim amber light, dust
- stove: small train compartment glowing orange from a squat black iron stove with a sack of coal, wool blankets, warm light, frost on the windows
- roof: view up through a train roof hatch at a snow covered chimney pipe and a dark snowy sky, falling snow
- snowcat: a snowcat vehicle with bright headlights driving through a whiteout toward a stopped train, snow swirling
- valley: snowy mountain valley at sunrise with a pink sky, a stopped night train and a snowcat in the snow, calm and bright
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: mystery
- CH4: tense

## CH1 | FIVE HOURS TO SUNRISE
// ACT hook
@ snow.night | fr:xwide | track:{hours:"5"}
Three passengers,
@ window.night | fr:insert,closeup
five hours until sunrise,
@ corridor.night | hero:look_up/worried | fr:ots,low
and one ticket that should not exist.
@ cab.night | hero:stand/scared | fr:closeup,back
By sunrise, you will know why its owner never threw it away.
// ACT act1
@ corridor.night | hero:sit/sleepy | fr:medium,closeup
The night train stops so gently you almost sleep through it.
@ corridor.night | hero:stand/shocked | fr:wide,low,closeup | fx:flicker
Then the engine dies, the lights blink amber, and the silence pours in like cold water.
@ snow.night | fr:xwide,wide
Somewhere ahead, in all that white, an avalanche has buried the track.
@ cab.night | rosa:stand/neutral | hero:stand/neutral | fr:medium,closeup,ots
The conductor is Rosa Penhale, nineteen, first week on the job, her name badge still shiny. She joined because her grandad worked this line.
@ cab.night | rosa:phone_hold/worried | fr:insert,ots,medium
She reaches dispatch a second before the signal fades. A crackly voice says,
@ cab.night | rosa:phone_hold/sad | hero:look_up/worried | fr:closeup,back
"Snowcat reaches you at sunrise. In this whiteout they can't see a thing. They'll drive the line and listen." Then nothing.
@ cab.night | rosa:point/worried | fr:insert,medium | track:{phone:"60%"}
Rosa checks the panel. "Battery at sixty percent," she says. "Below ten, everything shuts off. Heaters, lights, all of it." Outside, it is minus eighteen.
@ coach2.night | okafor:sit/neutral | theo:sit/neutral | vane:sit/neutral | fr:wide,medium
There are only three other passengers.
@ coach2.night | okafor:write/relieved | fr:medium,insert
Mrs. Okafor, round and calm, knitting a scarf longer than she is.
@ coach2.night | theo:reach/determined | fr:closeup,low
Theo, sixteen, cranking a little wind-up radio like a fishing reel.
@ window.night | vane:stand/neutral | fr:profile,insert,closeup
And Mr. Vane, old and quiet in a grey coat, who runs his thumb along the window frame and mutters, "Still haven't fixed this latch."
@ cab.night | rosa:stand/worried | hero:stand/neutral | fr:ots,closeup
Rosa whispers one more thing you will need. "The heaters drink power. The lights barely sip."
@ window.night | fr:insert,closeup | track:{phone:"51%"}
Forty minutes pass. Battery at fifty-one percent. Frost creeps across the inside of the glass.
## CH2 | THE HEATERS
// ACT act2a
@ corridor.night | hero:stand/worried | rosa:stand/worried | fr:ots | ov:option_cards("ALL HEATERS","LIGHTS ONLY","ONE ROOM","1","draught,glow,ledge")
Freeze. Option one, keep the heaters in all three coaches running on low, so nobody is cold anywhere.
@ corridor.night | hero:stand/worried | rosa:stand/worried | fr:wide | ov:option_cards("ALL HEATERS","LIGHTS ONLY","ONE ROOM","2","draught,glow,ledge")
Option two, switch the heaters off and keep the lights on, because people panic in the dark.
@ corridor.night | hero:stand/worried | rosa:stand/worried | fr:medium | ov:option_cards("ALL HEATERS","LIGHTS ONLY","ONE ROOM","3","draught,glow,ledge")
Option three, one heater, one compartment, everyone squeezed together under Mrs. Okafor's blankets.
@ corridor.night | hero:stand/worried | rosa:stand/worried | fr:wide | ov:option_cards("ALL HEATERS","LIGHTS ONLY","ONE ROOM","0","draught,glow,ledge") | fx:flicker
Pause the video. Decide now.
@ corridor.night | hero:stand/worried | rosa:stand/worried | fr:ots | ov:option_cards("ALL HEATERS","LIGHTS ONLY","ONE ROOM","0","draught,glow,ledge")
Your battery keeps falling.
// HOLD decision 4.5
@ compartment.night | hero:sit/worried | okafor:sit/relieved | theo:sit/neutral | fr:medium,wide
You choose option three. Five people, one small room, knees touching.
@ compartment.night | okafor:reach/relieved | fr:insert,medium,closeup
Mrs. Okafor hands out wool like a magician.
@ cab.night | rosa:point/relieved | fr:insert,ots | track:{phone:"55%"}
The drain slows to a crawl.
@ coach2.night | fr:wide,low,xwide
Three heaters on low would have warmed empty seats and drained everything by four. Heat you don't share is heat you waste.
@ compartment.night | hero:sit/relieved | fr:closeup,medium
It works. For a while.
@ cab.night | rosa:back_away/scared | hero:stand/worried | fr:closeup,ots
Then Rosa goes pale. "The roof marker lights run on the same battery," she says. "If we spend it all on warmth, there's nothing left to be seen with."
@ snow.night | fr:xwide,wide,insert | fx:dust
Every percent of heat is a percent of being found.
@ cab.night | rosa:stand/worried | fr:insert,closeup | track:{hours:"4",phone:"44%"}
Four hours left. Battery at forty-four percent.
## CH3 | THE TICKET
// ACT midpoint
@ corridor.night | rosa:write/neutral | hero:stand/neutral | fr:medium,insert,ots
Rescue needs a passenger list, so Rosa checks tickets by torchlight.
@ coach2.night | okafor:sit/neutral | rosa:write/neutral | fr:profile,insert
Mrs. Okafor, coach two, seat fourteen. Theo, student pass, coach three.
@ coach2.night | vane:reach/neutral | rosa:reach/shocked | fr:insert,closeup,ots
Then Mr. Vane hands over a ticket that is soft and yellow, with an ink stamp instead of a barcode.
@ coach2.night | rosa:stand/shocked | vane:stand/neutral | fr:closeup,low,wide
"Coach four, berth B," Rosa reads. This train has three coaches.
@ window.night | vane:stand/neutral | fr:silhouette,insert,profile
Nobody speaks. Mr. Vane just watches the frosted window.
@ coach2.night | hero:stand/worried | vane:stand/neutral | fr:ots | ov:option_cards("MOVE HIM","IGNORE IT","ASK HIM","1","gap,wind,star")
Freeze. Option one, move Mr. Vane to the empty front coach until rescue, because a fake ticket might hide something worse.
@ coach2.night | hero:stand/worried | vane:stand/neutral | fr:wide | ov:option_cards("MOVE HIM","IGNORE IT","ASK HIM","2","gap,wind,star")
Option two, ignore it, because tickets don't matter tonight.
@ coach2.night | hero:stand/worried | vane:stand/neutral | fr:medium | ov:option_cards("MOVE HIM","IGNORE IT","ASK HIM","3","gap,wind,star")
Option three, ask him one question that only a real passenger of coach four could answer.
@ coach2.night | hero:stand/worried | vane:stand/neutral | fr:wide | ov:option_cards("MOVE HIM","IGNORE IT","ASK HIM","0","gap,wind,star") | fx:flicker
Pause the video. Decide now.
@ coach2.night | hero:stand/worried | vane:stand/neutral | fr:ots | ov:option_cards("MOVE HIM","IGNORE IT","ASK HIM","0","gap,wind,star")
Your clock keeps running.
// HOLD decision 4.5
@ coach2.night | hero:point/determined | vane:stand/neutral | fr:ots,closeup
You choose option three. "What was coach four?"
@ coach2.night | vane:stand/relieved | fr:closeup,medium
For the first time, he smiles.
@ luggage.night | vane:point/neutral | fr:wide,insert,ots
"The guard's van," he says. "It had an iron stove. When they cut the van off, they boarded the stove up in the back of coach three. Behind the luggage rack."
@ window.night | vane:reach/neutral | fr:insert,closeup
Remember the latch he knew was broken.
@ coach2.night | hero:stand/relieved | vane:stand/neutral | fr:medium,low
A stranger doesn't know a train's old injuries. Locking him away would have locked away the only person who knew this train.
@ luggage.night | theo:reach/shocked | hero:crouch/worried | fr:insert,closeup,wide
Behind a plywood panel there it is. A squat black stove and a sack of old coal.
@ stove.night | theo:reach/determined | fr:insert,closeup | fx:embers
Theo finds a lighter.
@ stove.night | hero:sit/relieved | okafor:sit/relieved | vane:sit/neutral | fr:wide,medium,low | fx:embers | track:{phone:"41%"}
Ten minutes later the compartment glows orange, and you switch off the last heater. Battery holding at forty-one percent.
@ stove.night | okafor:stand/relieved | vane:stand/relieved | fr:medium,closeup
Mrs. Okafor laughs and wraps half of her endless scarf around Mr. Vane's shoulders.
@ stove.night | hero:stand/relieved | okafor:stand/relieved | theo:stand/relieved | fr:wide,medium | cta:subscribe | fx:embers
If you trusted the old man, you read people like a survivor. If you didn't, stay close, because the next freeze bites harder. Subscribe so the next train finds you.
@ window.night | vane:stand/relieved | fr:closeup,profile
Here is what you got wrong. He never lied. His ticket was simply older than the train.
## CH4 | THREE IN THE MORNING
// ACT sacrifice
@ snow.night | fr:xwide,wide | fx:snow | track:{hours:"3"}
Three in the morning. Snow piles higher. The windows go dark.
@ cab.night | rosa:stand/shocked | hero:stand/scared | fr:ots,wide | fx:alarm_pulse | track:{hours:"1.5",phone:"20%"}
At four forty, three things happen at once. A sharp beep from the battery panel, flashing twenty percent.
@ coach2.night | fr:low,wide,insert
A long crack from the roof above your heads.
@ stove.night | fr:insert,closeup
And a soft, steady hiss from the stove pipe.
@ stove.night | vane:point/neutral | hero:stand/worried | fr:closeup,ots
Earlier, when the fire caught, Mr. Vane had tapped that pipe. "If she ever hisses," he said, "the chimney is drowning in snow."
@ stove.night | hero:stand/scared | rosa:stand/scared | fr:ots | ov:option_cards("SHUT LIGHTS","GET DOWN","CLEAR PIPE","1","battery,gap,chimney")
Freeze. Option one, the battery alarm. Shut down the marker lights now.
@ stove.night | hero:stand/scared | rosa:stand/scared | fr:wide | ov:option_cards("SHUT LIGHTS","GET DOWN","CLEAR PIPE","2","battery,gap,chimney")
Option two, the crack in the roof. Get everyone down onto the corridor floor.
@ stove.night | hero:stand/scared | rosa:stand/scared | fr:medium | ov:option_cards("SHUT LIGHTS","GET DOWN","CLEAR PIPE","3","battery,gap,chimney")
Option three, the hiss. Reach up through the roof hatch and push the snow cap off the chimney with Rosa's signal pole.
@ stove.night | hero:stand/scared | rosa:stand/scared | fr:wide | ov:option_cards("SHUT LIGHTS","GET DOWN","CLEAR PIPE","0","battery,gap,chimney") | fx:flicker
Pause the video. Decide now.
@ stove.night | hero:stand/scared | rosa:stand/scared | fr:ots | ov:option_cards("SHUT LIGHTS","GET DOWN","CLEAR PIPE","0","battery,gap,chimney")
The air is getting thick.
// HOLD decision 4.5
// ACT climax
@ roof.night | hero:reach/determined | rosa:crouch/worried | fr:low,ots,wide
You choose option three. Rosa holds your boots while you jab the pole upward.
@ roof.night | fr:insert,wide,low | fx:snow
A heavy slab of snow slides away, and the pipe breathes again.
@ roof.night | hero:look_up/relieved | fr:back,wide
Grey smoke rises straight into the dark.
@ cab.night | rosa:point/relieved | hero:stand/relieved | fr:medium,closeup
"The panel cries wolf at twenty," Rosa admits. "The real cutoff is ten." And the crack? Just snow settling, the roof talking in its sleep.
@ stove.night | fr:insert,closeup
Silence. Only the stove, ticking.
@ snow.dusk | fr:xwide,wide | track:{hours:"0.3",phone:"9%"}
Five fifty. Sunrise in twenty minutes. Battery at nine percent.
@ coach2.dusk | theo:look_up/shocked | fr:closeup,profile,ots
Theo hears it first. Far away, a low engine, grinding, fading in and out with the wind.
@ cab.dusk | rosa:reach/worried | fr:insert,closeup,ots
Rosa's hand hovers over the controls. "The horn runs on stored air," she says. "Three blasts. That's all we get."
@ cab.dusk | hero:stand/scared | rosa:stand/worried | fr:ots | ov:option_cards("ALL LIGHTS","HORN NOW","WAIT, THEN HORN","1","glow,wind,star")
Freeze. Option one, switch on every marker light now and burn the last nine percent.
@ cab.dusk | hero:stand/scared | rosa:stand/worried | fr:wide | ov:option_cards("ALL LIGHTS","HORN NOW","WAIT, THEN HORN","2","glow,wind,star")
Option two, blow all three horn blasts right away, so they know early.
@ cab.dusk | hero:stand/scared | rosa:stand/worried | fr:medium | ov:option_cards("ALL LIGHTS","HORN NOW","WAIT, THEN HORN","3","glow,wind,star")
Option three, wait until the engine is close and loud, then blow the horn three times.
@ cab.dusk | hero:stand/scared | rosa:stand/worried | fr:wide | ov:option_cards("ALL LIGHTS","HORN NOW","WAIT, THEN HORN","0","glow,wind,star") | fx:flicker
Pause the video. Decide now.
@ cab.dusk | hero:stand/scared | rosa:stand/worried | fr:ots | ov:option_cards("ALL LIGHTS","HORN NOW","WAIT, THEN HORN","0","glow,wind,star")
They might drive right past.
// HOLD decision 4.5
@ snowcat.dusk | fr:xwide,wide,low
You choose option three. You wait. The engine grows louder. Louder. Now.
@ snow.dusk | fr:wide,low,xwide | fx:dust
Three long blasts roll across the valley. The engine stops. Then it turns toward you.
@ cab.dusk | rosa:stand/relieved | hero:stand/relieved | fr:ots,closeup,medium
Dispatch said it in the first minute. In a whiteout, they can't see. They drive the line and listen. Lights would have died unseen at dawn. Early blasts would have vanished in the wind.
// ACT resolution
@ valley.day | hero:walk/relieved | okafor:walk/relieved | theo:walk/relieved | fr:wide,xwide,medium
The snowcat crew helps everyone out into a pink sunrise. Mr. Vane goes last. He presses his old ticket into Rosa's hand.
@ valley.day | vane:reach/neutral | rosa:reach/shocked | fr:insert,closeup,ots
It is dated forty years ago tonight. Same train, same pass, same snow. He was a boy in coach four, and the guard lit the iron stove and told stories until morning.
@ valley.day | vane:stand/neutral | rosa:stand/shocked | fr:profile,closeup,medium
"The guard's name," Mr. Vane said, "was Penhale."
@ valley.day | rosa:stand/shocked | fr:closeup,insert
Rosa stares down at her shiny badge. "That was my grandad," she said.
@ valley.day | vane:stand/relieved | rosa:stand/relieved | fr:medium,wide,low
"I ride this train every year on this night," he said. "Just in case."
@ valley.day | hero:look_up/neutral | fr:back,wide
So be honest. At nine percent, with that engine fading in and out, could you have waited?
// LASTLINE
@ valley.day | vane:stand/relieved | rosa:stand/relieved | hero:stand/relieved | fr:wide,low
The ticket that should not exist was the only one that mattered.
@ valley.day | vane:stand/relieved | rosa:stand/relieved | hero:stand/relieved | fr:wide,medium | cta:subscribe
Next time, you'll have less light and a stranger who really is lying. Subscribe, and keep your ticket.
