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

### First Side
1. Go (Start)
2. Forward 1
3. Safe space
4. Quiz card
5. Back 2 spaces
6. Go to jail
7. Forward 1
8. Bonus card
9. Safe space
10. Safe space

### Second Side
11. Go to jail
12. Safe space
13. Forward 1
14. Back 2 spaces
15. Forward 1
16. Back 2 spaces
17. Safe space

### Third Side
18. Bonus card
19. Safe space
20. Back 2 spaces
21. Quiz card
22. Bonus card
23. Path choice

### Path Options
Path Up:
1. Safe space
2. Forward 1
3. Bonus card
4. Go to jail

Path Left:
1. Safe space
2. Forward 1
3. Go to jail
4. Back 2 spaces

### Final Stretch (Paths Converge)
1. Quiz card
2. Back 2 spaces
3. Safe space
4. Finish

## Victory Condition
- Game ends when all players reach the finish space

## Game Rules
1. Players roll single die to move
2. Landing spots effects:
   - Forward 1: Move forward one space
   - Back 2 spaces: Move back two spaces
   - Safe space: No effect
   - Go to jail: Move to jail space
   - Bonus card (B): Draw Bonus card
   - Quiz card (Q): Draw Quiz card

3. Jail Escape: Must roll even number on turn to exit

4. Quiz Cards:
   - Correct answer: Stay on space
   - Incorrect answer: Move back two spaces

5. Chain Reactions: If movement from cards/spaces leads to new effect squares, those effects must also be followed

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

## Visual Style
- Background: Natural rock texture with various gray and brown stones
- UI Elements: Clean, modern style with rounded buttons
- Characters: White "Pebble Boi" figures with colored hats
- Text: White text for headers, colored text for special spaces

## Player Piece Visualization
- Player pieces ("Pebble Bois") are semi-transparent to allow visibility of the square beneath
- Multiple pieces on same square:
  - First piece centers on square
  - Additional pieces overlap halfway off the square while still counting as being on that square
  - This allows all pieces to remain visible while maintaining their position status

## Technical Notes
- Original game created in 2020
- Digital version created in Scratch
- Pebble Bois modeled in "Makers Empire" and rendered in "Blender"
- Game squares created in Scratch Texture Editor
- Card backs drawn in Autodesk Sketchbook
