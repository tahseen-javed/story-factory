TITLE: Three Logbooks and One Forgery
LENGTH_MIN: 9
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=navy, hat=cap, hair=short, skin=tan)
- maisie = rig_hero(outfit=mustard, hair=curly, skin=light)
- amos = rig_hero(outfit=olive, age=old, hat=cap, hair=short, skin=brown)
LOCATIONS:
- dock: small stone landing stage on a rocky island at dusk, wet stone steps, an iron mooring ring, thick grey fog rolling in, a white lighthouse tower fading into the fog, calm dark water
- door: heavy blue wooden door at the base of a white lighthouse tower, brass lamp bracket, wet stone step, evening fog, warm lantern glow spilling out
- stairs: inside a lighthouse tower, curling iron staircase with a handrail winding upward, round whitewashed wall, small round windows, warm lantern light
- lamp: lighthouse lantern room at the top of a tower, large glass lens in the middle, curved glass windows showing dark fog, a brass oil burner, one cracked pane, iron floor
- burner: close view of an old brass oil burner with a round glass chimney and a glowing wick flame, a fuel tank with a round gauge dial and needle, warm light
- gallery: narrow iron balcony railing outside a lighthouse lantern room at night, dark sea and fog far below, a hand signal lamp with green glass on a stand, windy
- desk: old wooden keeper's desk with a brass lamp, three logbooks (one green, one red, one black leather), a pencil jar and a tea mug, warm light
- radio: small marine radio on a wooden shelf with dials and a coiled cable, a tin mug beside it, a window with fog behind, dim warm light
- reef: dark sea at night with jagged black rocks and a leaning iron post carrying a small ship's bell, pale fog and white foam
- cave: sea cave on the east cliffs at night, wet rocks, rising water at the entrance, a small torch glow flashing in the dark, seals on a ledge
- slipway: stone slipway at the foot of a lighthouse at night, two wooden posts, lanterns glowing one high and one low, black water and fog, a small wooden rowing boat
- ferry: huge pale night ferry with rows of tiny lit windows swinging away in thick fog beside black rocks, white wake foam, a green light on its side
- harbour: calm harbour at dawn with a coastguard boat, pink and gold sky, still water, a white lighthouse tower in the distance, soft mist
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: mystery
- CH4: tense
- CH5: tense

## CH1 | SIX IN THE EVENING
// ACT hook
@ desk.night | fr:insert,closeup | fx:flicker | sfx:wind | cam:push 1.00>1.15
You have three logbooks,
@ burner.night | fr:insert,low | cam:push 1.05>1.20 | track:{oil:"4H"}
four hours of lamp oil,
@ desk.night | hero:point/shocked | fr:closeup,low | sfx:heartbeat | cam:pull 1.18>1.02
and one forgery.
@ lamp.night | hero:look_up/determined | fr:wide,low | fx:smoke | cam:tilt_up
By sunrise, you will know who forged it, and why.
@ dock.dusk | hero:stand/worried | fr:wide,low | fx:smoke | cam:push 1.00>1.14
The supply boat drops you on Gull Rock at six in the evening,
@ dock.dusk | hero:look_up/determined | fr:closeup,back | fx:smoke | cam:pan_l
just as the fog rolls in like wet wool.
// ACT act1
@ dock.dusk | hero:point/neutral | fr:medium,ots | fx:smoke | cam:pull 1.18>1.02
You are a relief keeper.
@ dock.dusk | hero:reach/worried | fr:closeup,profile | fx:smoke | cam:tilt_up
Your training was on modern lights, the kind that switch themselves on.
@ dock.dusk | hero:stand/determined | fr:xwide,wide | fx:smoke | cam:pan_r
This one is older than your grandparents.
@ radio.dusk | fr:insert,closeup | sfx:radio_static | cam:push 1.05>1.20
Its keeper, Amos Kettle, seventy-nine, has not answered the radio since lunch.
@ door.dusk | hero:look_up/neutral | maisie:shrug/neutral | fr:medium,closeup | fx:smoke | cam:parallax_drift
The door opens before you knock.
@ door.dusk | hero:point/worried | maisie:stand/worried | fr:low,wide | fx:smoke | cam:tilt_down
A girl of twelve, freckles, yellow raincoat, a lantern held in both hands.
@ reef.dusk | fr:insert,low | cam:pull 1.22>1.06
"I'm Maisie," she said. "Grandad rowed out at four to fix the reef bell.
@ door.dusk | hero:reach/determined | maisie:look_up/scared | fr:ots,wide | fx:smoke | cam:rack_focus
Then the fog came. He didn't come back."
@ dock.dusk | hero:stand/neutral | fr:closeup,ots | fx:smoke | cam:push 1.00>1.14
Behind you, the supply boat is already a grey shape, then nothing.
@ radio.dusk | fr:insert,wide | sfx:radio_static | cam:pan_l
The radio crackles once. "Storm closes the harbour tonight," a tired voice says.
@ dock.dusk | hero:look_up/worried | fr:wide,medium | fx:smoke | cam:pull 1.18>1.02
"We come at dawn. Not before."
@ lamp.night | hero:point/determined | fr:profile,medium | cam:tilt_up
Here is your clock. The electric lamp died with the generator.
@ burner.night | fr:insert,closeup | cam:push 1.05>1.20 | track:{oil:"4H"}
The backup is an old oil burner,
@ burner.night | fr:insert,closeup,low | cam:pan_r
and its tank holds four hours at full flame.
@ reef.night | fr:wide,low | cam:pull 1.18>1.02 | track:{ferry:"5H"}
The night ferry passes the reef at eleven, five hours from now.
@ lamp.night | hero:reach/neutral | fr:back,wide | cam:push 1.05>1.20
Dawn is at seven. And somewhere in the fog
@ lamp.night | hero:stand/worried | fr:closeup,low | cam:parallax_drift
is an old man in a small wooden boat.
## CH2 | THE CRACKED PANE
@ stairs.night | hero:look_up/determined | maisie:shrug/shocked | fr:medium,wide | cam:tilt_down
You climb a hundred and twelve steps.
@ stairs.night | hero:point/neutral | maisie:shrug/neutral | fr:wide,low | cam:pull 1.22>1.06
Maisie talks the whole way up.
@ burner.night | fr:insert,closeup | cam:rack_focus
"The burner is slow," she said.
@ stairs.night | hero:reach/worried | fr:closeup,back | cam:push 1.00>1.14
"Twenty minutes from a glow to a real beam.
@ burner.night | fr:insert,low | cam:pan_l
Grandad says wind is what eats a flame, not time."
// ACT act2a
@ burner.night | fr:insert,wide | cam:pull 1.18>1.02
You strike a match. The wick catches.
@ lamp.night | hero:stand/determined | maisie:look_up/scared | fr:medium,ots | fx:dust | cam:tilt_up
Slowly, a gold glow swells into a beam,
@ lamp.night | hero:look_up/neutral | fr:closeup,profile | fx:dust | cam:pan_r
and the beam swings out across the water.
@ lamp.night | hero:point/worried | maisie:stand/worried | fr:xwide,wide | fx:dust | cam:push 1.05>1.20
Maisie cheers. It feels like winning.
@ lamp.night | fr:insert,closeup,low | sfx:wind | cam:parallax_drift
Then you hear it. A thin whistle.
@ lamp.night | fr:insert,closeup | sfx:wind | cam:tilt_down
One pane of the lantern room is cracked,
@ lamp.night | hero:reach/determined | maisie:look_up/scared | fr:medium,closeup | fx:dust | sfx:wind | cam:pull 1.22>1.06
and the west wind is pushing straight through.
@ burner.night | fr:insert,low | cam:rack_focus
The flame leans and roars.
@ burner.night | fr:insert,wide | cam:push 1.00>1.14
You check the gauge. It has dropped like a stone.
@ burner.night | fr:insert,closeup | fx:flicker | track:{oil:"2.5H"}
At this rate, oil for two and a half hours.
@ lamp.night | hero:stand/neutral | maisie:shrug/neutral | fr:low,wide | fx:dust | sfx:wind | cam:pan_l
The ferry is still five hours away.
@ lamp.night | hero:stand/worried | maisie:look_up/scared | fr:ots | ov:option_cards("FULL FLAME","PLUG THE PANE","LAMP OUT","1","glow,draught,star")
Freeze. Option one, burn full flame anyway,
@ lamp.night | hero:look_up/determined | maisie:shrug/shocked | fr:closeup | ov:option_cards("FULL FLAME","PLUG THE PANE","LAMP OUT","1","glow,draught,star")
because the ferry needs the brightest light you have.
@ lamp.night | hero:stand/worried | maisie:look_up/scared | fr:wide | ov:option_cards("FULL FLAME","PLUG THE PANE","LAMP OUT","2","glow,draught,star")
Option two, plug the cracked pane with Amos's heavy oilskin coat
@ lamp.night | hero:look_up/determined | maisie:shrug/shocked | fr:medium | ov:option_cards("FULL FLAME","PLUG THE PANE","LAMP OUT","2","glow,draught,star")
and turn the wick down to half.
@ lamp.night | hero:stand/worried | maisie:look_up/scared | fr:medium | ov:option_cards("FULL FLAME","PLUG THE PANE","LAMP OUT","3","glow,draught,star")
Option three, put the lamp out completely
@ lamp.night | hero:look_up/determined | maisie:shrug/shocked | fr:closeup | ov:option_cards("FULL FLAME","PLUG THE PANE","LAMP OUT","3","glow,draught,star")
and relight it the moment you hear the ferry's horn.
@ lamp.night | hero:stand/worried | maisie:look_up/scared | fr:wide | ov:option_cards("FULL FLAME","PLUG THE PANE","LAMP OUT","0","glow,draught,star") | fx:flicker
Pause the video. Decide now.
@ lamp.night | hero:look_up/determined | maisie:shrug/shocked | fr:ots | ov:option_cards("FULL FLAME","PLUG THE PANE","LAMP OUT","0","glow,draught,star")
Your oil keeps burning.
// HOLD decision 4.5
@ lamp.night | hero:look_up/worried | maisie:stand/worried | fr:ots,wide | fx:dust | cam:pull 1.18>1.02
You choose option two. The coat smells of salt and pipe smoke.
@ burner.night | fr:insert,closeup,low | cam:tilt_up
The whistle stops. The flame stands up straight
@ burner.night | fr:insert,closeup | cam:pan_r
and calm, and the gauge finally settles.
@ burner.night | fr:insert,closeup | track:{oil:"4.5H"} | cam:push 1.05>1.20
Oil for four and a half hours.
@ lamp.night | hero:point/determined | fr:closeup,ots | fx:dust | cam:parallax_drift
Just enough, if nothing goes wrong.
@ burner.night | fr:insert,low | cam:tilt_down
Full flame in that wind would have run dry before nine.
@ ferry.night | fr:insert,wide | cam:pull 1.22>1.06
And the horn plan? Remember Maisie on the stairs.
@ stairs.night | hero:reach/neutral | maisie:shrug/neutral | fr:wide,medium | cam:rack_focus
Twenty minutes from glow to beam.
@ ferry.night | fr:insert,closeup,low | cam:push 1.00>1.14
The ferry would be on the rocks before your light woke up.
@ lamp.night | hero:stand/worried | fr:profile,medium | cam:pan_l
You sit on the cold iron floor.
@ lamp.night | maisie:look_up/scared | fr:back,wide | cam:pull 1.18>1.02
Then Maisie lifts her head. "Listen," she said.
@ lamp.night | hero:look_up/determined | fr:wide,low | fx:flicker | cam:hold
Nothing. No sound at all.
@ reef.night | fr:insert,closeup | cam:tilt_up
The reef bell has stopped.
@ lamp.night | maisie:shrug/neutral | fr:closeup,low | cam:pan_r
"It never stops," she whispers.
@ lamp.night | hero:reach/worried | maisie:stand/worried | fr:medium,wide | cam:push 1.05>1.20
"Not in a storm. Not ever."
## CH3 | SEVEN THIRTY
@ desk.night | fr:insert,wide | cam:push 1.05>1.20 | track:{oil:"<4H",ferry:"3H30"}
Seven thirty. Oil for under four hours.
@ desk.night | hero:stand/determined | maisie:look_up/scared | fr:wide,low | cam:parallax_drift
You need to know where Amos is.
@ desk.night | fr:insert,low | cam:tilt_down
Maisie pulls three logbooks from his desk.
@ desk.night | fr:insert,wide | cam:pull 1.22>1.06
A green one, the official log, neat blue ink,
@ desk.night | hero:look_up/neutral | fr:closeup,back | cam:rack_focus
every day signed "All well, A. Kettle."
@ desk.night | fr:insert,closeup,low | cam:push 1.00>1.14
A red one, his own diary, written in huge, shaky pencil letters.
@ lamp.night | fr:insert,closeup | sfx:wind | cam:pan_l
And a black one, cracked leather, his father's book from long ago,
@ desk.night | hero:point/worried | maisie:stand/worried | fr:medium,ots | cam:pull 1.18>1.02
full of drawings of the reef and the caves.
@ reef.night | fr:insert,low | cam:tilt_up
The red diary, today: "Bell clapper loose.
@ desk.night | hero:reach/determined | fr:closeup,profile | cam:pan_r
Fix at low water." Below it,
@ desk.night | hero:stand/neutral | maisie:shrug/neutral | fr:xwide,wide | cam:push 1.05>1.20
a tide note. "High water eight. North reef drowns."
@ gallery.night | hero:look_up/worried | maisie:stand/worried | fr:medium,closeup | fx:smoke | cam:parallax_drift
On the gallery rail sits a hand signal lamp with a green glass filter.
@ gallery.night | hero:point/determined | maisie:look_up/scared | fr:low,wide | fx:smoke | cam:tilt_down
It throws a narrow beam.
@ gallery.night | hero:reach/neutral | maisie:shrug/neutral | fr:ots,wide | fx:smoke | cam:pull 1.22>1.06
You can search one direction. Only one.
@ gallery.night | hero:stand/worried | maisie:look_up/worried | fr:ots | ov:option_cards("NORTH REEF","SEAL CAVE","SOUTH SLIPWAY","1","ledge,arch,rope")
Freeze. Option one, the north reef, because that is
@ gallery.night | hero:look_up/determined | maisie:shrug/determined | fr:closeup | ov:option_cards("NORTH REEF","SEAL CAVE","SOUTH SLIPWAY","1","ledge,arch,rope")
where the bell is and where he said he would go.
@ gallery.night | hero:stand/worried | maisie:look_up/worried | fr:wide | ov:option_cards("NORTH REEF","SEAL CAVE","SOUTH SLIPWAY","2","ledge,arch,rope")
Option two, the seal cave on the east side, out of the wind.
@ gallery.night | hero:look_up/determined | maisie:shrug/determined | fr:medium | ov:option_cards("NORTH REEF","SEAL CAVE","SOUTH SLIPWAY","3","ledge,arch,rope")
Option three, the south slipway, because surely he would try to row home.
@ gallery.night | hero:stand/worried | maisie:look_up/worried | fr:wide | ov:option_cards("NORTH REEF","SEAL CAVE","SOUTH SLIPWAY","0","ledge,arch,rope") | fx:flicker
Pause the video. Decide now.
@ gallery.night | hero:look_up/determined | maisie:shrug/determined | fr:ots | ov:option_cards("NORTH REEF","SEAL CAVE","SOUTH SLIPWAY","0","ledge,arch,rope")
The tide keeps rising.
// HOLD decision 4.5
@ gallery.night | hero:stand/worried | fr:closeup,ots | fx:smoke | cam:rack_focus
You choose option two. The wind is from the west.
@ lamp.night | fr:insert,wide | sfx:wind | cam:push 1.00>1.14
The cracked pane taught you that.
@ gallery.night | hero:look_up/determined | maisie:look_up/scared | fr:wide,medium | fx:smoke | cam:pan_l
A man in a small boat hides from it on the east side.
@ gallery.night | hero:point/neutral | fr:profile,medium | fx:smoke | cam:pull 1.18>1.02
The north reef drowns at eight.
@ gallery.night | hero:reach/worried | fr:back,wide | fx:smoke | cam:tilt_up
And rowing home against that wind, blind in this fog,
@ gallery.night | hero:stand/determined | fr:closeup,low | fx:smoke | cam:pan_r
is something a fifty-year keeper would never do.
@ gallery.night | hero:look_up/neutral | maisie:shrug/neutral | fr:medium,wide | fx:smoke | cam:push 1.05>1.20
You aim the lamp at the east cliffs and flash. Once. Twice.
@ cave.night | fr:insert,closeup,low | fx:flicker
Darkness. Then, small and stubborn, a torch blinks back. Three times.
@ gallery.night | hero:point/worried | maisie:stand/worried | fr:wide,low | fx:smoke | cam:parallax_drift
Maisie grips the rail and laughs
@ gallery.night | hero:reach/determined | fr:closeup,back | fx:smoke | cam:tilt_down
and cries a little, all at the same time.
@ gallery.night | hero:stand/neutral | maisie:shrug/neutral | fr:medium,ots | fx:smoke | cam:pull 1.22>1.06
If you found him, you think like a keeper.
@ gallery.night | hero:look_up/worried | fr:closeup,profile | fx:smoke | cam:rack_focus
If you didn't, stay with us, because the hardest freeze hasn't happened yet.
@ gallery.night | hero:stand/relieved | maisie:stand/relieved | fr:medium,closeup | cam:push 1.05>1.20 | cta:subscribe
Subscribe so this light keeps finding you.
## CH4 | THE GREEN LOG
// ACT midpoint
@ desk.night | hero:point/determined | maisie:look_up/scared | fr:xwide,wide | cam:push 1.00>1.14
You go back to the desk to see
@ cave.night | fr:insert,closeup | fx:flicker
what the black book says about the seal cave.
@ desk.night | fr:insert,low | cam:pan_l
But something bothers you. The green log. Neat ink.
@ desk.night | hero:reach/neutral | maisie:shrug/neutral | fr:medium,closeup | cam:pull 1.18>1.02
A steady hand. Every single day, "All well."
@ desk.night | hero:stand/worried | maisie:stand/worried | fr:low,wide | cam:tilt_up
Amos writes in huge, shaky pencil.
@ desk.night | fr:insert,wide | cam:pan_r
Every page of the red diary proves it. "Maisie," you say.
@ desk.night | fr:insert,closeup,low | cam:push 1.05>1.20
"Who writes the green log?"
@ desk.night | hero:look_up/determined | maisie:look_up/scared | fr:ots,wide | cam:parallax_drift
She looks at the floor for a long time. "Me," she said. "Since spring.
@ desk.night | hero:point/neutral | fr:closeup,ots | cam:tilt_down
His hands got bad. If the mainland knew,
@ desk.night | hero:reach/worried | maisie:stand/worried | fr:wide,medium | cam:pull 1.22>1.06
they'd move him to a home in town.
@ desk.night | hero:stand/determined | fr:profile,medium | cam:rack_focus
He'd hate it. So I copy his name.
@ desk.night | hero:look_up/neutral | fr:back,wide | cam:push 1.00>1.14
And I keep the light."
@ desk.night | hero:stand/shocked | fr:medium,ots | cam:pull 1.18>1.02
You thought you came to help an old keeper.
@ desk.night | maisie:look_up/determined | fr:closeup,low | sfx:stinger_chapter | cam:push 1.05>1.25
The real keeper is twelve.
// ACT act2b
@ burner.night | fr:insert,low | cam:push 1.05>1.20 | track:{oil:"30M",ferry:"20M"}
Ten forty. Oil for thirty minutes at half wick, fifteen at full.
@ ferry.night | fr:insert,closeup | cam:pan_l
The ferry is due at eleven.
@ lamp.night | hero:point/worried | fr:closeup,low | fx:flicker
Then three things happen at once.
@ lamp.night | hero:reach/determined | maisie:look_up/scared | fr:medium,wide | fx:flicker
In the window, a green light glides slowly to the left.
@ ferry.night | fr:insert,low | cam:pull 1.18>1.02
From the west, a long, low horn.
@ reef.night | fr:insert,wide | cam:tilt_up
And out on the reef, the bell starts ringing again,
@ lamp.night | hero:stand/neutral | maisie:shrug/neutral | fr:wide,low | fx:flicker
fast, faster than you have ever heard it.
@ lamp.night | maisie:stand/worried | fr:closeup,back | fx:flicker
Maisie told you something on the stairs, hours ago, between a hundred other things.
@ reef.night | fr:insert,closeup,low | cam:pan_r
"The bell rings fast when something big pushes the water past it."
@ lamp.night | hero:stand/scared | maisie:look_up/scared | fr:ots | ov:option_cards("FLAME AND GREEN","WAIT FOR HORN","FLAME FOR BELL","1","glow,star,wind")
Freeze. Option one, full flame now, and follow the green light.
@ lamp.night | hero:look_up/shocked | maisie:shrug/shocked | fr:wide | ov:option_cards("FLAME AND GREEN","WAIT FOR HORN","FLAME FOR BELL","2","glow,star,wind")
Option two, wait until the horn sounds louder and closer.
@ lamp.night | hero:stand/scared | maisie:look_up/scared | fr:medium | ov:option_cards("FLAME AND GREEN","WAIT FOR HORN","FLAME FOR BELL","3","glow,star,wind")
Option three, full flame now, because of the bell.
@ lamp.night | hero:look_up/shocked | maisie:shrug/shocked | fr:wide | ov:option_cards("FLAME AND GREEN","WAIT FOR HORN","FLAME FOR BELL","0","glow,star,wind") | fx:flicker
Pause the video. Decide now.
@ lamp.night | hero:stand/scared | maisie:look_up/scared | fr:ots | ov:option_cards("FLAME AND GREEN","WAIT FOR HORN","FLAME FOR BELL","0","glow,star,wind")
Something big is very close.
// HOLD decision 4.5
@ burner.night | fr:insert,closeup | cam:push 1.05>1.20
You choose option three. You turn the wick all the way up.
@ lamp.night | hero:point/determined | maisie:shrug/shocked | fr:medium,ots | fx:flicker
The beam blazes. Out in the fog,
@ ferry.night | fr:insert,low | cam:parallax_drift
a huge pale shape swings hard away, its wake hissing over the rocks.
@ ferry.night | fr:wide,low | cam:pull 1.18>1.02 | track:{ferry:"SAFE"}
The ferry. Two hundred metres from the reef.
@ ferry.night | fr:insert,wide | cam:tilt_down
The horn was the ferry too,
@ lamp.night | hero:reach/neutral | fr:closeup,profile | cam:pull 1.22>1.06
but fog bends sound, and the wind dragged it west.
@ lamp.night | hero:stand/worried | maisie:stand/worried | fr:xwide,wide | cam:rack_focus
And the green light? Look behind you.
@ lamp.night | hero:look_up/determined | maisie:look_up/scared | fr:medium,closeup | cam:push 1.00>1.14
Your own signal lamp, green filter still on,
@ lamp.night | hero:point/neutral | maisie:shrug/neutral | fr:low,wide | cam:pan_l
sitting on the shelf, reflected in the glass.
@ lamp.night | hero:reach/worried | maisie:stand/worried | fr:ots,wide | cam:pull 1.18>1.02
You were about to chase yourself.
@ radio.night | fr:insert,closeup,low | sfx:radio_static | cam:tilt_up
The radio crackles. "Gull Rock, thank you," a voice says.
@ lamp.night | hero:stand/determined | fr:closeup,ots | cam:pan_r
"We nearly didn't see you."
## CH5 | TEN FIFTY-FIVE
@ burner.night | fr:insert,low | fx:flicker | track:{oil:"5M"}
Ten fifty-five. Oil for five minutes.
// ACT sacrifice
@ cave.night | fr:insert,closeup | fx:flicker
Then the torch in the seal cave flashes again, fast and urgent.
@ gallery.night | hero:look_up/neutral | maisie:shrug/neutral | fr:wide,medium | fx:smoke | cam:push 1.05>1.20
High water is filling the cave.
@ gallery.night | hero:point/worried | fr:profile,medium | fx:smoke | cam:parallax_drift
Amos has to row out now, in darkness,
@ slipway.night | fr:insert,low | cam:tilt_down
around the reef, to the slipway below you.
@ desk.night | fr:insert,wide | cam:pull 1.22>1.06
You open the black book to its last page.
@ desk.night | hero:reach/determined | fr:back,wide | cam:rack_focus
A drawing, in his father's careful hand.
@ slipway.night | fr:insert,closeup,low | cam:push 1.00>1.14
Two lanterns at the slipway,
@ desk.night | hero:stand/neutral | fr:closeup,low | cam:pan_l
one high on the post, one low by the water.
@ desk.night | hero:look_up/worried | maisie:stand/worried | fr:medium,wide | cam:pull 1.18>1.02
Under it, one line. "The big light shows the danger.
@ desk.night | hero:point/determined | maisie:look_up/scared | fr:wide,low | cam:tilt_up
Two lights show the way.
@ desk.night | hero:reach/neutral | fr:closeup,back | cam:pan_r
Keep them in a line, and you are in the gap."
@ desk.night | hero:stand/scared | maisie:shrug/shocked | fr:ots | ov:option_cards("MAIN BEAM","SIGNAL LAMP","TWO LANTERNS","1","glow,star,chimney")
Freeze. Option one, keep the main beam blazing, so Amos can see the tower.
@ desk.night | hero:look_up/shocked | maisie:look_up/scared | fr:wide | ov:option_cards("MAIN BEAM","SIGNAL LAMP","TWO LANTERNS","2","glow,star,chimney")
Option two, flash the signal lamp at the cave,
@ desk.night | hero:stand/scared | maisie:shrug/shocked | fr:medium | ov:option_cards("MAIN BEAM","SIGNAL LAMP","TWO LANTERNS","2","glow,star,chimney")
so he knows you are still watching.
@ desk.night | hero:look_up/shocked | maisie:look_up/scared | fr:medium | ov:option_cards("MAIN BEAM","SIGNAL LAMP","TWO LANTERNS","3","glow,star,chimney")
Option three, carry two lanterns down to the slipway
@ desk.night | hero:stand/scared | maisie:shrug/shocked | fr:closeup | ov:option_cards("MAIN BEAM","SIGNAL LAMP","TWO LANTERNS","3","glow,star,chimney")
and set them one above the other.
@ desk.night | hero:look_up/shocked | maisie:look_up/scared | fr:wide | ov:option_cards("MAIN BEAM","SIGNAL LAMP","TWO LANTERNS","0","glow,star,chimney") | fx:flicker
Pause the video. Decide now.
@ desk.night | hero:stand/scared | maisie:shrug/shocked | fr:ots | ov:option_cards("MAIN BEAM","SIGNAL LAMP","TWO LANTERNS","0","glow,star,chimney")
His boat is already moving.
// HOLD decision 4.5
// ACT climax
@ stairs.night | hero:stand/worried | maisie:stand/worried | fr:medium,ots | cam:push 1.05>1.20
You choose option three. You and Maisie race down a hundred and twelve steps.
@ slipway.night | hero:look_up/determined | fr:closeup,profile | fx:smoke | cam:parallax_drift
One lantern on the post. One by the water.
@ slipway.blackout | hero:point/neutral | maisie:shrug/neutral | fr:xwide,wide | fx:smoke | cam:tilt_down
Behind you, high above, the main lamp coughs, flickers, and goes dark.
@ slipway.blackout | hero:reach/worried | maisie:stand/worried | fr:medium,closeup | fx:smoke | cam:pull 1.22>1.06
You wait in the wind.
@ slipway.blackout | fr:insert,closeup | cam:rack_focus
Then, out of the fog, the creak of oars. Slow. Steady.
@ slipway.blackout | hero:stand/determined | maisie:look_up/scared | fr:low,wide | fx:smoke | cam:push 1.00>1.14
And there he is, rowing straight through the gap in the reef,
@ slipway.blackout | hero:look_up/neutral | maisie:shrug/neutral | fr:ots,wide | fx:smoke | cam:pan_l
eyes fixed on two small lights in a line.
@ slipway.blackout | hero:point/worried | fr:closeup,ots | fx:smoke | cam:pull 1.18>1.02
The big beam would only have shown him the tower,
@ slipway.blackout | hero:reach/determined | maisie:look_up/scared | fr:wide,medium | fx:smoke | cam:tilt_up
and the tower stands behind the rocks.
@ slipway.blackout | hero:stand/neutral | fr:profile,medium | fx:smoke | cam:pan_r
A lighthouse tells you where not to go.
@ slipway.blackout | hero:look_up/worried | fr:back,wide | fx:smoke | cam:push 1.05>1.20
Only the lanterns could tell him where to go.
@ slipway.blackout | fr:insert,low | cam:parallax_drift
Amos climbs onto the slipway, soaked, grinning,
@ slipway.blackout | maisie:shrug/shocked | fr:closeup,low | cam:tilt_down
and pulls Maisie into a hug so tight her raincoat squeaks.
// ACT resolution
@ harbour.dusk | hero:reach/neutral | maisie:shrug/neutral | amos:shrug/relieved | fr:medium,wide | cam:pull 1.22>1.06
At dawn, the coastguard boat noses into the harbour.
@ desk.dusk | fr:insert,wide | cam:rack_focus
Before anyone climbs the steps, you open the green log,
@ desk.dusk | hero:stand/worried | fr:wide,low | cam:push 1.00>1.14
and in your own handwriting, you write the truth.
@ desk.dusk | hero:look_up/determined | fr:closeup,back | cam:pan_l
"Keeper's hands unsteady. Light kept for months by his granddaughter.
@ desk.dusk | hero:point/neutral | fr:medium,ots | cam:pull 1.18>1.02
Requesting a full-time assistant keeper. I volunteer."
@ desk.dusk | amos:stand/neutral | fr:closeup,profile | cam:tilt_up
Amos reads it twice. "You'd stay?" he said.
@ desk.dusk | hero:stand/determined | maisie:look_up/scared | amos:reach/worried | fr:xwide,wide | cam:pan_r
"Out here?" "Somebody has to keep the lanterns in a line," you said.
@ desk.dusk | hero:look_up/neutral | maisie:shrug/neutral | amos:shrug/relieved | fr:medium,closeup | cam:push 1.05>1.20
Maisie says nothing. She just takes your hand.
@ lamp.dusk | hero:point/worried | fr:low,wide | cam:parallax_drift
So think back. At the last freeze, with the main lamp dying,
@ lamp.dusk | hero:reach/determined | fr:ots,wide | cam:tilt_down
would you have walked away from the biggest light you had?
// LASTLINE
@ desk.dusk | fr:insert,closeup,low | cam:pull 1.22>1.06
Three logbooks. One forgery. And finally, one true entry.
@ desk.dusk | hero:stand/neutral | fr:closeup,ots | cam:rack_focus
Next time, the fog is thicker and the light itself is lying.
@ dock.dusk | hero:stand/determined | fr:wide,low | fx:smoke | cam:pull 1.18>1.02 | cta:subscribe
Subscribe, and keep your lantern lit.
