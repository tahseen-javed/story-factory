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

## CH1 | FRIDAY 6:33 PM
// RITUAL tracker: the survival log opens every chapter
// ACT hook
// LOOP open never_drive: you swore you would never drive again
@ apartment.night | hero:phone_hold/scared | ov:label_tag("BATTERY 1%") | fx:flicker | sfx:beep,heartbeat | track:{hours:0,phone:"1%",water:"6 L",cash:"$40"}
Friday, six thirty-three p.m. Your phone says one percent, and the whole city is dark.
@ street.night | fx:dust | sfx:wind
Not one window is lit.
@ rooftop.blackout | hero:stand/scared | ov:timer("00:09:00","MARA'S OXYGEN") | sfx:heartbeat,ticking_clock
And two floors down, Mara's oxygen machine has nine minutes of battery left.
// SILENCE
// INTERRUPT silence
@ rooftop.blackout | hero:stand/determined | sfx:wind
To save her, you must do the one thing you swore you would never, ever do again.
@ rooftop.blackout | hero:stand/sad | banner:"15 HOURS EARLIER" | sfx:whoosh
Fifteen hours earlier, it was just a quiet Friday. Why did only your phone see this coming?
// ACT act1
@ hallway.night | hero:stand/shocked | fx:alarm_pulse | sfx:door_knock,alert_siren
Three twelve a.m. Your phone screams, and you pound on Mara's door.
@ hallway.night | hero:stand/worried | mara:stand/neutral | sfx:door_creak
She opens it, an oxygen line under her nose, calm as a clock.
@ apartment.alarm | hero:phone_hold/shocked | ov:phone_alert("EMERGENCY ALERT","Severe space weather. Impact in 15 hours") | fx:alarm_pulse | sfx:alert_siren,phone_buzz | track:{hours:15,phone:"38%",water:"6 L",cash:"$40"}
A storm from the Sun is coming, and it lands in fifteen hours.
@ apartment.alarm | hero:stand/worried | ov:label_tag("15-18 HOURS") | sfx:click
The fastest ones reach Earth in just fifteen to eighteen hours.
@ apartment.alarm | hero:stand/scared | ov:label_tag("G5 = EXTREME") | sfx:click
At the top level, a G five, whole power grids can collapse.
// INTERRUPT surprise
@ hallway.night | hero:stand/worried | mara:stand/sad | sfx:rustle
In 1989, one storm blacked out Quebec for nine hours.
// PLANT groceries: you carried Mara's groceries last winter
@ hallway.night | hero:stand/worried | mara:point/determined | ov:timer("04:00:00","MARA'S BACKUP BATTERY") | sfx:ticking_clock
Mara's machine runs on wall power, with a backup that lasts four hours. Four hours, then nothing.
// ACT act2a
@ hallway.night | hero:stand/determined | sfx:heartbeat
There is only one way to keep it running. A car.
// CLIFF
@ apartment.night | hero:sit_bed/scared | sfx:wind
And your car has sat dead in the garage for two years.
// LOOP open why_only_me: why did only your phone get the warning

## CH2 | FRIDAY 9:05 AM
// RITUAL tracker: the survival log opens every chapter
@ apartment.day | hero:write/determined | ov:notepad_tracker("SURVIVAL LOG") | sfx:typing | track:{hours:9,phone:"38%",water:"6 L",cash:"$40"}
You write a list. Water. Cash. Fuel. Power for Mara.
@ apartment.day | hero:point/worried | ov:arrow_callout("1 gallon per person, per day","right") | sfx:click
Ready dot gov says one gallon of water, per person, per day.
@ hallway.day | hero:carry/determined | sfx:water_pour,footsteps
You fill every pot, then the bathtub, and drag the water down the hall.
// PLANT number: Mara asked for your phone number
@ hallway.day | hero:stand/neutral | mara:stand/sly | sfx:click
Mara watches you, almost smiling, like she planned this.
@ kitchen.day | hero:stand/worried | ov:paper_bar_chart("HOW LONG FOOD STAYS COLD","Fridge=4","Full freezer=48") | sfx:paper_slide
A closed fridge keeps food cold for four hours. A full freezer, forty-eight.
// INTERRUPT joke
@ kitchen.day | hero:stand/neutral | sfx:click
You eat all the ice cream first. Survival has rules.
@ kitchen.day | hero:point/determined | cta:subscribe | sfx:click
If you want more stories where the clock is real, subscribe.
@ street.day | hero:walk/determined | ov:dashed_path("Home","Gas station") | sfx:footsteps,wind
Now you walk to the gas station, forty dollars in your pocket.
@ street.day | hero:stand/worried | fx:dust | sfx:wind
A man on the corner laughs. The Sun? Please. Nobody here believes the warning.
// LOOP open nobody_listens: the neighbours do not believe the warning
@ street.day | hero:stand/relieved | sfx:radio_static
Then a hand-crank radio in a shop window crackles with a weather tone. The storm is real, and confirmed.
// INTERRUPT scene
@ gas_station.day | hero:stand/neutral | sfx:click
Cash only, the clerk says, and he sells you the last inverter on the shelf.
@ gas_station.day | hero:stand/neutral | ov:receipt("CORNER GAS","Inverter   $24.00","Fuel can   $13.00","TOTAL   $37.00") | sfx:click
An inverter and a fuel can. Thirty-seven dollars. That is the plan.
// ACT midpoint
// INTERRUPT surprise
@ gas_station.day | hero:stand/shocked | fx:glitch | sfx:power_down
Then the pumps die. Every screen goes black.
@ gas_station.day | hero:hands_up/scared | sfx:radio_static
The clerk shrugs. Pumps need electricity, and the grid just fell, early.
@ gas_station.day | hero:stand/worried | sfx:rustle
Ready dot gov says to keep your tank half full. Yours is nearly empty. Behind you, the shelves empty in minutes.
// CLIFF
@ street.day | hero:run/scared | ov:phone_alert("UPDATE","Impact moved up: 3 hours") | sfx:alert_siren,footsteps
Your phone buzzes. The storm is coming six hours sooner.
// LOOP open grid_falls: the lights go out before the storm should arrive

## CH3 | FRIDAY 3:00 PM
// RITUAL tracker: the survival log opens every chapter
// ACT act2b
@ stairwell.day | hero:run/scared | fx:flicker | sfx:footsteps | track:{hours:3,phone:"9%",water:"6 L",cash:"$3"}
Three hours left. The elevator is dead, so you take the stairs.
@ stairwell.day | hero:stand/worried | sfx:crowd_murmur
On the second floor, scared neighbours block the stairs, all asking what you know.
@ hallway.day | hero:stand/worried | mara:stand/sad | sfx:rustle
Mara is sitting by her door, tired, her breathing short. She pats your hand. Leave me, she whispers. Save your water.
// ACT sacrifice
// INTERRUPT surprise
@ hallway.day | hero:stand/determined | mara:stand/sad | ov:numbered_circle(3,"HOURS LEFT") | sfx:click
Your forty dollars was your own water and food. It is gone. She matters more.
// BEAT emotional: you sit with Mara in the dark and share the last water
// INTERRUPT scene
@ kitchen.blackout | hero:sit/sad | mara:sit/sad | fx:flicker | sfx:wind
Then six twelve p.m. The lights die. The whole building goes silent.
@ kitchen.blackout | hero:sit/sad | mara:sit/sad | sfx:water_pour
You sit with Mara in the dark and share your last bottle of water.
@ stairwell.blackout | hero:carry/scared | fx:glitch | sfx:power_down,heartbeat
Mara's backup battery wakes up, beeping. Thirty minutes. That is all.
// SILENCE
@ stairwell.blackout | hero:carry/determined | mara:stand/scared | sfx:footsteps,heartbeat
You carry the machine down three floors in the dark, your last one percent lighting the steps.
@ stairwell.blackout | hero:carry/scared | sfx:heartbeat
Seven minutes. Your arms burn, and every landing feels a mile long.
// ACT climax
@ hallway.blackout | hero:run/scared | ov:timer("00:06:00","MARA'S OXYGEN") | sfx:footsteps
Flashlight beams shake across the walls. Six minutes. The garage door will not open.
@ hallway.blackout | hero:crouch/scared | sfx:rustle
You pull the manual release with both hands.
@ hallway.blackout | hero:stand/scared | sfx:wind
A car running in a closed garage can poison you. You have to drive it out.
// INTERRUPT silence
@ street.blackout | hero:stand/determined | sfx:car_engine
Your hands shake. Two years of dust, and one turn of the key. The car shudders, coughs, and for one second, nothing.
// PAYOFF groceries
// PAYOFF number
@ street.blackout | hero:stand/determined | mara:stand/relieved | sfx:car_engine,heartbeat
The engine catches. Your inverter hums. Mara's machine breathes again, with one minute to spare. She squeezes your hand, and her breathing slows.
// ACT resolution
// LOOP close never_drive: you drove, for her
@ rooftop.dusk | hero:stand/relieved | mara:stand/relieved | sfx:wind
By sunrise, the whole street is sharing candles, water and radios. Nobody is alone. The storm passes, and the grid takes days to wake up.
// LOOP close why_only_me: Mara signed you up for the alert
// SILENCE
@ rooftop.dusk | hero:stand/shocked | mara:stand/sly | sfx:click
Mara used to work at the power company. Last winter, you carried her groceries, and she wrote your number on the warning list.
// TWIST: the alert reached only you because Mara put your number on the warning list last winter
@ rooftop.dusk | hero:stand/relieved | mara:stand/relieved | sfx:wind
You thought the alert woke you to save yourself. Mara made sure you would be awake, to save her.
