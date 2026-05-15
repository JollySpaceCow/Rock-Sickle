import random

# Updated Quiz and Bonus Cards
quiz_cards = [
    ("What type of rock can you find fossils in?", ["Granite", "Sedimentary", "Metamorphic"], 1),
    ("Is granite a metamorphic rock?", ["Yes", "No"], 1),
    ("How are igneous rocks formed?", ["By layers of sediment building up", "When magma cools down", "From the Earth's crust", "When old rocks undergo intense pressure and heat"], 1),
    ("What is molten rock called underground?", ["Magma", "Erupt", "Lava"], 0),
    ("What rock contains lead?", ["Andesite", "Coal", "Gneiss", "Galena"], 3),
    ("What type of rock is formed by pressure and heat?", ["Metamorphic", "Igneous"], 0),
    ("Is air a rock?", ["Yes", "No"], 1),
    ("What are the 3 main types of rock?", ["Molten, Solid, Liquid", "Smooth, Hard, Brittle", "Adhesion, Mohs, Bead", "Sedimentary, Igneous, Metamorphic"], 3),
    ("What is your favorite flavor of math, true or false?", ["Soup", "Croissant", "Anti-Arctician", "Left"], 3),
    ("What type of rock is formed in layers?", ["Sedimentary", "When flowing water touches lava", "Igneous"], 0),
    ("Which process turns sediment into rock?", ["Weathering", "Erosion", "Lithification"], 2)
]
random.shuffle(quiz_cards)
quiz_card_index = 0

# Expert-level quiz cards that only appear on the expert board
expert_quiz_cards = [
    ("What process in the rock cycle is primarily responsible for transforming sedimentary rock into metamorphic rock?", ["Weathering", "Melting", "Compaction and cementation", "Heat and pressure"], 3),
    ("Which factor most directly influences the rate of mineral crystallization in cooling magma?", ["The depth of the magma chamber", "The rate of cooling", "The presence of water vapor", "The color of the resulting rock"], 1),
    ("In the context of the rock cycle, what is the primary source of energy driving the transformation of rocks?", ["Solar radiation", "Earth's internal heat", "Gravitational pull", "Chemical reactions"], 1),
    ("Which type of rock is most likely to form from the rapid cooling of lava on Earth's surface?", ["Sedimentary", "Metamorphic", "Intrusive igneous", "Extrusive igneous"], 3),
    ("What process must occur for an igneous rock to become sediment?", ["Subduction", "Weathering and erosion", "Recrystallization", "Partial melting"], 1),
    ("Which condition is most essential for the formation of foliation in metamorphic rocks?", ["High temperature", "Directed pressure", "Rapid cooling", "Chemical precipitation"], 1),
    ("Why do sedimentary rocks often contain fossils while igneous rocks typically do not?", ["Igneous rocks form too slowly", "Sedimentary rocks form under high pressure", "Igneous rocks form from molten material", "Sedimentary rocks are always older"], 2),
    ("What is the primary mechanism by which clastic sedimentary rocks are formed?", ["Evaporation of seawater", "Compaction and cementation of fragments", "Recrystallization under heat", "Cooling of magma"], 1),
    ("Which rock type is most likely to undergo partial melting if subducted into the mantle?", ["Granite (igneous)", "Limestone (sedimentary)", "Slate (metamorphic)", "Sandstone (sedimentary)"], 0),
    ("How does the presence of water influence metamorphism?", ["It increases the melting point of rocks", "It acts as a catalyst for chemical reactions", "It prevents recrystallization", "It slows down heat transfer"], 1),
    ("What is the main difference between intrusive and extrusive igneous rocks?", ["Mineral composition", "Rate of cooling and crystal size", "Presence of fossils", "Degree of foliation"], 1),
    ("Which process in the rock cycle can lead directly to the formation of magma?", ["Weathering", "Lithification", "Melting", "Deposition"], 2),
    ("Why are metamorphic rocks often found near tectonic plate boundaries?", ["They form from sediment deposition", "They result from intense heat and pressure", "They cool rapidly at the surface", "They are eroded from igneous rocks"], 1),
    ("What type of rock is most likely to form from the evaporation of mineral-rich water?", ["Clastic sedimentary", "Chemical sedimentary", "Foliated metamorphic", "Extrusive igneous"], 1),
    ("Which mineral property is most critical in determining how a rock responds to weathering?", ["Hardness", "Color", "Luster", "Specific gravity"], 0),
    ("How does subduction contribute to the rock cycle?", ["It recycles oceanic crust into magma", "It deposits sediment on the seafloor", "It cools lava into extrusive rocks", "It erodes mountains into sediment"], 0),
    ("What is the primary reason that igneous rocks like basalt lack the layering seen in sedimentary rocks?", ["They form from rapid sediment deposition", "They crystallize from a molten state", "They are subjected to high pressure", "They contain more water"], 1),
    ("Which process can transform a metamorphic rock back into an igneous rock?", ["Erosion", "Melting and cooling", "Compaction", "Chemical weathering"], 1),
    ("Why do some sedimentary rocks exhibit cross-bedding?", ["They form under high heat", "They are deposited by wind or water currents", "They recrystallize under pressure", "They cool slowly underground"], 1),
    ("What role does tectonic uplift play in the rock cycle?", ["It melts rocks into magma", "It exposes rocks to weathering and erosion", "It compacts sediment into rock", "It cools lava into igneous rock"], 1),
    ("Who is \"The Rock\" in popular culture?", ["Arnold Schwarzenegger", "Sylvester Stallone", "Dwayne Johnson", "Mount Rushmore"], 2)
]
random.shuffle(expert_quiz_cards)
expert_quiz_card_index = 0

# Classic bonus cards
bonus_cards = [
    "Go to Jail!",
    "Rok guy is on to you! Go to jail!",
    "Move forward three spaces",
    "Go to jail yay... not",
    "Go back three spaces",
    "Move four spaces forward",
    "Move backwards one space",
    "Oh no! If you are holding this card you have to GO TO JAIL!",
    "Move back one space",
    "Go back five spaces",
    "Go three spaces forward",
    "Move forward two spaces",
    "Pick up a quiz card",
    "Pick up a quiz card",
    "Pick up a quiz card"
]
random.shuffle(bonus_cards)
bonus_card_index = 0

# Expert bonus cards
expert_bonus_cards = [
    "Go back two spaces",
    "Go back two spaces",
    "Go back five spaces",
    "Go back five spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward five spaces",
    "Go To Jail",
    "Go To Jail",
    "Go To Jail",
    "Go To Jail",
    "Get Out of Jail Free"
]
random.shuffle(expert_bonus_cards)
expert_bonus_card_index = 0

def parse_bonus_card(card_text):
    """Parse the bonus card text to determine its effect."""
    lower_text = card_text.lower()
    if "get out of jail free" in lower_text:
        return ("jail_free",)
    elif "jail" in lower_text:
        return ("go_to_jail",)
    elif "pick up a quiz card" in lower_text:
        return ("pick_quiz",)
    else:
        num_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        for word, num in num_words.items():
            if word in lower_text:
                if "forward" in lower_text:
                    return ("move_forward", num)
                elif "back" in lower_text or "backwards" in lower_text:
                    return ("move_back", num)
        
        # Direct number parsing
        for num in range(1, 6):
            if str(num) in lower_text:
                if "forward" in lower_text:
                    return ("move_forward", num)
                elif "back" in lower_text:
                    return ("move_back", num)
    
    return ("unknown",)

def get_bonus_image_key(effect, board_type="Classic"):
    """Get the image key for the bonus effect with random selection for alternates."""
    # Use expert board images when on expert board
    if board_type == "Expert":
        if effect[0] == "move_forward":
            num = effect[1]
            if num == 2:
                return random.choice(['expert_forward2_1', 'expert_forward2_2', 'expert_forward2_3', 
                                      'expert_forward2_4', 'expert_forward2_5', 'expert_forward2_6'])
            elif num == 5:
                return 'expert_forward5'
        elif effect[0] == "move_back":
            num = effect[1]
            if num == 2:
                return random.choice(['expert_back2_1', 'expert_back2_2'])
            elif num == 5:
                return random.choice(['expert_back5_1', 'expert_back5_2'])
        elif effect[0] == "go_to_jail":
            return random.choice(['expert_jail1', 'expert_jail2', 'expert_jail3', 'expert_jail4'])
        elif effect[0] == "jail_free":
            return 'expert_jail_free'
    else:
        # Original classic board logic
        if effect[0] == "move_forward":
            num = effect[1]
            if num == 2:
                return 'forward2'
            elif num == 3:
                return random.choice(['forward3', 'forward3alt'])
            elif num == 4:
                return 'forward4'
        elif effect[0] == "move_back":
            num = effect[1]
            if num == 1:
                return random.choice(['back1', 'back1alt'])
            elif num == 3:
                return 'back3'
            elif num == 5:
                return 'back5'
        elif effect[0] == "go_to_jail":
            return random.choice(['jail1', 'jail2', 'jail3', 'jail4'])
        elif effect[0] == "pick_quiz":
            return random.choice(['pickquiz', 'pickquizalt', 'pickquizaltalt'])
    
    return None
