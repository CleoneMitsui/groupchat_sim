import random

topics = {
    "guns": {
        "liberal": [
            ("Curtis", "Hey, so there's another debate flaring up about gun laws. I honestly can't believe people are still arguing over it."),
            ("Olivia", "Exactly, how many more shootings do we need before we pass real reform?"),
            ("Mark", "Totally. It's like logic takes a back seat. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ],
        "conservative": [
            ("Curtis", "Honestly, more responsible gun ownership could save lives. It’s not about banning everything."),
            ("Olivia", "Right, and people have a right to feel safe. You can’t always count on police to be there."),
            ("Mark", "Exactly — legal gun ownership is a constitutional right. Let’s not lose sight of that. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ]
    },
    "immigration": {
        "liberal": [
            ("Curtis", "Saw someone say immigration causes terrorism again. That tired trope just won’t die."),
            ("Olivia", "Yeah, it’s heartbreaking how fear gets used to justify excluding people in need."),
            ("Mark", "I’d love to know what data they're using. Historically, immigration doesn't correlate with terrorism spikes. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ],
        "conservative": [
            ("Curtis", "There’s a real concern here. Open borders just aren’t realistic when security is on the line."),
            ("Olivia", "Exactly. No one's saying all immigrants are bad, but you can’t ignore the risk of bad actors."),
            ("Mark", "It's about balance. Immigration needs rules and vetting, especially in today’s world. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ]
    },
    "abortion": {
        "liberal": [
            ("Curtis", "Another state is trying to ban abortion again. It's like we’re going backwards."),
            ("Olivia", "It’s terrifying. Imagine being forced to carry a pregnancy you didn’t choose."),
            ("Mark", "It’s a tough issue, but stripping choice away never leads to good policy. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ],
        "conservative": [
            ("Curtis", "Every life matters...even unborn ones. That’s the core of it for me."),
            ("Olivia", "And there are options. Adoption, support networks… we can help without ending life."),
            ("Mark", "Policy should reflect morality. We shouldn’t make convenience outweigh life. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ]
    },
    "vaccines": {
        "liberal": [
            ("Curtis", "Some folks are mad that the government requires kids to get vaccinated. Seriously?"),
            ("Olivia", "I get some hesitation, but it’s about protecting the whole community."),
            ("Mark", "The science is clear...mandated childhood vaccines save lives and prevent outbreaks. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ],
        "conservative": [
            ("Curtis", "I just think it’s overreach to force this stuff on parents. Give people the choice."),
            ("Olivia", "Right. Parents should decide what goes in their kid’s body, not the government."),
            ("Mark", "Mandates erode trust. We need transparency and personal responsibility, not top-down control. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ]
    },
    "gender": {
        "liberal": [
            ("Curtis", "People are freaking out about kids learning about gender identity. It’s basic human respect."),
            ("Olivia", "Exactly! It’s not about politics, it’s about helping kids understand themselves and others."),
            ("Mark", "Honestly, most of it is just fear-mongering. Schools aren’t turning kids into anything they’re teaching empathy. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ],
        "conservative": [
            ("Curtis", "Teaching this to young kids? I don’t think they’re ready for that conversation."),
            ("Olivia", "It’s one thing to be inclusive, but it feels like schools are overstepping."),
            ("Mark", "Parents should decide when and how kids learn about sensitive topics like gender. Anyway, welcome to the group, {{user_name}}. What are your thoughts?")
        ]
    }
}

def get_random_topic_and_messages(ideology, user_name):
    topic_key = random.choice(list(topics.keys()))
    messages = topics[topic_key][ideology]
    messages = [
        (speaker, line.replace("{{user_name}}", user_name))
        for speaker, line in messages
    ]
    return topic_key, messages
