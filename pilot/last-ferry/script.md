TITLE: Last Ferry
LENGTH_MIN: 4
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=coral, hat=beanie, hair=curly)
- kit = rig_hero(outfit=olive, hat=cap, hair=short, skin=brown)
LOCATIONS:
- dock: small island ferry pier at dusk with a wooden ticket hut, a big station clock, mooring ropes and a grey stormy sea
- street: narrow harbour village street with fishing cottages, stacked crates, rope coils and a stormy sky
- shelter: small harbour waiting shelter with a wooden bench, a kettle, a radio on a shelf and a window onto stormy waves
- rocks: rocky shore with a narrow stone jetty, crashing waves and a dark lighthouse on the headland
- skiff: small wooden rowing skiff with an outboard motor and a lantern on rough dark sea waves
- lighthouse: small lighthouse on a rocky headland at night with a bright beam sweeping across dark stormy waves
MUSIC_MOODS:
- CH1: tense
- CH2: urgent
- CH3: climax

## CH1 | 4:12 PM
// RITUAL tracker: the survival log opens every chapter
// ACT hook
// HOOKOPT 1 | Two hours until the storm. The last ferry leaves in nine minutes, and you are on the wrong side of the pier. Your phone says twelve percent. Your wallet says eighteen dollars. Finn, your brother, is twelve, alone on the island, and he just stopped answering. Why would he go quiet now?
// HOOKOPT 2 | Your brother is alone on an island, a storm is coming, and the last ferry is about to leave.
// HOOKOPT 3 | At four twelve, your brother stops answering his phone.
// HOOKPICK 1
// LOOP open why_silent: why did Finn stop answering
// LOOP open wrong_side: which side of the pier is the wrong one
@ dock.dusk | hero:run/scared | ov:timer("02:00:00","UNTIL STORM") | fx:rain | sfx:ticking_clock,wind | track:{hours:2,phone:"12%",water:"1 L",cash:"$18"}
Two hours until the storm. The last ferry leaves in nine minutes, and you are on the wrong side of the pier.
@ insert.night | ov:meter("battery","12%","PHONE") | fx:dust | sfx:beep
Your phone says twelve percent.
@ insert.night | ov:meter("cash","$18","CASH") | fx:dust | sfx:click
Your wallet says eighteen dollars.
@ dock.dusk | hero:phone_hold/worried | ov:phone_call("FINN","No answer") | fx:rain | sfx:phone_buzz
Finn, your brother, is twelve, alone on the island, and he just stopped answering.
// INTERRUPT silence
@ dock.dusk | hero:stand/scared | fx:rain | sfx:heartbeat
Why would he go quiet now?
// SILENCE
@ dock.dusk | hero:back_away/shocked | banner:"LAST FERRY 4:21 PM" | fx:rain | sfx:impact,wind
The ferry horn blows once. Nine minutes become eight.
// ACT act1
@ insert.dusk | ov:receipt("FERRY TICKET","Adult single   $20.00","You have   $18.00","SHORT   $2.00") | fx:dust | sfx:paper_slide
The ticket costs twenty dollars. You are two short.
@ dock.dusk | hero:stand/worried | kit:stand/neutral | fx:rain | sfx:click
Kit, the deckhand, checks his watch twice. Nobody boards without a full ticket.
// PLANT voicemail: Finn's unplayed voice message
@ dock.dusk | hero:phone_hold/sad | kit:stand/neutral | fx:rain | sfx:phone_buzz
You show him your phone. A missed call from Finn, and a voice message you have not played.
// INTERRUPT surprise
@ insert.night | ov:sticky_note("RULE 1","Be on that ferry") | fx:dust | sfx:paper_slide
Rule one: be on that ferry. Everything else can wait.
// PLANT lamp: the dark lighthouse
@ rocks.dusk | fx:rain | sfx:wind
Out on the rocks, the old lighthouse has been dark for years, ever since its keeper retired.
@ dock.dusk | hero:stand/determined | kit:stand/worried | fx:rain | sfx:rustle
Kit glances at the clock, then at you, and looks away. He lowers his voice. Find two dollars in eight minutes, and he will hold the ramp.
// ACT act2a
@ street.dusk | hero:run/determined | fx:rain | sfx:footsteps
You run into the village with eight minutes and one plan.
@ insert.night | ov:timer("00:08:00","UNTIL THE RAMP") | fx:dust | sfx:ticking_clock
Eight minutes is enough time for one very small miracle.
@ street.dusk | hero:stand/worried | fx:rain | sfx:crowd_murmur
Every shop is closing early. The shutters drop like eyelids.
@ insert.dusk | ov:label_tag("4:21 PM") | fx:dust | sfx:ticking_clock
The harbour clock says four twenty-one. You are running out of everything.
@ street.dusk | hero:reach/determined | fx:rain | sfx:rustle
A shopkeeper laughs at your eighteen dollars and your two-dollar problem.
@ street.dusk | hero:carry/determined | fx:rain | sfx:rustle
An old fisherman struggles with a tangle of rope. You drop your bag and help him, without asking for anything.
// INTERRUPT scene
@ street.dusk | hero:stand/relieved | fx:rain | sfx:click
He presses five dollars into your hand and says nothing.
@ insert.night | ov:meter("cash","$23","CASH") | fx:dust | sfx:click
Twenty-three dollars. Your small miracle came dressed as a fisherman.
// CLIFF
@ dock.dusk | hero:run/scared | fx:rain | sfx:impact,whoosh
Then the horn blows twice, and the ramp starts to rise.

## CH2 | 4:29 PM
// RITUAL tracker: the survival log opens every chapter
@ dock.dusk | hero:reach/scared | kit:stand/scared | fx:rain | sfx:footsteps,impact | track:{hours:2,phone:"9%",water:"1 L",cash:"$23"}
You reach the ramp with twenty-three dollars in your fist. Kit shakes his head.
// ACT midpoint
// INTERRUPT surprise
@ insert.alarm | ov:phone_alert("HARBOUR NOTICE","All sailings cancelled. Sea closed.") | fx:alarm_pulse | sfx:alert_siren,phone_buzz
The harbour master cancels every sailing. The storm has moved up, and the sea closes in one hour.
@ dock.alarm | hero:hands_up/shocked | kit:stand/sad | fx:alarm_pulse | sfx:alert_siren
Your plan is gone. The ferry is gone. Only the clock is left.
@ insert.night | ov:meter("battery","7%","PHONE") | fx:dust | sfx:beep
Seven percent. Finn's phone is still silent.
@ shelter.night | hero:sit/sad | kit:sit/neutral | cta:subscribe | fx:rain | sfx:rustle,wind
Kit hands you a cup of tea. If you ever need a story to wait out a storm, subscribe, and this one will wait with you.
@ shelter.night | hero:stand/determined | kit:stand/worried | fx:rain | sfx:radio_static
Kit says the sea closes like a shop, only louder, and almost smiles.
@ shelter.night | hero:stand/determined | kit:stand/worried | fx:rain | sfx:radio_static
Then he points at the radio. Channel sixteen is the distress channel. You are not in distress yet.
// ACT act2b
@ insert.night | ov:numbered_circle(8,"FORCE EIGHT GALE") | fx:dust | sfx:wind
A force eight gale means winds of thirty-four to forty knots.
@ rocks.night | hero:run/determined | fx:rain | sfx:wind,footsteps
You run along the shore to the rocks, where a stone jetty reaches into the dark.
@ insert.night | ov:paper_diagram("THE JETTY","Low tide","High tide","Skiff") | fx:dust | sfx:paper_slide
High tides come about twelve hours and twenty-five minutes apart, and this one will drown the jetty in forty minutes.
@ rocks.night | hero:stand/shocked | kit:stand/worried | fx:rain | sfx:wind
Kit has followed you. Behind the rocks lies his uncle's skiff, small as a bathtub, with room for two.
// INTERRUPT scene
@ skiff.night | hero:stand/scared | kit:stand/neutral | fx:rain | sfx:car_engine,wind
The outboard coughs, wakes, and pulls you out into black water.
@ skiff.night | hero:stand/worried | kit:stand/neutral | fx:rain | sfx:rustle
Kit tosses you a life jacket. Cold water shock hits in the first minute, he says, so nobody takes it off.
// CLIFF
@ insert.alarm | ov:meter("water","1","WATER") | fx:alarm_pulse | sfx:heartbeat
A litre of water. One bag. One wave taller than the boat.

## CH3 | 5:40 PM
// RITUAL tracker: the survival log opens every chapter
@ skiff.night | hero:crouch/scared | kit:stand/scared | fx:rain | sfx:wind,thunder | track:{hours:1,phone:"4%",water:"1 L",cash:"$23"}
The skiff sits too low. Every pound in your bag pulls the sea closer.
// ACT sacrifice
// INTERRUPT surprise
@ skiff.night | hero:stand/sad | fx:rain | sfx:rustle
Inside the bag is Finn's birthday present, a model ship you saved for since spring.
// BEAT emotional: you let go of the gift to lift the boat
@ skiff.night | hero:reach/sad | fx:rain | sfx:rustle,whoosh
You drop the bag into the dark water. The boat rises, and so does your throat.
@ skiff.night | hero:stand/sad | kit:stand/neutral | fx:rain | sfx:wind
Salt stings your eyes, and you pretend it is only the sea.
// ACT climax
@ skiff.night | hero:stand/scared | kit:stand/scared | fx:rain | sfx:car_engine,power_down
Then the outboard dies, and the waves take the silence.
@ insert.night | ov:meter("battery","3%","PHONE") | fx:dust | sfx:beep
Three percent. One thing left that you have never played. Your thumb hovers over it like it is hot.
// SILENCE
@ skiff.night | hero:phone_hold/determined | fx:rain | sfx:phone_buzz
You press play on Finn's voice message. His small voice says: the lamp is on, follow the lamp.
// PAYOFF voicemail
// SILENCE big
@ lighthouse.night | hero:look_up/shocked | fx:rain | sfx:riser,impact
Far across the water, the dark lighthouse wakes, and its beam sweeps over you.
// PAYOFF lamp
@ skiff.night | hero:point/determined | kit:stand/relieved | fx:rain | sfx:car_engine,wind
You stop trusting the clock and start trusting the light. Kit pulls the cord, and the engine answers.
// ACT resolution
@ rocks.night | hero:run/relieved | fx:rain | sfx:footsteps,wind
You hit the island jetty as the sea begins to close behind you.
// LOOP close why_silent: Finn's phone died while he relit the lamp
@ rocks.night | hero:stand/shocked | kit:stand/relieved | fx:rain | sfx:rustle
Finn is there with the keeper's key and a flat phone. He climbed the lighthouse stairs to relight the lamp for you.
// TWIST: Finn went silent because he was relighting the dark lighthouse to guide you home
@ rocks.night | hero:stand/relieved | kit:stand/relieved | cta:subscribe | fx:rain | sfx:wind
If you made it this far, subscribe. The next sea is already waiting.
// LOOP close wrong_side: the wrong side of the pier was the side without him
// LASTLINE
@ lighthouse.night | hero:stand/relieved | fx:rain | sfx:wind
The wrong side of the pier was only ever the side without him.
