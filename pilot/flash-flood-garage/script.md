TITLE: The Door Marked Do Not Use
LENGTH_MIN: 8
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=mustard, hair=short, skin=brown)
- jojo = rig_hero(outfit=cobalt, hat=cap, hair=curly, skin=tan)
- bell = rig_hero(outfit=olive, age=old, hair=short, skin=dark)
- alder = rig_hero(outfit=coral, age=old, hair=bun, skin=light)
LOCATIONS:
- street: flooded city street at night seen from a raised pavement, brown river water covering the road, streetlights standing in the water, heavy rain, orange glow in the sky
- b3: lowest level of an underground car park at night with concrete pillars, parked cars, painted bays and dim flickering strip lights, thin water on the floor
- ramp: steep concrete car park ramp sloping down, a thin sheet of shiny water sliding down it, dim strip lights, wet walls
- shutter: roller shutter half closed at the top of a car park ramp, street light shining under the gap, rain outside
- booth: small car park attendant booth with a window, a kettle, a clipboard and a torch, dim yellow light
- trolley: shopping trolley full of tinned peaches and bags in a car park, torch light, concrete pillar behind
- lift: lift lobby in a car park with a metal lift door and a small floor number display, flickering light, painted concrete
- stairs: concrete fire stairwell with metal handrails and painted floor numbers, torch light, echoing, damp walls
- b2: wide grey underground car park floor with pillars and painted bays, dim light, shiny damp concrete, water noise below
- exitd: end of a car park corridor with a tall grey metal door and an old red sign saying Exit D do not use loading bay, rust on the hinges, dim light
- chain: top of a concrete stairwell with a street door wrapped in a heavy chain and padlock, thin light under the door
- bay: dry steep concrete loading bay ramp climbing out of the dark toward a pale orange evening sky, calm and bright
- boat: flooded street at dusk with a rescue boat, streetlights standing in brown water, orange sky, rescue workers with torches
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: mystery
- CH4: tense

## CH1 | NINE TWELVE AT NIGHT
// ACT hook
@ street.night | fr:xwide,wide | fx:rain | sfx:thunder | track:{hours:"3"} | cam:push 1.00>1.14
It is 9:12 at night,
@ street.night | fr:insert,low | fx:rain | sfx:water_pour | cam:pan_l
the river is climbing over the road above you,
@ exitd.night | fr:insert,closeup | fx:flicker
and the only exit left in this car park is
@ b3.night | hero:stand/scared | fr:closeup,back | cam:pull 1.18>1.02
the one door everyone told you never to open.
// ACT act1
@ b3.night | fr:xwide,wide | track:{hours:"3"} | cam:tilt_up
Three hours until the flood crests.
@ b3.night | hero:phone_hold/shocked | fr:insert,closeup | sfx:phone_buzz | cam:pan_r
Your phone buzzes on the dashboard.
@ b3.night | hero:phone_hold/scared | fr:closeup,ots | ov:phone_alert("EMERGENCY ALERT","Marlow Street: leave now") | cam:push 1.05>1.20
"Marlow Street, leave the car park now."
@ b3.night | hero:stand/worried | fr:wide,medium | cam:parallax_drift
You are on level B3, the lowest floor,
@ shutter.night | fr:insert,low | fx:dust | sfx:impact | cam:tilt_down
and the shutter at the top of the ramp has just started to close.
@ ramp.night | hero:run/scared | fr:wide,low | cam:pull 1.22>1.06
You run for the ramp.
@ ramp.night | fr:insert,low | fx:rain | sfx:water_pour | cam:rack_focus
Water is already sliding down it, thin and shiny,
@ ramp.night | fr:closeup,wide | fx:rain | cam:push 1.00>1.14
like a tongue licking the concrete.
@ ramp.night | hero:stand/worried | fr:closeup,medium | track:{hours:"3",phone:"82%",tide:"ANKLES"} | cam:pan_l
Battery at eighty-two percent. Water at your ankles.
@ ramp.night | jojo:run/neutral | fr:wide,low | cam:pull 1.18>1.02
A delivery rider skids down the slope pushing a loaded bike.
@ ramp.night | jojo:stand/neutral | fr:medium,closeup | cam:tilt_up
This is Jojo.
@ ramp.night | jojo:stand/relieved | fr:closeup,profile | cam:pan_r
He has a helmet with ears, a yellow bag,
@ ramp.night | jojo:reach/neutral | fr:insert,closeup | cam:push 1.05>1.20
and a small tool pouch clipped on his belt.
@ shutter.night | jojo:point/worried | hero:look_up/determined | fr:ots,medium | cam:parallax_drift
"Shutter's stuck halfway," he says. "
@ shutter.night | jojo:shrug/worried | fr:closeup,low | cam:tilt_down
Nobody's driving out of here."
@ b3.night | bell:stand/relieved | fr:medium,wide | cam:pull 1.22>1.06
Behind a pillar, an old man in a green vest waves a torch.
@ booth.night | bell:stand/neutral | fr:closeup,ots | cam:rack_focus
Mr. Bell, the night attendant, sixty years on his feet and still smiling.
@ trolley.night | alder:stand/relieved | fr:medium,closeup | cam:push 1.00>1.14
Beside him, Mrs. Alder, round and unbothered,
@ trolley.night | fr:insert,low | cam:pan_l
guarding a shopping trolley full of tinned peaches.
@ b3.night | bell:point/neutral | hero:stand/neutral | fr:ots,wide | fx:beam | cam:pull 1.18>1.02
Mr. Bell points the torch along the far wall.
@ lift.night | fr:insert,low | cam:tilt_up
"Lift still works.
@ stairs.night | fr:insert,wide | cam:pan_r
Fire stairs behind it.
@ exitd.night | bell:point/worried | fr:ots,closeup | cam:push 1.05>1.20
And that door at the end of level B2, marked do not use, goes nowhere.
@ exitd.night | bell:stand/worried | fr:closeup,profile | cam:parallax_drift
Don't touch it."
@ exitd.night | jojo:stand/sly | fr:closeup,low | cam:tilt_down
Jojo grins at the sign.
@ exitd.night | jojo:shrug/sly | hero:look_up/worried | fr:medium,ots | cam:pull 1.22>1.06
"Everything in this place says do not use."
@ lift.night | fr:wide,xwide | fx:flicker | sfx:power_down
Then the lights flicker,
@ lift.night | fr:insert,closeup | fx:flicker
the lift display blinks,
@ lift.night | fr:low,wide | sfx:ding | cam:rack_focus
and the lift pings up to level B1 all by itself.
## CH2 | THE STAIRS
// ACT act2a
@ ramp.night | hero:stand/scared | fr:medium,low | fx:rain | track:{hours:"3",phone:"82%",tide:"KNEES"} | cam:push 1.00>1.14
Water at your knees on the ramp, three hours left,
@ b3.night | hero:stand/worried | jojo:stand/worried | fr:ots,wide | cam:pan_l
and you have to choose how to climb.
@ b3.night | hero:look_up/determined | jojo:look_up/determined | fr:ots | ov:option_cards("RAMP","LIFT","STAIRS","1","ledge,glow,arch")
Freeze. Option one, run up the car ramp before the water gets deeper.
@ b3.night | hero:stand/worried | jojo:stand/worried | fr:wide | ov:option_cards("RAMP","LIFT","STAIRS","2","ledge,glow,arch")
Option two, take the lift, because it is fast and dry.
@ b3.night | hero:look_up/determined | jojo:look_up/determined | fr:medium | ov:option_cards("RAMP","LIFT","STAIRS","3","ledge,glow,arch")
Option three, climb the fire stairs behind the lift.
@ b3.night | hero:stand/worried | jojo:stand/worried | fr:wide | ov:option_cards("RAMP","LIFT","STAIRS","0","ledge,glow,arch") | fx:flicker
Pause the video. Decide now.
@ b3.night | hero:look_up/determined | jojo:look_up/determined | fr:ots | ov:option_cards("RAMP","LIFT","STAIRS","0","ledge,glow,arch")
Your clock keeps running.
// HOLD decision 4.5
@ stairs.night | jojo:carry/determined | alder:push_cart/neutral | fr:wide,medium | sfx:footsteps | cam:pull 1.18>1.02
You choose option three. Jojo hauls his bike onto his shoulder, Mrs. Alder pushes her trolley up the first steps, and the three of you follow Mr. Bell's torch into the stairwell.
@ lift.night | fr:insert,low | cam:tilt_up
Behind you, the lift sinks back down with a tired little chime,
@ lift.night | fr:wide,closeup | fx:flicker | sfx:power_down
and its lights go out.
@ lift.night | fr:insert,closeup | cam:pan_r
The pit at the bottom of a lift shaft is the first place in a building to flood.
@ stairs.night | bell:point/neutral | fr:ots,insert | cam:push 1.05>1.20
The moment water touches the motor, the lift stops, with passengers inside.
@ ramp.night | fr:wide,low | fx:rain | cam:parallax_drift
And that ramp?
@ ramp.night | jojo:back_away/shocked | fr:closeup,wide | cam:tilt_down
Moving water only fifteen centimetres deep can knock a grown adult off their feet.
@ street.night | fr:xwide,wide | fx:rain | cam:pull 1.22>1.06
Level ground is a river's favourite road.
@ stairs.night | hero:walk/relieved | jojo:walk/relieved | fr:medium,wide | sfx:footsteps | cam:rack_focus
Stairs are boring. Stairs are why you are alive.
## CH3 | LEVEL B2
// ACT midpoint
@ b2.night | hero:walk/worried | jojo:walk/worried | bell:walk/neutral | alder:walk/neutral | fr:wide,xwide | sfx:footsteps | cam:push 1.00>1.14
On level B2 the stairwell door opens onto a wide grey floor and the sound of rushing water from somewhere below.
@ b2.night | hero:stand/worried | fr:closeup,medium | track:{hours:"2.7",phone:"71%"} | cam:pan_l
Seventy-one percent battery. Two hours forty left.
@ b2.night | jojo:phone_hold/worried | fr:closeup,insert | cam:pull 1.18>1.02
Jojo checks his phone and winces. "No signal down here."
@ stairs.night | bell:point/neutral | hero:stand/neutral | fr:ots,medium | fx:beam | cam:tilt_up
Mr. Bell sets his torch on a pillar. "
@ chain.night | fr:insert,wide | cam:pan_r
Street door is at the top of this stairwell. Chained from outside since the last storm. I never got the key back."
@ trolley.night | alder:stand/relieved | fr:closeup,medium | cam:push 1.05>1.20
Mrs. Alder pats her trolley. "Then we wait with peaches."
@ b2.night | fr:insert,low | fx:rain | cam:parallax_drift
Nobody laughs.
@ b2.night | fr:wide,low | sfx:water_pour | cam:tilt_down
The water on B2 is still dry, but you can hear it knocking on the walls like a patient visitor.
@ b2.night | hero:walk/worried | fr:back,wide | cam:pull 1.22>1.06
You walk along the wall to look for a vent, a window, anything.
@ exitd.night | fr:insert,closeup | fx:dust | cam:rack_focus
And there it is. A tall grey door at the end of the corridor, with an old red sign. Exit D. Do not use. Loading bay.
@ exitd.night | jojo:stand/worried | hero:stand/worried | fr:ots,medium | cam:push 1.00>1.14
Jojo whispers. "That one?"
@ exitd.night | bell:stand/worried | fr:closeup,profile | cam:pan_l
Mr. Bell frowns. "
@ exitd.night | bell:shrug/neutral | fr:medium,low | cam:pull 1.18>1.02
It jammed years ago. Hinges are rusty. I never even touched the handle."
@ b2.night | hero:phone_hold/worried | fr:insert,closeup | track:{hours:"2.6",phone:"64%"} | cam:tilt_up
Your phone shows no signal at all. Battery at sixty-four percent. One bar flickers, appears, disappears.
@ b2.night | hero:phone_hold/determined | jojo:look_up/determined | fr:ots | ov:option_cards("ONE MESSAGE","LONG CALL","PHONE OFF","1","star,arch,battery")
Freeze. Option one, hold the phone up near the vent and send a single short message with your level and street.
@ b2.night | hero:phone_hold/worried | jojo:stand/worried | fr:wide | ov:option_cards("ONE MESSAGE","LONG CALL","PHONE OFF","2","star,arch,battery")
Option two, call the emergency line and keep talking as long as you can.
@ b2.night | hero:phone_hold/determined | jojo:look_up/determined | fr:medium | ov:option_cards("ONE MESSAGE","LONG CALL","PHONE OFF","3","star,arch,battery")
Option three, switch the phone off completely to save every percent for later.
@ b2.night | hero:phone_hold/worried | jojo:stand/worried | fr:wide | ov:option_cards("ONE MESSAGE","LONG CALL","PHONE OFF","0","star,arch,battery") | fx:flicker
Pause the video. Decide now.
@ b2.night | hero:phone_hold/determined | jojo:look_up/determined | fr:ots | ov:option_cards("ONE MESSAGE","LONG CALL","PHONE OFF","0","star,arch,battery")
One bar will not last.
// HOLD decision 4.5
@ b2.night | hero:phone_hold/scared | fr:closeup,insert | sfx:typing | cam:pan_r
You choose option one. You type four lines. "Marlow Street car park. Four people. Level B2. Water rising." Send.
@ b2.night | hero:phone_hold/neutral | fr:insert,wide | ov:phone_alert("SENT","Marlow Street car park, level B2") | cam:push 1.05>1.20
The message climbs out of the dark and leaves.
@ stairs.night | fr:insert,closeup | sfx:ding | cam:parallax_drift
One word, delivered.
@ b2.night | hero:phone_hold/worried | jojo:stand/relieved | fr:medium,ots | cam:tilt_down
A call needs a steady signal for the whole minute, and one bar cannot hold it.
@ b2.night | fr:insert,low | cam:pull 1.22>1.06
A message needs only a second. Rescuers read messages while they are driving.
@ b2.night | hero:stand/worried | fr:closeup,medium | cam:rack_focus
And if you switch the phone off, there will be no answer when somebody finally writes back.
@ b2.night | hero:stand/relieved | fr:closeup,low | track:{phone:"61%"} | cam:push 1.00>1.14
You hold the phone close to your chest and it warms your hand. Sixty-one percent.
@ trolley.night | alder:reach/relieved | hero:look_up/sad | fr:medium,closeup | cta:subscribe | cam:pan_l
Mrs. Alder squeezes your hand. "If you'd like us to keep telling you stories, subscribe, and we will meet you in the next one."
@ trolley.night | jojo:stand/sly | fr:closeup,profile | cam:pull 1.18>1.02
Jojo grins. "Oh, I heard that."
@ b2.night | fr:insert,low | fx:rain | sfx:water_pour | track:{tide:"ANKLES"} | cam:tilt_up
Then the first real water arrives. Not a trickle, a lip of brown,
@ stairs.night | fr:wide,low | fx:rain | cam:pan_r
rolling under the stairwell door and spreading across the floor like spilled tea. Water at your ankles on B2.
@ stairs.night | bell:stand/worried | fr:medium,closeup | cam:push 1.05>1.20
Mr. Bell looks down at the water and then up at the stairs.
@ stairs.night | bell:point/worried | fr:closeup,ots | cam:parallax_drift
"At this speed, B2 is under in an hour."
@ chain.night | fr:insert,closeup | cam:tilt_down
You glance at the stair door at the top. Chained.
@ exitd.night | hero:look_up/worried | fr:back,wide | cam:pull 1.22>1.06
You look back at Exit D. Rusty.
@ b2.night | alder:stand/neutral | hero:stand/worried | fr:ots,profile | cam:rack_focus
Mrs. Alder watches your face and quietly says, "When you've looked at both, you already know."
@ exitd.night | jojo:crouch/determined | fr:insert,closeup,low | cam:push 1.00>1.14
Jojo kneels and opens his small tool pouch. "Let me try something."
@ stairs.night | hero:stand/scared | jojo:crouch/worried | fr:ots | ov:option_cards("WAIT UPSTAIRS","SHOUT AND BANG","BACK TO EXIT D","1","ledge,wind,gap")
Freeze. Option one, wait for rescue on the stairs, a floor above the water.
@ stairs.night | hero:look_up/shocked | jojo:crouch/determined | fr:wide | ov:option_cards("WAIT UPSTAIRS","SHOUT AND BANG","BACK TO EXIT D","2","ledge,wind,gap")
Option two, shout and bang on the chained street door until somebody hears.
@ stairs.night | hero:stand/scared | jojo:crouch/worried | fr:medium | ov:option_cards("WAIT UPSTAIRS","SHOUT AND BANG","BACK TO EXIT D","3","ledge,wind,gap")
Option three, go back to Exit D and work out why it is stuck.
@ stairs.night | hero:look_up/shocked | jojo:crouch/determined | fr:wide | ov:option_cards("WAIT UPSTAIRS","SHOUT AND BANG","BACK TO EXIT D","0","ledge,wind,gap") | fx:flicker
Pause the video. Decide now.
@ stairs.night | hero:stand/scared | jojo:crouch/worried | fr:ots | ov:option_cards("WAIT UPSTAIRS","SHOUT AND BANG","BACK TO EXIT D","0","ledge,wind,gap")
The water does not wait.
// HOLD decision 4.5
@ exitd.night | jojo:stand/determined | fr:closeup,ots | sfx:door_creak | cam:pan_l
You choose option three. Jojo presses his ear against the cold metal. He tries the handle. Nothing.
@ exitd.night | jojo:stand/neutral | hero:stand/worried | fr:medium,low | cam:pull 1.18>1.02
He wipes his hands on his coat, looks at the frame, and mutters, "It isn't locked. It is swollen."
@ exitd.night | fr:insert,closeup | fx:dust | cam:tilt_up
Rain, rust and a decade of damp.
@ exitd.night | jojo:reach/determined | fr:insert,closeup | cam:pan_r
He picks a flat tool from his pouch, slides it into the gap,
@ exitd.night | fr:wide,low | sfx:door_creak | cam:push 1.05>1.20
and the whole door gives a faint creak, like an old man stretching.
@ chain.night | fr:insert,wide | cam:parallax_drift
The street door was chained because someone wanted it shut. Exit D was marked because someone wanted it left alone.
@ exitd.night | hero:stand/neutral | fr:closeup,medium | cam:tilt_down
Neither sign said it was unsafe. One said do not enter. One said do not use.
@ bay.dusk | fr:xwide,wide | cam:pull 1.22>1.06
And the old loading bay, you remember, always sat higher than the street.
@ b2.night | hero:stand/worried | fr:closeup,medium | fx:rain | track:{hours:"1.7",phone:"52%",tide:"KNEES"} | cam:rack_focus
It is half past ten. Fifty-two percent. Water at your knees.
## CH4 | THE LAST HOUR
// ACT sacrifice
@ stairs.night | fr:wide,low | fx:flicker | sfx:power_down
Then the stairwell lights die.
@ stairs.blackout | fr:closeup,insert | fx:flicker
Everything goes black, except the little red glow of Mr. Bell's torch.
@ b2.blackout | fr:wide,low | sfx:impact | cam:push 1.00>1.14
A deep metallic groan rolls through the walls. The building is talking.
@ b2.night | hero:stand/scared | fr:medium,low | fx:rain | track:{hours:"1",tide:"WAIST"} | cam:pan_l
Water at your waist.
@ b2.night | hero:phone_hold/scared | fr:insert,closeup | track:{hours:"1",phone:"41%",tide:"WAIST"} | cam:pull 1.18>1.02
Forty-one percent. One hour left.
@ exitd.night | hero:stand/scared | jojo:stand/worried | bell:stand/worried | alder:stand/worried | fr:ots | ov:option_cards("PUSH TOGETHER","TAKE OUT PINS","BREAK THE CHAIN","1","rope,chalk,gap")
Freeze. Option one, push on the door together with all your weight.
@ exitd.night | hero:look_up/shocked | jojo:look_up/determined | bell:look_up/determined | alder:look_up/determined | fr:wide | ov:option_cards("PUSH TOGETHER","TAKE OUT PINS","BREAK THE CHAIN","2","rope,chalk,gap")
Option two, take the hinge pins out with Jojo's tool and lift the door off its frame.
@ exitd.night | hero:stand/scared | jojo:stand/worried | bell:stand/worried | alder:stand/worried | fr:medium | ov:option_cards("PUSH TOGETHER","TAKE OUT PINS","BREAK THE CHAIN","3","rope,chalk,gap")
Option three, run for the chained street door and try to break the chain.
@ exitd.night | hero:look_up/shocked | jojo:look_up/determined | bell:look_up/determined | alder:look_up/determined | fr:wide | ov:option_cards("PUSH TOGETHER","TAKE OUT PINS","BREAK THE CHAIN","0","rope,chalk,gap") | fx:flicker
Pause the video. Decide now.
@ exitd.night | hero:stand/scared | jojo:stand/worried | bell:stand/worried | alder:stand/worried | fr:ots | ov:option_cards("PUSH TOGETHER","TAKE OUT PINS","BREAK THE CHAIN","0","rope,chalk,gap")
The door is your only chance.
// HOLD decision 4.5
// ACT climax
@ exitd.night | jojo:crouch/determined | fr:insert,closeup,low | sfx:click | cam:tilt_up
You choose option two. Jojo kneels, taps the first hinge pin, then the second, then the third, one by one with the heel of his tool.
@ exitd.night | fr:insert,closeup | sfx:click | cam:pan_r
A bolt clicks, a pin slides out, and the door leans toward you with a long, tired sigh.
@ exitd.night | hero:reach/determined | jojo:reach/determined | bell:reach/determined | alder:reach/determined | fr:wide,medium | sfx:impact | cam:push 1.05>1.20
All four of you lift it together. The door tips outward, falls flat across the doorway,
@ exitd.night | hero:look_up/relieved | fr:closeup,back | sfx:wind | cam:parallax_drift
and a cold, clean wind blows straight into your face.
@ exitd.night | fr:insert,closeup | cam:tilt_down
You were not pushing at a lock. You were pushing against a hinge that rust had welded in place.
@ exitd.night | jojo:stand/neutral | fr:medium,low | cam:pull 1.22>1.06
A swollen door fights back harder the more you shove it.
@ exitd.night | fr:insert,wide | cam:rack_focus
Take out the pins, and it forgets how to resist.
@ bay.dusk | fr:wide,low | cam:push 1.00>1.14
Beyond the door is a concrete ramp, dry and steep,
@ bay.dusk | fr:xwide,wide | fx:dust | cam:pan_l
climbing out of the dark toward a pale orange sky.
@ bay.dusk | hero:shrug/sad | fr:back,wide | cam:pull 1.18>1.02
The loading bay. Two storeys above the street.
@ bay.dusk | bell:walk/relieved | fr:medium,wide | cam:tilt_up
Mr. Bell steps through first,
@ bay.dusk | alder:walk/relieved | jojo:walk/relieved | fr:wide,medium | cam:pan_r
then Mrs. Alder with her trolley, then Jojo with his bike.
@ b2.night | fr:insert,low | fx:rain | track:{phone:"37%",tide:"WAIST"} | cam:push 1.05>1.20
Water at your hips behind you. Thirty-seven percent.
// ACT resolution
@ street.dusk | hero:look_up/relieved | fr:back,wide | cam:parallax_drift
You climb to the top, and the street below is a brown river with
@ boat.dusk | fr:xwide,wide | fx:rain | cam:tilt_down
streetlights standing in it like candles in a birthday cake.
@ boat.dusk | fr:wide,low | cam:pull 1.22>1.06
A rescue boat rolls past.
@ boat.dusk | hero:hands_up/relieved | jojo:hands_up/relieved | bell:hands_up/relieved | alder:hands_up/relieved | fr:wide,medium | fx:beam | cam:rack_focus
A rescue crew waves a torch at the four of you.
@ street.dusk | fr:xwide,wide | sfx:thunder | cam:push 1.00>1.14
At midnight the flood crests,
@ ramp.night | fr:insert,wide | cam:pan_l
two metres above the ramp you first walked down.
@ street.dusk | alder:reach/relieved | fr:medium,closeup | cam:pull 1.18>1.02
Mrs. Alder shares peaches with a rescuer and says,
@ street.dusk | alder:stand/sly | fr:closeup,profile | cam:tilt_up
"I told you, I always bring supplies."
@ bay.dusk | bell:stand/relieved | fr:closeup,medium | cam:pan_r
Mr. Bell reads the sign on the loading bay door one last time.
@ bay.dusk | bell:point/relieved | fr:ots,closeup | cam:push 1.05>1.20
"I wrote that sign myself," he says.
@ bay.dusk | bell:stand/neutral | fr:profile,medium | cam:parallax_drift
"Thirty years ago. It means the door is old, not that it is dangerous."
@ street.dusk | hero:look_up/neutral | fr:back,wide | cam:tilt_down
So be honest.
@ ramp.night | fr:insert,low | cam:pull 1.22>1.06
At the foot of that ramp, with water at your knees, would you have taken the stairs?
// LASTLINE
@ bay.dusk | hero:stand/relieved | jojo:stand/relieved | bell:stand/relieved | alder:stand/relieved | fr:wide,low | cam:rack_focus
The door marked do not use was the only way out that was ever open.
@ bay.dusk | hero:look_up/sad | jojo:look_up/sad | bell:look_up/sad | alder:look_up/sad | fr:wide,medium | cta:subscribe | cam:push 1.00>1.14
Next time, the water will be darker and the clock will be shorter. Subscribe, and keep your torch.
