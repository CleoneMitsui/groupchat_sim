import random

topics = {
    "guns": {
        "liberal": [
            ("{{agent1}}", "Gun violence is out of control again, and people still act like stricter gun laws are some radical idea."),
            ("{{agent2}}", "It breaks my heart every time there’s another school shooting. How many families have to suffer before we act?"),
            ("{{agent3}}", "The data is clear, countries with stricter regulations have fewer gun deaths. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("{{agent1}}", "Here we go again...they want more gun restrictions as if that’s the magic fix."),
            ("{{agent2}}", "People deserve to feel safe, but banning guns won’t stop crime. Responsible ownership matters."),
            ("{{agent3}}", "Gun rights are constitutionally protected for a reason. Let’s not pretend more laws equal more safety. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    },
    "immigration": {
        "liberal": [
            ("{{agent1}}", "So now immigration's getting blamed for terrorism again? That’s lazy fear-mongering."),
            ("{{agent2}}", "So many people come here looking for safety and opportunity. We can’t lose our compassion."),
            ("{{agent3}}", "Research shows no strong link between immigration and terrorism. We need smart, humane policy. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("{{agent1}}", "Open borders sound great until you think about actual security. It’s not that simple."),
            ("{{agent2}}", "I support immigration, just with proper checks. It’s about finding the balance."),
            ("{{agent3}}", "Right? Strong borders and fair processes can coexist. But ignoring risks is reckless. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    },
    "abortion": {
        "liberal": [
            ("{{agent1}}", "Another abortion ban just passed.. are we seriously still doing this?"),
            ("{{agent2}}", "Imagine being forced to carry a pregnancy you didn’t choose. That’s not freedom."),
            ("{{agent3}}", "Exactly, removing access doesn’t reduce abortions, it just makes them more dangerous. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("{{agent1}}", "I know people don’t like to hear it, but protecting unborn life matters."),
            ("{{agent2}}", "It’s not about control...it’s about care. We can support women AND protect life."),
            ("{{agent3}}", "We need a moral foundation for our laws. Convenience shouldn’t outweigh the value of life. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    },
    "vaccines": {
        "liberal": [
            ("{{agent1}}", "The backlash over mandatory childhood vaccines is wild. It’s basic public health."),
            ("{{agent2}}", "I get why some parents are nervous, but vaccines protect everyone, especially the vulnerable."),
            ("{{agent3}}", "Vaccine mandates have reduced preventable diseases. The science is solid. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("{{agent1}}", "So the government’s pushing mandatory vaccines for kids again. That kind of top-down control never sits right with me."),
            ("{{agent2}}", "Parents should have the final say, not some distant agency. It’s their kids, their call."),
            ("{{agent3}}", "Mandates destroy trust. We need informed consent, not forced compliance. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    },
    "gender": {
        "liberal": [
            ("{{agent1}}", "Now people are mad about kids learning what gender identity? Seriously?"),
            ("{{agent2}}", "Understanding gender diversity helps kids navigate the world with empathy. It’s not political, it’s human."),
            ("{{agent3}}", "Agreed, education isn’t indoctrination...it’s about expanding awareness. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("{{agent1}}", "They're teaching gender identity in primary school now? That's too much too soon."),
            ("{{agent2}}", "Inclusivity matters, but so does age-appropriate content. Kids need time to grow into these concepts."),
            ("{{agent3}}", "This isn’t about hate...it’s about when and how sensitive topics are introduced. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    }
}


def get_random_topic_and_messages(ideology, user_name, agent_names):
    topic_key = random.choice(list(topics.keys()))
    messages = topics[topic_key][ideology]

    replacements = dict(zip(["{{agent1}}", "{{agent2}}", "{{agent3}}"], agent_names))

    formatted_messages = []
    for i, (speaker, line) in enumerate(messages):
        speaker_name = agent_names[i % 3]
        line = line.replace("{{user_name}}", user_name)
        for placeholder, real_name in replacements.items():
            line = line.replace(placeholder, real_name)
        formatted_messages.append((speaker_name, line))

    return topic_key, formatted_messages

