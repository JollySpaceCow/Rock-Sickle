# Rock-Sickle

## Game Rules
1. Players roll a single die to move
   
2. Landing spots effects:
   - Forward 1: Move forward one space
   - Back 2 spaces: Move back two spaces
   - Safe space: No effect
   - Go to jail: Move to jail space
   - Bonus card (B): Draw Bonus card
   - Quiz card (Q): Draw Quiz card

3. Jail Escape: Must roll an even number on turn to exit

4. Quiz Cards:
   - Correct answer: Stay on space
   - Incorrect answer: Move back two spaces

5. Chain Reactions: If movement from cards/spaces leads to new effect squares, those effects must also be followed

6. Turn ends once a player:
   - Lands on a safe space
   - Answers a quiz card correctly
   - Escapes jail
   - Fails to escape jail

## Board Layout
Starting from "Go" and following the perimeter clockwise:

### Board Spaces
- [Direction East] 1, 0, Q, -2, J, 1, B, 0, 0
- [Direction South] J, 0, 1, -2, 1, -2, 0
- [Direction West] B, 0, -2, Q, B, P
- (Path North) [Direction North] 0, 1
- (Path North) [Direction West] B, J, Q
- (Path North) [Direction North] -2, 0, F
- (Path West) [Direction West] 0, 1, J
- (Path West) [Direction North] -2, Q, -2, 0, F

### Space Symbols
- 0 = Safe space
- 1 = Jump one space
- -2 = Go back two spaces
- J = Go to Jail
- B = Pick up a bonus card
- Q = Pick up a quiz card
- F = Finish line

## Game Components
- 1 six-sided die
- Game board with rocky background
- 6 "Pebble Boi" player pieces (white characters with different colored hats: red, orange, yellow, green, blue, purple)
- 15 Bonus Cards
- 10 Quiz Cards
- Stopwatch/timer functionality for high scores

## Card Details

### Bonus Cards (15)
1. Go to Jail!
2. Rok guy is on to you! Go to jail!
3. Move forward three spaces
4. Go to jail yay... not
5. Go back three spaces
6. Move four spaces forward
7. Move backwards one space
8. Oh no! If you are holding this card you have to GO TO JAIL!
9. Move back one space
10. Go back five spaces
11. Go three spaces forward
12. Move forward two spaces
13. Pick up a quiz card
14. Pick up a quiz card
15. Pick up a quiz card

### Quiz Cards (11)
1. Q: What type of rock can you find fossils in?
   A: Sedimentary
   * Granite
   * Sedimentary ✓
   * Metamorphic

2. Q: Is granite a metamorphic rock?
   A: No
   * Yes
   * No ✓

3. Q: How are igneous rocks formed?
   A: By magma cooling
   * By layers of sediment building up
   * When magma cools down ✓
   * From the Earth's crust
   * When old rocks undergo intense pressure and heat

4. Q: What is molten rock called underground?
   A: Magma
   * Magma ✓
   * Erupt
   * Lava

5. Q: What rock contains lead?
   A: Galena
   * Andesite
   * Coal
   * Gneiss
   * Galena ✓

6. Q: What type of rock is formed by pressure and heat?
   A: Metamorphic
   * Metamorphic ✓
   * Igneous

7. Q: Is air a rock?
   A: No
   * Yes
   * No ✓

8. Q: What are the 3 main types of rock?
   A: Sedimentary, Igneous, Metamorphic
   * Molten, Solid, Liquid
   * Smooth, Hard, Brittle
   * Adhesion, Mohs, Bead
   * Sedimentary, Igneous, Metamorphic ✓

9. Q: What is your favorite flavor of math, true or false?
   A: Left
   * Soup
   * Croissant
   * Anti-Arctician
   * Left ✓

10. Q: What type of rock is formed in layers?
    A: Sedimentary
    * Sedimentary ✓
    * When flowing water touches lava
    * Igneous

11. Q: Which process turns sediment into rock?
    A: Lithification
    * Weathering
    * Erosion
    * Lithification ✓

## Branching Paths
- If the player has more spaces to travel when they reach the pick a path space, they are stopped in their tracks and shown their options
- A ghost of their character appears on both sides, showing which spaces they could end up at
- They pick a path and continue moving by how many jumps they have left from their die roll
- If a player starts their turn on the pick a path space, they will roll and then pick their direction

## Player Piece Visualization
- Player pieces (pebble bois) are semi-transparent to allow visibility of the square beneath
- Multiple pieces on same square:
  - First piece centers on the square
  - Additional pieces overlap halfway off the square while still counting as being on that square
  - This allows all pieces to remain visible while maintaining their position status

## Computer Players
- There are easy, normal, and hard computer players
- Computer players roll, answer quiz cards, and choose paths on their own
- They are all represented with a cyborg pebble boi with a grey cap

## UI Details
- On startup, there are six player slots
- When a player slot is clicked, it cycles through no player, human player, computer player
- When a computer player is selected, there are three button options of easy, medium, and hard
- The start the game button is only green and clickable if there is at least one player set
- A single clickable die is in the centre
- It rolls with a drum roll and randomly jumps around the screen when the sound plays

## Visual Style
- Background: Natural rock texture with various gray and brown stones
- UI Elements: Simple vector graphics
- Characters: White "Pebble Boi" figures with coloured hats
- Text: Black text, coloured text for special spaces, coloured text that represents the colour of each player

## Ending Cutscene
- When a player gets to the finish line, they glide to the victory area
- Players are ordered in the victory area by who finished quicker
- Game ends when all players reach the finish space
- When playing with six players and everyone finishes, the credits roll

## Expert Board

### Quiz Cards (20)
1. Q: What process in the rock cycle is primarily responsible for transforming sedimentary rock into metamorphic rock?
   A: Heat and pressure
   * Weathering
   * Melting
   * Compaction and cementation
   * Heat and pressure ✓

2. Q: Which factor most directly influences the rate of mineral crystallization in cooling magma?
   A: The rate of cooling
   * The depth of the magma chamber
   * The rate of cooling ✓
   * The presence of water vapor
   * The color of the resulting rock

3. Q: In the context of the rock cycle, what is the primary source of energy driving the transformation of rocks?
   A: Earth's internal heat
   * Solar radiation
   * Earth's internal heat ✓
   * Gravitational pull
   * Chemical reactions

4. Q: Which type of rock is most likely to form from the rapid cooling of lava on Earth's surface?
   A: Extrusive igneous
   * Sedimentary
   * Metamorphic
   * Intrusive igneous
   * Extrusive igneous ✓

5. Q: What process must occur for an igneous rock to become sediment?
   A: Weathering and erosion
   * Subduction
   * Weathering and erosion ✓
   * Recrystallization
   * Partial melting

6. Q: Which condition is most essential for the formation of foliation in metamorphic rocks?
   A: Directed pressure
   * High temperature
   * Directed pressure ✓
   * Rapid cooling
   * Chemical precipitation

7. Q: Why do sedimentary rocks often contain fossils while igneous rocks typically do not?
   A: Igneous rocks form from molten material
   * Igneous rocks form too slowly
   * Sedimentary rocks form under high pressure
   * Igneous rocks form from molten material ✓
   * Sedimentary rocks are always older

8. Q: What is the primary mechanism by which clastic sedimentary rocks are formed?
   A: Compaction and cementation of fragments
   * Evaporation of seawater
   * Compaction and cementation of fragments ✓
   * Recrystallization under heat
   * Cooling of magma

9. Q: Which rock type is most likely to undergo partial melting if subducted into the mantle?
   A: Granite (igneous)
   * Granite (igneous) ✓
   * Limestone (sedimentary)
   * Slate (metamorphic)
   * Sandstone (sedimentary)

10. Q: How does the presence of water influence metamorphism?
    A: It acts as a catalyst for chemical reactions
    * It increases the melting point of rocks
    * It acts as a catalyst for chemical reactions ✓
    * It prevents recrystallization
    * It slows down heat transfer

11. Q: What is the main difference between intrusive and extrusive igneous rocks?
    A: Rate of cooling and crystal size
    * Mineral composition
    * Rate of cooling and crystal size ✓
    * Presence of fossils
    * Degree of foliation

12. Q: Which process in the rock cycle can lead directly to the formation of magma?
    A: Melting
    * Weathering
    * Lithification
    * Melting ✓
    * Deposition

13. Q: Why are metamorphic rocks often found near tectonic plate boundaries?
    A: They result from intense heat and pressure
    * They form from sediment deposition
    * They result from intense heat and pressure ✓
    * They cool rapidly at the surface
    * They are eroded from igneous rocks

14. Q: What type of rock is most likely to form from the evaporation of mineral-rich water?
    A: Chemical sedimentary
    * Clastic sedimentary
    * Chemical sedimentary ✓
    * Foliated metamorphic
    * Extrusive igneous

15. Q: Which mineral property is most critical in determining how a rock responds to weathering?
    A: Hardness
    * Hardness ✓
    * Color
    * Luster
    * Specific gravity

16. Q: How does subduction contribute to the rock cycle?
    A: It recycles oceanic crust into magma
    * It recycles oceanic crust into magma ✓
    * It deposits sediment on the seafloor
    * It cools lava into extrusive rocks
    * It erodes mountains into sediment

17. Q: What is the primary reason that igneous rocks like basalt lack the layering seen in sedimentary rocks?
    A: They crystallize from a molten state
    * They form from rapid sediment deposition
    * They crystallize from a molten state ✓
    * They are subjected to high pressure
    * They contain more water

18. Q: Which process can transform a metamorphic rock back into an igneous rock?
    A: Melting and cooling
    * Erosion
    * Melting and cooling ✓
    * Compaction
    * Chemical weathering

19. Q: Why do some sedimentary rocks exhibit cross-bedding?
    A: They are deposited by wind or water currents
    * They form under high heat
    * They are deposited by wind or water currents ✓
    * They recrystallize under pressure
    * They cool slowly underground

20. Q: What role does tectonic uplift play in the rock cycle?
    A: It exposes rocks to weathering and erosion
    * It melts rocks into magma
    * It exposes rocks to weathering and erosion ✓
    * It compacts sediment into rock
    * It cools lava into igneous rock
