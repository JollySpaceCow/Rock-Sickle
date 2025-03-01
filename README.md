# Rock-Sickle

## Game Components
- 1 six-sided die
- Game board with rocky background
- 6 "Pebble Boi" player pieces (white characters with different colored hats: red, orange, yellow, green, blue, purple)
- 15 Bonus Cards
- 10 Quiz Cards
- Stopwatch/timer functionality for high scores

## Board Layout
Starting from "Go" and following the perimeter clockwise:

## Board Spaces
   [Direction East] 1, 0, Q, -2, J, 1, B, 0, 0
   [Direction South] J, 0, 1, -2, 1, -2, 0
[Direction West] B, 0, -2, Q, B, P
(Path North) [Direction North] 0, 1
(Path North) [Direction West] B, J, Q
(Path North) [Direction North] -2, 0, F
(Path West) [Direction West] 0, 1, J
(Path West) [Direction North] -2, Q, -2, 0, F

0 = Safe space
1 = Jump one space
-2 = Go back two spaces
J = Go to Jail
B = Pick up a bonus card
Q = Pick up a bonus card
F = Finish line

## Ending Cutscene
- When a player gets to the finish line, they glide to the victory area
- Players are ordered in the victory area by who finished quicker
- Game ends when all players reach the finish space
- When playing with six players and everyone finishes, the credits roll

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

### Quiz Cards (10)
1. Q: What type of rock can you find fossils in?
   A: Sedimentary
2. Q: Is granite a metamorphic rock?
   A: Negative
3. Q: How are igneous rocks formed?
   A: By magma cooling
4. Q: What is molten rock called underground?
   A: Magma
5. Q: What rock contains lead?
   A: Galena
6. Q: What type of rock is formed by pressure and heat?
   A: Metamorphic
7. Q: Is air a rock?
   A:
8. Q: What are the 3 main types of rock?
   A: Sedimentary, Igneous, Metamorphic
9. Q: What is your favorite flavor of math, true or false?
   A: Left
10. Q: What type of rock is formed in layers?
    A: Sedimentary
### Quiz Cards (10)
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

7. Q: What type of rock is formed by pressure and heat?
   A: Metamorphic
   * Metamorphic ✓
   * Igneous

8. Q: Is air a rock?
   A: No
   * Yes
   * No ✓

9. Q: What are the 3 main types of rock?
   A: Sedimentary, Igneous, Metamorphic
   * Molten, Solid, Liquid
   * Smooth, Hard, Brittle
   * Adhesion, Mohs, Bead
   * Sedimentary, Igneous, Metamorphic ✓

10. Q: What is your favorite flavor of math, true or false?
   A: Left
   * Soup
   * Croissant
   * Anti-Arctician
   * Left ✓

11. Q: What type of rock is formed in layers?
    A: Sedimentary
    * Sedimentary ✓
    * When flowing water touches lava
    * Igneous

## Visual Style
- Background: Natural rock texture with various gray and brown stones
- UI Elements: Simple vector graphics
- Characters: White "Pebble Boi" figures with coloured hats
- Text: Black text, coloured text for special spaces, coloured text that represents the colour of each player

## Player Piece Visualization
- Player pieces ("Pebble Bois") are semi-transparent to allow visibility of the square beneath
- Multiple pieces on same square:
  - First piece centers on the square
  - Additional pieces overlap halfway off the square while still counting as being on that square
  - This allows all pieces to remain visible while maintaining their position status
