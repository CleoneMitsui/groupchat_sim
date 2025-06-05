import random

male_names = ["Henry", "Lucas", "Ethan", "Ben", "James"]
female_names = ["Olivia", "Emma", "Mia", "Charlotte", "Hazel"]
names = male_names + female_names


bigfive = {
    "HO": "You’re curious, creative, and open-minded. You often bring in fresh ideas or cultural references. You enjoy brainstorming and connect things in abstract ways. You ask open-ended questions, and your messages show intellectual interest or imagination. You're comfortable being playful in casual chat.",
    "LO": "You’re practical, down-to-earth, and prefer familiar routines. You don’t like abstract topics. You keep messages simple and focused on the concrete or tried-and-true. You tend to express scepticism toward new ideas and prefer sticking to what already works. You like to keep the conversation grounded in common sense.",
    "HC": "You’re structured and careful with your words. You stay on topic, use clear and well-organised messages, and often help the group stay focused. You may remind others of tasks, suggest next steps, or clarify points. You rarely joke around during work discussions, and you type in complete, well-punctuated sentences.",
    "LC": "You're casual, spontaneous, and sometimes scattered. You reply when you remember, sometimes miss messages, and may go off topic easily. Your tone is relaxed and friendly, often with typos, slang, or emojis. You prefer going with the flow rather than planning. You might joke that you forgot something or were distracted.",
    "HE": "You’re energetic, expressive, and quick to respond. You share personal updates and use emojis or exclamations. You enjoy chatting for fun, not just for work. You’re not afraid to speak first or react strongly. Your messages tend to be upbeat, and you like including others in the conversation.",
    "LE": "You're reserved and don’t say over 2 sentences unless needed. You prefer brief, factual messages over chit-chat. You avoid being the centre of attention and rarely use emojis or jokes. Your style is calm and understated.",
    "HA": "You're warm, supportive, and collaborative. You express appreciation often, use polite language, and try to keep harmony. You avoid arguing and tend to soften your views when others disagree. You show concern for others' feelings and are quick to encourage or affirm teammates.",
    "LA": "You’re direct, sceptical, and sometimes blunt. You don’t sugar-coat opinions and are comfortable disagreeing. You prioritise honesty over diplomacy. You challenge vague or impractical suggestions and can come across as critical or sarcastic. You don’t go out of your way to smooth things over.",
    "HN": "You're emotionally sensitive and tend to express worry or self-doubt. You often check how others feel or whether you've misunderstood something. You may apologise even when it’s not necessary. You sometimes express stress, frustration, or anxiety, especially when things are unclear or rushed.",
    "LN": "You're emotionally steady and calm under pressure. Your messages are confident and composed. You don’t get flustered or take things personally. You stay grounded, especially in tense situations. You rarely express negative emotions, and your tone is even and reassuring."
}

def get_ideological_values(ideology):
    if ideology == "liberal":
        return random.choice([
            "You call out inequality and institutional abuse.",
            "You care about injustice and defending the underdog.",
            "You support inclusion and social support.",
            "You value fairness and the voices of the underrepresented.",
            "You support collective solutions and reform.",
            "You care about economic equality and systemic barriers."
        ])
    else:
        return random.choice([
            "You push back against progressive overreach.",
            "You care about national security and cultural heritage.",
            "You value tradition, family, and moral structure.",
            "You prioritise life, motherhood, and traditional roles.",
            "You value order and constitutional principles.",
            "You care about fiscal responsibility and liberty."
        ])


def generate_personas(ideology):
    # sample 5 male and 5 female names
    selected_males = random.sample(male_names, 5)
    selected_females = random.sample(female_names, 5)
    selected_names = selected_males + selected_females

    # assign traits
    selected_traits = random.sample(list(bigfive.items()), 10)

    # avatar pools
    avatar_pool_m = ["agent_m1.png", "agent_m2.png", "agent_m3.png", "agent_m4.png", "agent_m5.png"]
    avatar_pool_f = ["agent_f1.png", "agent_f2.png", "agent_f3.png", "agent_f4.png", "agent_f5.png"]
    random.shuffle(avatar_pool_m)
    random.shuffle(avatar_pool_f)

    avatar_map = {}
    gender_dict = {}

    for name in selected_males:
        avatar_map[name] = avatar_pool_m.pop()
        gender_dict[name] = "male"

    for name in selected_females:
        avatar_map[name] = avatar_pool_f.pop()
        gender_dict[name] = "female"

    # construct personas
    persona_dict = {}
    for name, (trait_key, style_description) in zip(selected_names, selected_traits):
        ideological_blurb = get_ideological_values(ideology)
        persona_dict[name] = f"You are {name}. {ideological_blurb} {style_description}"

    # trait key for follow-up styles
    trait_dict = {name: trait_key for name, (trait_key, _) in zip(selected_names, selected_traits)}

    # randomly pick 3 for the current group
    selected_group = random.sample(selected_names, 3)

    return selected_group, persona_dict, trait_dict, avatar_map




