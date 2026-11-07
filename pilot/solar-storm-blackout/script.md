TITLE: Solar Storm Blackout
LENGTH_MIN: 4
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=teal, hat=cap, hair=short)
- mara = rig_hero(outfit=plum, hat=none, hair=bun, age=old)
LOCATIONS:
- apartment: cramped one-room city apartment with a single bed under a big window, a cluttered desk with a laptop, a warm lamp and curtains over a street view
- street: quiet city apartment street with parked cars, brick buildings and a distant gas station sign
- gas_station: small corner gas station with two pumps under a flat canopy and a tiny shop
- hallway: narrow apartment corridor with numbered wooden doors, worn carpet and a faint exit sign
- kitchen: small tidy kitchen with an old refrigerator, a window with lace curtains, a radio on a shelf and a power grid map pinned to the wall
- stairwell: narrow concrete stairwell with metal railings, tall windows and one bare bulb
- rooftop: apartment rooftop with water tanks, a low brick wall and a wide view over a city skyline
MUSIC_MOODS:
- CH1: dread
- CH2: urgent
- CH3: climax

## CH1 | FRIDAY 3:12 AM
// RITUAL tracker: the survival log opens every chapter
// LOOP open why_only_me: why did only your phone get the warning
@ apartment.night | hero:sit_bed/sleepy | cam:push 1.00>1.10 | fx:dust | sfx:ticking_clock | track:{hours:15,water:"6 L",phone:"38%",cash:"$40"}
It's Friday, three twelve in the morning.
@ apartment.night | hero:phone_hold/scared | ov:phone_alert("EMERGENCY ALERT","Severe space weather. Impact in 15 hours") | cam:push 1.05>1.20 | fx:flicker | sfx:alert_siren,phone_buzz
And your phone is screaming.
@ apartment.night | hero:phone_hold/shocked | ov:timer("15:00:00","UNTIL IMPACT") | cam:push 1.04>1.18 | sfx:heartbeat
Fifteen hours. That's all you have before a solar storm hits Earth.
@ apartment.night | hero:stand/worried | ov:paper_diagram("SOLAR STORM PATH","Sun","Storm cloud","Earth","Power grid") | cam:pull 1.20>1.08 | sfx:paper_slide
Storm clouds from the Sun can be fast.
@ apartment.night | hero:stand/worried | ov:label_tag("15-18 HOURS") | cam:push 1.04>1.16 | sfx:click
The fastest reach Earth in just fifteen to eighteen hours.
@ apartment.night | hero:stand/scared | ov:label_tag("G5 = EXTREME") | cam:push 1.06>1.20 | sfx:click
At the top level, a G5, some power grids can collapse completely.
@ street.night | cam:pan_r 1.12>1.12 | fx:dust | sfx:wind
You peek through the curtain. The street is silent.
@ street.night | cam:push 1.04>1.18 | fx:smoke | sfx:wind
Not one window is lit.
@ apartment.night | hero:stand/scared | cam:push 1.10>1.30 | sfx:heartbeat
So why did only your phone wake up?
@ rooftop.blackout | hero:stand/sad | banner:"SATURDAY 6:00 AM" | cam:pull 1.25>1.06 | sfx:wind
Fast forward. Saturday, six in the morning.
@ rooftop.blackout | hero:stand/sad | cam:parallax_drift 1.05>1.16 | sfx:wind
You stand on a rooftop, and the whole city is dark.
@ rooftop.blackout | hero:phone_hold/scared | ov:label_tag("BATTERY 1%") | cam:push 1.05>1.22 | sfx:beep
One percent battery. And behind you, a voice says your name.
@ apartment.night | hero:sit_bed/determined | cam:hold | sfx:click
Back to Friday. Fifteen hours. You grab a notepad.
@ apartment.night | hero:stand/worried | cam:pull 1.18>1.06 | sfx:rustle
You've read about storms like this. You never thought one would find you.
@ apartment.night | hero:write/determined | ov:notepad_tracker("SURVIVAL LOG") | cam:push 1.00>1.12 | sfx:typing
Six liters of water. Thirty-eight percent battery. Forty dollars in cash.
@ apartment.night | hero:point/worried | ov:arrow_callout("1 gallon per person, per day","right") | cam:push 1.06>1.18 | sfx:click
Ready dot gov says one gallon of water, per person, per day.
@ apartment.night | hero:stand/worried | cam:push 1.08>1.20 | sfx:click
You have under two days.
@ apartment.night | hero:carry/determined | cam:pan_l 1.12>1.12 | sfx:water_pour
So you fill every pot, every bottle, every cup you own.
@ apartment.night | hero:carry/determined | cam:push 1.04>1.16 | sfx:water_pour,rustle
The bathtub too. Every drop counts. You grab batteries, a flashlight, and your charger.
@ apartment.night | hero:phone_hold/worried | ov:phone_search("solar storm tonight","One headline loads","Page not responding") | cam:push 1.04>1.16 | sfx:beep
You search for answers. One headline loads, and then the page freezes.
@ apartment.night | hero:phone_hold/scared | cam:push 1.06>1.18 | fx:flicker | sfx:beep
Your signal drops from four bars to one.
@ street.night | cam:pan_l 1.12>1.12 | fx:dust | sfx:wind
In the street below, a dog barks at nothing.
// PLANT groceries: you carried Mara's groceries last winter
@ hallway.night | hero:stand/neutral | ov:sticky_note("3B","Check on Mara") | cam:parallax_drift 1.05>1.12 | sfx:footsteps
Then you remember Mara, in apartment three B.
@ hallway.night | hero:stand/worried | cam:push 1.06>1.18 | sfx:footsteps
Last winter, you carried her groceries up four floors.
// PLANT number: Mara asked for your phone number
@ hallway.night | hero:stand/worried | cam:push 1.08>1.24 | sfx:door_knock
She asked for your phone number. Just in case, she said.
// CLIFF
@ apartment.alarm | hero:phone_hold/shocked | ov:phone_alert("UPDATE","Impact moved up. 9 hours.") | cam:shake_light 1.10>1.10 | fx:alarm_pulse | sfx:alert_siren | track:{hours:9}
Then your phone buzzes again. Fifteen hours just became nine.

## CH2 | FRIDAY 9:05 AM
// RITUAL tracker: the survival log is updated at the start of each chapter
// LOOP open stranger_doubt: nobody in the building believes the warning
// LOOP open mara_knows: why does Mara know so much
@ apartment.day | hero:write/worried | ov:notepad_tracker("SURVIVAL LOG") | cam:push 1.00>1.12 | sfx:typing | track:{hours:3,phone:"100%"}
Nine oh five. Three hours left.
// CTA sits at roughly one third of the story
@ apartment.day | hero:phone_hold/determined | cam:push 1.05>1.20 | cta:subscribe | sfx:click
Stay with me. If you want to see how this ends, subscribe.
@ hallway.day | hero:stand/worried | cam:pan_l 1.10>1.10 | sfx:door_knock,footsteps
You knock on every door in the hallway.
@ hallway.day | hero:stand/sad | cam:push 1.04>1.16 | sfx:door_creak
Most never answer.
@ hallway.day | hero:stand/sad | cam:push 1.06>1.18 | sfx:door_creak
One man laughs. Space weather? Go back to bed, he says.
@ hallway.day | hero:stand/worried@left | mara:carry/neutral@right | cam:push 1.06>1.20 | sfx:door_creak
Then a door opens. It's Mara, holding a radio with a hand crank.
@ hallway.day | hero:stand/neutral@left | mara:stand/determined@right | cam:push 1.06>1.18 | sfx:click
She doesn't laugh.
@ kitchen.day | hero:stand/neutral@left | mara:point/determined@right | ov:hand_pen("9 HOURS DARK") | cam:push 1.05>1.18 | sfx:rustle
Nineteen eighty-nine, she says. Canada. Nine hours of blackout.
@ kitchen.day | hero:stand/worried@left | mara:stand/neutral@right | cam:parallax_drift 1.05>1.14 | sfx:click
Her voice is steady. Too steady.
@ kitchen.day | hero:stand/neutral@left | mara:stand/neutral@right | cam:pan_r 1.12>1.12 | sfx:click
A map of the power grid hangs on her wall.
@ kitchen.day | mara:point/determined@right | hero:stand/neutral@left | cam:push 1.04>1.16 | sfx:click
Rule one. Keep the fridge shut.
@ kitchen.day | mara:point/determined@right | hero:stand/neutral@left | ov:paper_bar_chart("HOW LONG FOOD STAYS COLD","Fridge=4","Full freezer=48") | cam:pull 1.18>1.06 | sfx:paper_slide
It stays cold about four hours. A full freezer lasts forty-eight.
@ kitchen.day | mara:stand/worried@right | hero:stand/neutral@left | ov:sticky_note("RULE 2","CASH") | cam:push 1.04>1.16 | sfx:click
Rule two. Cash. When the grid fails, card readers die.
@ kitchen.day | mara:carry/determined@right | hero:stand/neutral@left | ov:label_tag("HAND-CRANK RADIO") | cam:parallax_drift 1.05>1.14 | sfx:click
Rule three. A radio that needs no power. She hands you hers.
@ kitchen.day | mara:stand/sly@right | hero:stand/worried@left | cam:push 1.06>1.18 | sfx:click
Take it, she says. You'll need it.
@ kitchen.day | mara:stand/sly@right | hero:stand/worried@left | cam:push 1.04>1.16 | sfx:ticking_clock
Mara checks her watch. Then she looks at you, a little too long.
@ street.day | cam:pan_r 1.12>1.12 | fx:dust | sfx:car_engine
Downstairs, a man wires a generator inside his garage.
@ street.day | hero:point/angry | cam:push 1.06>1.20 | sfx:footsteps
You stop him. Ready dot gov says outdoors only, away from windows.
@ street.day | hero:point/determined | cam:push 1.04>1.16 | sfx:car_engine
He shrugs, and drags it outside.
@ street.day | hero:run/determined | ov:dashed_path("Home","Gas station") | cam:pan_r 1.10>1.10 | sfx:footsteps
You run to the gas station with forty dollars in your hand.
@ gas_station.day | hero:stand/shocked | cam:push 1.05>1.18 | fx:dust | sfx:crowd_murmur,car_engine
A dozen cars are already waiting.
@ gas_station.day | hero:stand/worried | cam:push 1.04>1.16 | sfx:crowd_murmur
Every pump here runs on electricity.
@ gas_station.day | hero:stand/determined | ov:receipt("CORNER GAS","Fuel   $20.00","Water x2   $4.00","TOTAL   $24.00") | cam:push 1.03>1.14 | sfx:beep | track:{cash:"$16",water:"8 L"}
Twenty dollars of fuel. Two bottles of water. Sixteen dollars left.
@ street.day | hero:run/scared | ov:timer("00:52:00","UNTIL IMPACT") | cam:push 1.06>1.22 | sfx:heartbeat,ticking_clock | track:{hours:"0.9"}
It's eleven twenty. Fifty-two minutes left.
@ stairwell.day | hero:stand/scared@left | mara:stand/worried@right | cam:shake_medium 1.12>1.12 | fx:flicker | sfx:spark
In the stairwell, the lights flicker. Once. Twice.
// CLIFF
@ stairwell.day | hero:stand/shocked@left | mara:stand/scared@right | cam:push 1.08>1.26 | sfx:heartbeat
Then Mara grabs your wrist.

## CH3 | FRIDAY 12:12 PM
// RITUAL tracker: the survival log is updated at the start of each chapter
@ stairwell.blackout | hero:stand/scared@left | mara:stand/scared@right | ov:notepad_tracker("SURVIVAL LOG") | cam:push 1.00>1.14 | sfx:power_down | track:{hours:0,power:"OFF",phone:"no signal"}
Twelve twelve. Every light in the building dies at once.
@ street.blackout | cam:pull 1.20>1.06 | fx:dust | sfx:wind
Outside, the traffic lights go dark. Every one of them.
@ hallway.blackout | hero:hide/scared | cam:push 1.04>1.18 | fx:flicker | sfx:heartbeat
No elevator. No Wi-Fi. No signal.
@ hallway.blackout | hero:phone_hold/sad | cam:push 1.05>1.20 | sfx:beep
Your phone shows no bars. Nothing. Only a clock.
@ hallway.blackout | hero:stand/worried | ov:numbered_circle(4,"G5 STORMS PER SOLAR CYCLE") | cam:push 1.05>1.16 | sfx:click
A storm this strong happens about four times in an eleven-year solar cycle.
@ hallway.blackout | hero:stand/sad | cam:parallax_drift 1.05>1.12 | sfx:click
That's why nobody was ready.
// LOOP close stranger_doubt: the neighbours finally listen
@ hallway.blackout | hero:stand/determined@left | mara:stand/neutral@right | cam:pan_l 1.10>1.10 | sfx:door_knock,crowd_murmur
Doors open. Neighbors with flashlights.
@ hallway.blackout | hero:stand/relieved@left | mara:stand/neutral@right | cam:push 1.05>1.16 | sfx:crowd_murmur
Now, finally, they listen.
@ hallway.blackout | hero:stand/sad@left | mara:stand/worried@right | cam:push 1.04>1.14 | sfx:crowd_murmur
A little girl asks if the lights will come back.
@ hallway.blackout | hero:stand/relieved@left | mara:stand/neutral@right | cam:push 1.04>1.14 | sfx:click
You say yes. Not today, but soon.
// BEAT emotional: you sit with Mara in the dark and share the last water
@ kitchen.blackout | hero:sit/sad@left | mara:sit/sad@right | cam:push 1.04>1.14 | fx:flicker | sfx:rustle
In her dark kitchen, Mara's hands shake.
@ kitchen.blackout | hero:sit/sad@left | mara:sit/sad@right | cam:push 1.05>1.18 | sfx:water_pour
You hand her your last bottle of water.
@ kitchen.blackout | hero:sit/determined@left | mara:sit/relieved@right | ov:glitch_text("CRANK") | cam:push 1.05>1.18 | sfx:radio_static
You turn the crank. Static. Static.
// PAYOFF radio: the hand-crank radio is the only voice in the dark
@ kitchen.blackout | hero:sit/relieved@left | mara:sit/relieved@right | cam:parallax_drift 1.05>1.14 | sfx:radio_static
Then a voice: crews are working, and power will return.
@ kitchen.blackout | hero:sit/sleepy@left | mara:sit/sleepy@right | cam:pull 1.18>1.06 | sfx:ticking_clock
The night drags on. You take turns cranking the radio.
@ rooftop.dusk | hero:stand/worried | cam:push 1.05>1.16 | sfx:wind
You wonder: why you? Why your number?
@ rooftop.blackout | hero:stand/relieved | cam:pull 1.20>1.06 | sfx:wind
Dawn breaks on the rooftop. Your phone shows one percent.
@ rooftop.blackout | hero:stand/shocked@left | mara:stand/sly@right | cam:push 1.05>1.22 | sfx:footsteps
You turn around. Mara is standing there, with a thermos and a tired smile.
// PAYOFF groceries
// PAYOFF number
// LOOP close why_only_me: Mara signed you up for the alert
// LOOP close mara_knows: Mara worked at the power company
// TWIST: the alert reached only you because Mara put your number on the warning list last winter
@ rooftop.blackout | mara:point/sly@right | hero:stand/shocked@left | cam:push 1.06>1.20 | sfx:click
Thirty years at the power company, she says.
@ rooftop.blackout | mara:stand/relieved@right | hero:stand/shocked@left | cam:push 1.04>1.16 | sfx:click
Last winter, I put your number on the list. Someone had to wake up.
@ rooftop.dusk | hero:stand/relieved | mara:stand/neutral | cam:pull 1.22>1.06 | sfx:wind
The warning was free, and open to everyone.
@ rooftop.dusk | hero:stand/relieved | mara:stand/neutral | cam:parallax_drift 1.05>1.12 | sfx:wind
You were just the only one who signed up.
@ rooftop.dusk | hero:stand/determined | mara:stand/relieved | ov:end_screen("Next story: the dam nobody was watching") | cam:hold | sfx:stinger_chapter
Everything you learned fits on one notepad. The city is dark. And next time, you will be ready.
