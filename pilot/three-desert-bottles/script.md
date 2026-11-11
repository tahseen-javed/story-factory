TITLE: The Bottle You Refuse
LENGTH_MIN: 8
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=plum, hair=short, skin=brown)
- pip = rig_hero(outfit=teal, hat=cap, hair=curly, skin=tan)
- gran = rig_hero(outfit=red, age=old, hair=bun, skin=light)
- abel = rig_hero(outfit=grey, age=old, hat=cap, hair=short, skin=dark)
LOCATIONS:
- road: long empty desert road under a harsh white sun, heat shimmer, orange sand and low rocks, a small broken-down car with its hood up and white steam, empty horizon
- cab: inside a small car, front seats and dashboard with a steering wheel, bright hot light through the windscreen, three bottles on the back seat, dusty glass
- seat: close view of a car back seat with three bottles: a blue metal flask, a big clear water bottle and a small glass bottle with a cork, hot bright light
- flask: close view of a blue metal flask with a screw cap and water drops, hot light, blurred sandy background
- cap: close view of a hand twisting the cap of a clear plastic bottle, the little plastic ring already broken, bright light
- phone: close view of a smartphone in a hand with a nearly empty battery icon and no signal bars, bright sun glare
- station: dusty roadside gas station with one old pump, a broken drinks cooler, a counter, a garden hose coiled in a bucket of empty bottles, sleepy afternoon light
- sign: sun-bleached wooden roadside sign leaning in the sand with a painted arrow, empty desert road behind, hot haze
- roof: top of a small car roof in the desert sun, one hand held high, wide empty desert horizon, bright sky
- shade: small car with all doors open and a silver windshield shade stretched across the back windows, cool blue shadow on the sand, two seats in the shadow
- dash: close view of a car dashboard with a temperature gauge needle leaning all the way to the red, steering wheel, warm dusty light
- hood: raised car hood showing the engine, a dry coolant tank with white crust around the rim, sun glare, tools on the sand
- sky: huge empty desert sky with heat haze, a lone hawk, still dust and shimmering sand, no wind
- drive: small car driving on a desert road with windows down, golden afternoon light, dust trail behind, a mile marker post
- house: small blue house at sunset with a front door and a porch, warm orange sky, desert plants, paper party decorations
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: tense
- CH4: tense
- CH5: mystery
- CH6: hopeful

## CH1 | TEN FORTY IN THE MORNING
// ACT hook
@ road.day | fr:xwide,wide | fx:dust | sfx:car_engine | cam:push 1.00>1.15
Your car dies on a desert road
@ seat.day | fr:insert,closeup | cam:push 1.05>1.20 | track:{water:"3 BOTTLES"}
with three bottles of water.
@ cab.day | hero:point/scared | fr:closeup,low | cam:pull 1.18>1.02
The one that saves you today
@ road.day | hero:stand/determined | pip:look_up/worried | fr:wide,low | cam:tilt_up
is the one you refuse to drink.
@ road.day | fr:xwide,wide | fx:dust | cam:pull 1.18>1.02 | track:{heat:"98F"}
It is ten forty in the morning,
@ road.day | hero:stand/worried | pip:stand/worried | fr:wide,low | fx:dust | cam:push 1.00>1.14
ninety-eight degrees, and the sun is still climbing.
@ phone.day | fr:insert,closeup | sfx:phone_buzz | cam:pan_l
Your phone shows no signal.
// ACT act1
@ road.day | fr:wide,low | fx:dust | cam:push 1.05>1.20 | track:{hours:"8"}
Sunset is eight hours away.
@ seat.day | fr:insert,low | cam:pull 1.18>1.02
Three bottles sit on the back seat,
@ road.day | hero:look_up/determined | fr:closeup,back | fx:dust | cam:tilt_up
and that is all the water there is.
@ cab.day | hero:point/neutral | pip:look_up/neutral | fr:medium,ots | fx:dust | cam:pan_r
Beside you sits Pip, your nervous new colleague, twenty-three,
@ cab.day | hero:reach/worried | fr:closeup,profile | fx:dust | cam:push 1.05>1.20
in a yellow cap with a cartoon cactus on it.
@ cab.day | hero:stand/determined | pip:shrug/scared | fr:xwide,wide | fx:dust | cam:parallax_drift
You offered to drive her to her grandmother's ninetieth birthday,
@ cab.day | hero:look_up/neutral | pip:look_up/neutral | fr:medium,closeup | fx:dust | cam:tilt_down
four hundred miles across nothing.
@ seat.day | fr:insert,wide | cam:pull 1.22>1.06
In her lap is a small glass bottle with a cork.
@ seat.day | fr:insert,closeup,low | cam:rack_focus
"Lemon and honey," she said. "Grandma's own recipe.
@ cab.day | hero:point/worried | pip:stand/worried | fr:low,wide | fx:dust | cam:push 1.00>1.14
It's her present, so hands off."
@ flask.day | fr:insert,closeup | cam:pan_l
The second bottle is your blue metal flask, half full.
@ seat.day | fr:insert,low | cam:pull 1.18>1.02
The third is a big clear bottle
@ cab.day | hero:reach/determined | pip:shrug/scared | fr:ots,wide | fx:dust | cam:tilt_up
you bought at the last gas station,
@ cab.day | hero:stand/neutral | fr:closeup,ots | fx:dust | cam:pan_r
the only one left on the shelf.
@ station.day | fr:insert,wide | cam:push 1.05>1.20
You remember that station well. A sleepy attendant. A broken cooler.
@ station.day | fr:insert,closeup,low | cam:parallax_drift
A garden hose curled into a
@ station.day | hero:look_up/neutral | abel:shrug/neutral | fr:wide,medium | fx:dust | cam:tilt_down
bucket of empty bottles behind the counter.
@ station.day | abel:stand/sly | fr:profile,medium | fx:dust | cam:pull 1.22>1.06
When you asked about the town ahead, he laughed. "Cobalt Springs?
@ station.day | hero:shrug/worried | fr:back,wide | fx:dust | cam:rack_focus
Closed when the mine closed.
@ station.day | hero:stand/worried | fr:closeup,low | fx:dust | cam:push 1.00>1.14
Just a water tower now."
@ hood.day | fr:insert,closeup | cam:pan_l
An hour later the engine coughed.
@ hood.day | fr:insert,low | cam:pull 1.18>1.02
A white hiss rose from under the hood.
@ road.day | hero:look_up/determined | pip:point/shocked | fr:medium,wide | fx:smoke | cam:tilt_up
The needle on the dashboard leaned all the way right,
@ road.day | hero:point/neutral | pip:look_up/neutral | fr:wide,low | fx:smoke | cam:pan_r
and then everything went quiet.
@ road.day | fr:xwide,wide | fx:dust | cam:pull 1.18>1.02 | track:{hours:"8",water:"3 BOTTLES"}
Eight hours of daylight. Three bottles. Zero bars.
## CH2 | ONE BAR
@ roof.day | hero:reach/worried | fr:closeup,back | fx:dust | cam:push 1.05>1.20
Then you find a trick.
@ phone.day | fr:insert,wide | sfx:phone_buzz | cam:parallax_drift
Standing on the roof, arm stretched high, one bar flickers.
@ roof.day | hero:stand/determined | pip:shrug/scared | fr:medium,ots | fx:dust | cam:tilt_down
You type fast. "Car dead on
@ roof.day | hero:look_up/neutral | fr:closeup,profile | fx:dust | cam:pull 1.22>1.06
Route 40 past mile marker 112."
@ roof.day | hero:point/worried | pip:stand/worried | fr:xwide,wide | fx:dust | cam:rack_focus
Sent. Pip cheers. You climb down feeling like a genius.
@ phone.day | fr:insert,closeup,low | sfx:phone_buzz | cam:push 1.00>1.14
Twenty minutes later the phone buzzes. Message failed.
@ phone.day | fr:insert,closeup | cam:push 1.05>1.20 | track:{phone:"11%"}
Battery eleven percent. Hunting for signal ate the rest.
@ cab.day | hero:reach/determined | pip:shrug/scared | fr:medium,closeup | fx:dust | cam:pan_l
Nobody knows where you are.
@ road.day | fr:wide,low | fx:dust | cam:pull 1.18>1.02 | track:{hours:"7.5",phone:"11%"}
Seven and a half hours left. Battery eleven percent.
## CH3 | NINE MILES
// ACT act2a
@ sign.day | fr:insert,closeup | cam:pull 1.18>1.02
Down the road, a sun-bleached sign leans in the sand.
@ sign.day | fr:insert,closeup | cam:push 1.05>1.20 | track:{town:"9 MI",station:"22 MI"}
Cobalt Springs, nine miles. Behind you,
@ station.day | fr:insert,low | cam:tilt_up
the gas station is twenty-two miles away.
@ road.day | hero:stand/neutral | pip:look_up/neutral | fr:low,wide | fx:dust | cam:pan_r
Pip is already tightening her laces.
@ sign.day | fr:insert,wide | cam:push 1.05>1.20
"Nine miles," she said. "We can do nine miles."
@ road.day | hero:stand/worried | pip:look_up/worried | fr:ots | ov:option_cards("WALK AHEAD","WALK BACK","STAY WITH CAR","1","chalk,rope,star")
Freeze. Option one, walk to Cobalt Springs,
@ road.day | hero:look_up/determined | pip:shrug/determined | fr:closeup | ov:option_cards("WALK AHEAD","WALK BACK","STAY WITH CAR","1","chalk,rope,star")
nine miles ahead, where the sign promises a town.
@ road.day | hero:stand/worried | pip:look_up/worried | fr:wide | ov:option_cards("WALK AHEAD","WALK BACK","STAY WITH CAR","2","chalk,rope,star")
Option two, walk back twenty-two miles to
@ road.day | hero:look_up/determined | pip:shrug/determined | fr:medium | ov:option_cards("WALK AHEAD","WALK BACK","STAY WITH CAR","2","chalk,rope,star")
the gas station you know is real.
@ road.day | hero:stand/worried | pip:look_up/worried | fr:medium | ov:option_cards("WALK AHEAD","WALK BACK","STAY WITH CAR","3","chalk,rope,star")
Option three, stay with the car
@ road.day | hero:look_up/determined | pip:shrug/determined | fr:closeup | ov:option_cards("WALK AHEAD","WALK BACK","STAY WITH CAR","3","chalk,rope,star")
and make it easy to find.
@ road.day | hero:stand/worried | pip:look_up/worried | fr:wide | ov:option_cards("WALK AHEAD","WALK BACK","STAY WITH CAR","0","chalk,rope,star") | fx:flicker
Pause the video. Decide now.
@ road.day | hero:look_up/determined | pip:shrug/determined | fr:ots | ov:option_cards("WALK AHEAD","WALK BACK","STAY WITH CAR","0","chalk,rope,star")
The sun is not waiting.
// HOLD decision 4.5
@ sign.day | fr:insert,closeup,low | cam:parallax_drift
You stay. The sign promises a town,
@ road.day | hero:look_up/worried | pip:stand/worried | fr:ots,wide | fx:dust | cam:tilt_down
but the attendant already told you the truth.
@ road.day | hero:point/determined | fr:closeup,ots | fx:dust | cam:pull 1.22>1.06
Cobalt Springs is a water tower and empty houses.
@ road.day | hero:reach/neutral | pip:look_up/neutral | fr:wide,medium | fx:dust | cam:rack_focus
Walking back means six hours in
@ flask.day | fr:insert,closeup | cam:push 1.00>1.14
full sun on half a flask.
@ road.day | hero:stand/worried | fr:profile,medium | fx:dust | cam:pan_l
A car is big, shiny and visible from the air.
@ road.day | hero:look_up/determined | fr:back,wide | fx:dust | cam:pull 1.18>1.02
Two walking people are dots.
@ sign.day | fr:insert,low | cam:tilt_up
The sign was older than the truth.
@ shade.day | hero:point/neutral | fr:closeup,low | fx:dust | cam:pan_r
You open every door for airflow
@ shade.day | fr:insert,wide | cam:push 1.05>1.20
and stretch the silver windshield shade across the back windows.
@ shade.day | fr:insert,closeup,low | cam:parallax_drift
Pip sits in the shadow, telling you about her grandad Harold,
@ shade.day | hero:reach/worried | pip:stand/worried | fr:medium,wide | fx:dust | cam:tilt_down
who drove a tow truck across this desert for thirty years.
@ shade.day | hero:stand/determined | pip:shrug/scared | fr:wide,low | fx:dust | cam:pull 1.22>1.06
His favourite story was a farmer
@ hood.day | fr:insert,closeup | cam:rack_focus
who poured cola into his radiator
@ hood.day | fr:insert,low | cam:push 1.00>1.14
and glued the whole engine shut.
@ shade.day | pip:look_up/neutral | fr:closeup,back | fx:dust | cam:pan_l
"Took Grandad a weekend to scrape it out," she said, smiling.
// ACT midpoint
@ sky.day | fr:insert,wide | cam:pull 1.18>1.02
Then the wind stops.
@ sky.day | hero:stand/worried | fr:wide,low | fx:flicker | cam:hold
Nothing. No sound at all.
@ sky.day | fr:insert,closeup,low | cam:tilt_up
No insects, no creak of metal. Only heat.
## CH4 | ONE IN THE AFTERNOON
@ shade.day | hero:look_up/determined | pip:stand/scared | fr:wide,low | fx:dust | cam:push 1.05>1.20 | track:{hours:"6",heat:"108F"}
Six hours left. It is one in the afternoon,
@ shade.day | hero:point/worried | pip:stand/worried | fr:medium,ots | fx:dust | cam:pan_r
a hundred and eight degrees, and Pip's voice has gone thin.
@ sky.day | fr:insert,closeup | cam:push 1.05>1.20
She says the sky is spinning
@ shade.day | pip:shrug/scared | fr:closeup,profile | fx:dust | cam:parallax_drift
a little. She needs water now.
@ shade.day | hero:stand/worried | pip:stand/scared | fr:ots | ov:option_cards("BIG BOTTLE","BLUE FLASK","LEMON HONEY","1","bottle,draught,star")
Freeze. Option one, the big clear bottle,
@ shade.day | hero:look_up/determined | pip:look_up/shocked | fr:closeup | ov:option_cards("BIG BOTTLE","BLUE FLASK","LEMON HONEY","1","bottle,draught,star")
full to the top, the most water you have.
@ shade.day | hero:stand/worried | pip:stand/scared | fr:wide | ov:option_cards("BIG BOTTLE","BLUE FLASK","LEMON HONEY","2","bottle,draught,star")
Option two, your blue flask, half full and warm as tea.
@ shade.day | hero:look_up/determined | pip:look_up/shocked | fr:medium | ov:option_cards("BIG BOTTLE","BLUE FLASK","LEMON HONEY","3","bottle,draught,star")
Option three, the lemon and honey,
@ shade.day | hero:stand/worried | pip:stand/scared | fr:closeup | ov:option_cards("BIG BOTTLE","BLUE FLASK","LEMON HONEY","3","bottle,draught,star")
sweet and small and saved for Grandma.
@ shade.day | hero:look_up/determined | pip:look_up/shocked | fr:wide | ov:option_cards("BIG BOTTLE","BLUE FLASK","LEMON HONEY","0","bottle,draught,star") | fx:flicker
Pause the video. Decide now.
@ shade.day | hero:stand/worried | pip:stand/scared | fr:ots | ov:option_cards("BIG BOTTLE","BLUE FLASK","LEMON HONEY","0","bottle,draught,star")
She is waiting for your hand.
// HOLD decision 4.5
@ seat.day | fr:insert,low | cam:tilt_down
Your hand goes to the big bottle. Then it stops.
@ cap.day | fr:insert,wide | sfx:click | cam:pull 1.22>1.06
You twist the cap. It turns too easily.
@ shade.day | hero:stand/neutral | pip:look_up/neutral | fr:xwide,wide | fx:dust | cam:rack_focus
No crack, no snap of the plastic ring.
@ seat.day | fr:insert,closeup,low | cam:push 1.00>1.14
Someone opened this bottle before you.
@ station.day | fr:insert,closeup | cam:pan_l
And you remember the hose, the bucket,
@ shade.day | hero:look_up/worried | pip:stand/worried | fr:medium,closeup | fx:dust | cam:pull 1.18>1.02
the empty bottles behind the counter.
@ shade.day | hero:point/determined | pip:shrug/scared | fr:low,wide | fx:dust | cam:tilt_up
This is refilled water from who knows where.
@ flask.day | fr:insert,low | cam:pan_r
You give Pip the flask. Small sips.
@ shade.day | hero:reach/neutral | pip:look_up/neutral | fr:ots,wide | fx:dust | cam:push 1.05>1.20
Ten minutes later the colour comes back into her cheeks
@ shade.day | pip:stand/worried | fr:closeup,ots | fx:dust | cam:parallax_drift
and she complains it tastes like a spoon,
@ shade.day | hero:look_up/determined | pip:shrug/scared | fr:wide,medium | fx:dust | cam:tilt_down
which means she is fine.
@ shade.day | hero:point/neutral | fr:profile,medium | fx:dust | cam:pull 1.22>1.06
A seal that does not crack has already been broken.
@ shade.day | pip:stand/worried | fr:back,wide | fx:dust | cam:rack_focus
Pip squeezes your arm. "You're a careful one," she said.
@ shade.day | pip:shrug/scared | fr:closeup,low | fx:dust | cam:push 1.00>1.14
"Grandad would have liked you."
@ flask.day | fr:insert,wide | cam:pan_l
If you chose the flask, you think like a survivor.
@ seat.day | fr:insert,closeup,low | cam:pull 1.18>1.02
If you grabbed the full bottle,
@ shade.day | hero:look_up/neutral | pip:look_up/neutral | fr:medium,wide | fx:dust | cam:tilt_up
stay close, the next freeze is meaner.
@ shade.day | hero:stand/relieved | pip:stand/relieved | fr:medium,closeup | cam:push 1.05>1.20 | cta:subscribe
Subscribe so the next story finds you.
## CH5 | THE NEEDLE
@ dash.day | fr:insert,low | cam:push 1.05>1.20 | track:{hours:"5",flask:"3 SIPS"}
Five hours left. The flask is down to three sips.
@ shade.day | hero:point/worried | pip:stand/worried | fr:wide,low | fx:dust | cam:pan_r
Pip keeps talking about Harold.
@ shade.day | hero:reach/determined | fr:closeup,back | fx:dust | cam:push 1.05>1.20
He carried a mirror in his pocket
@ shade.day | hero:stand/neutral | pip:look_up/neutral | fr:medium,ots | fx:dust | cam:parallax_drift
and a joke for every breakdown.
@ shade.day | pip:stand/worried | fr:closeup,profile | fx:dust | cam:tilt_down
Then she stops mid-sentence
@ dash.day | fr:insert,closeup | cam:pull 1.22>1.06
and points through the open door at the dashboard.
@ dash.day | fr:insert,low | cam:rack_focus
"That needle," she said. "When did it climb?"
@ shade.day | hero:point/determined | pip:shrug/scared | fr:xwide,wide | fx:dust | cam:push 1.00>1.14
Before the engine stopped, you tell her. Long before.
@ shade.day | hero:reach/neutral | pip:look_up/neutral | fr:medium,closeup | fx:dust | cam:pan_l
She laughs, a dry little laugh.
@ dash.day | fr:insert,wide | cam:pull 1.18>1.02
"Grandad always said, when that needle climbs,
@ hood.day | fr:insert,closeup,low | cam:tilt_up
the engine isn't dead. It's thirsty."
// ACT act2b
@ hood.day | hero:stand/worried | pip:stand/worried | fr:low,wide | fx:dust | cam:pan_r
Everything you believed flips. You thought the car was finished.
@ hood.day | fr:insert,closeup | cam:push 1.05>1.20
It was only overheated. It does not need a mechanic.
@ hood.day | hero:look_up/determined | pip:shrug/scared | fr:ots,wide | fx:dust | cam:parallax_drift
It needs water and time to cool.
@ seat.day | fr:insert,low | cam:tilt_down
And you have three kinds of water,
@ hood.day | hero:point/neutral | fr:closeup,ots | fx:dust | cam:pull 1.22>1.06
and two people who still need to drink.
## CH6 | FOUR HOURS LEFT
// ACT sacrifice
@ shade.day | fr:wide,low | fx:dust | cam:pull 1.18>1.02 | track:{hours:"4"}
Four hours left. The hood is cooler now.
@ shade.day | fr:insert,wide | cam:rack_focus
You wait in the shade, counting minutes,
@ shade.day | fr:insert,closeup,low | cam:push 1.00>1.14
watching the shadow of the car
@ shade.day | hero:reach/worried | pip:stand/worried | fr:wide,medium | fx:dust | cam:pan_l
slowly grow longer across the sand.
@ sky.day | fr:insert,closeup | cam:pull 1.18>1.02
Somewhere far away, a hawk cries once
@ sky.day | fr:insert,low | cam:tilt_up
and then the silence closes again.
@ hood.day | pip:shrug/scared | fr:profile,medium | fx:dust | cam:pan_r
When Pip finally says it is time,
@ hood.day | fr:insert,wide | cam:push 1.05>1.20
you lift the hood together.
@ hood.day | fr:insert,closeup,low | cam:parallax_drift
The coolant tank underneath is bone dry,
@ hood.day | hero:look_up/neutral | fr:back,wide | fx:dust | cam:tilt_down
white crust around the rim like salt on an old boot.
@ hood.day | hero:stand/worried | pip:look_up/scared | fr:ots | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","1","draught,star,bottle")
Freeze. Option one, pour your last
@ hood.day | hero:look_up/determined | pip:shrug/shocked | fr:closeup | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","1","draught,star,bottle")
three sips from the clean flask,
@ hood.day | hero:stand/worried | pip:look_up/scared | fr:closeup | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","1","draught,star,bottle")
the only water you trust.
@ hood.day | hero:look_up/determined | pip:shrug/shocked | fr:wide | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","2","draught,star,bottle")
Option two, pour the lemon and honey,
@ hood.day | hero:stand/worried | pip:look_up/scared | fr:medium | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","2","draught,star,bottle")
the sweet bottle meant for Grandma.
@ hood.day | hero:look_up/determined | pip:shrug/shocked | fr:medium | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","3","draught,star,bottle")
Option three, pour the big full bottle,
@ hood.day | hero:stand/worried | pip:look_up/scared | fr:closeup | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","3","draught,star,bottle")
the one you refused to give her.
@ hood.day | hero:look_up/determined | pip:shrug/shocked | fr:wide | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","0","draught,star,bottle") | fx:flicker
Pause the video. Decide now.
@ hood.day | hero:stand/worried | pip:look_up/scared | fr:ots | ov:option_cards("LAST SIPS","LEMON HONEY","BIG BOTTLE","0","draught,star,bottle")
The shadows are getting longer.
// HOLD decision 4.5
// ACT climax
@ flask.day | fr:insert,closeup | cam:pull 1.22>1.06
Think back. The flask is clean,
@ seat.day | fr:insert,low | cam:rack_focus
but three sips will not fill anything,
@ hood.day | hero:point/worried | fr:closeup,low | fx:dust | cam:push 1.00>1.14
and you two still need it.
@ hood.day | fr:insert,wide | cam:pan_l
The honey would turn to glue inside a hot engine,
@ hood.day | hero:reach/determined | pip:shrug/scared | fr:medium,wide | fx:dust | cam:pull 1.18>1.02
just like the farmer's cola in Harold's story.
@ seat.day | fr:insert,closeup,low | cam:tilt_up
So you pour the full bottle. All of it.
@ hood.day | hero:stand/neutral | pip:look_up/neutral | fr:wide,low | fx:dust | cam:pan_r
Water that is wrong for a
@ hood.day | hero:look_up/worried | fr:closeup,back | fx:dust | cam:push 1.05>1.20
person can be perfect for a machine.
@ hood.day | fr:insert,closeup | cam:parallax_drift
You turn the key. The engine coughs. Coughs again.
@ cab.day | hero:point/determined | pip:shrug/scared | fr:medium,ots | fx:dust | cam:tilt_down
Then it roars, and Pip throws
@ roof.day | fr:insert,low | cam:pull 1.22>1.06
her cactus cap at the roof.
@ dash.day | fr:insert,closeup | cam:push 1.05>1.20 | track:{hours:"3",phone:"9%"}
Three hours left. Battery nine percent. Engine alive.
@ drive.day | hero:reach/neutral | fr:closeup,profile | fx:dust | cam:rack_focus
You drive with the windows down
@ dash.day | fr:insert,wide | cam:push 1.00>1.14
and the needle sitting politely in the middle.
@ drive.day | hero:stand/worried | pip:stand/worried | fr:xwide,wide | fx:dust | cam:pan_l
Near mile marker one hundred and fifty,
@ phone.day | fr:insert,closeup,low | sfx:phone_buzz | cam:pull 1.18>1.02
your phone finds two full bars,
@ drive.day | hero:look_up/determined | pip:shrug/scared | fr:medium,closeup | fx:dust | cam:tilt_up
and Pip calls her mother, laughing
@ drive.day | hero:point/neutral | pip:look_up/neutral | fr:low,wide | fx:dust | cam:pan_r
and crying at the same time.
// ACT resolution
@ house.dusk | hero:reach/worried | pip:stand/worried | gran:stand/neutral | fr:ots,wide | cam:push 1.05>1.20
At sunset you pull up to a small blue house.
@ house.dusk | gran:reach/worried | fr:closeup,ots | cam:parallax_drift
Grandma opens the door in a paper party hat.
@ seat.dusk | fr:insert,closeup | cam:tilt_down
Pip hands her the glass bottle,
@ house.dusk | hero:look_up/neutral | pip:look_up/neutral | gran:shrug/relieved | fr:wide,medium | cam:pull 1.22>1.06
still corked, still sweet, not one drop missing.
@ seat.dusk | fr:insert,low | cam:rack_focus
And now you see what the three bottles really were.
@ flask.dusk | fr:insert,wide | cam:push 1.00>1.14
The flask was for the people.
@ house.dusk | hero:point/worried | fr:profile,medium | cam:pan_l
The full bottle was for the car.
@ seat.dusk | fr:insert,closeup,low | cam:pull 1.18>1.02
The little glass bottle was never water at all.
@ house.dusk | hero:reach/determined | fr:back,wide | cam:tilt_up
It was the reason you were on that road.
@ house.dusk | gran:point/sad | fr:closeup,low | cam:pan_r
Grandma holds it to the light and smiles.
@ house.dusk | hero:look_up/worried | pip:stand/worried | gran:stand/neutral | fr:medium,wide | cam:push 1.05>1.20
"Your grandad would have poured the wrong one," she said.
// LASTLINE
@ seat.dusk | fr:insert,closeup | cam:parallax_drift
The bottle that saved you was the one you refused.
@ road.dusk | hero:point/determined | fr:wide,low | fx:dust | cam:tilt_down
So tell me honestly. At the last freeze,
@ seat.dusk | fr:insert,low | cam:pull 1.22>1.06
would you have poured the full bottle,
@ road.dusk | hero:reach/neutral | fr:closeup,back | fx:dust | cam:rack_focus
or kept it, just in case?
@ road.dusk | hero:stand/worried | fr:medium,ots | fx:dust | cam:push 1.00>1.14
Next time the water is clean and the map is lying.
@ road.dusk | hero:stand/determined | fr:wide,low | fx:dust | cam:pull 1.18>1.02 | cta:subscribe
Subscribe if you want to be there.
