import random

topics = {
    "guns": {
        "liberal": [
            ("Curtis", "Gun violence is out of control again, and people still act like stricter gun laws are some radical idea."),
            ("Olivia", "It breaks my heart every time there’s another shooting. How many families have to suffer before we act?"),
            ("Mark", "The data is clear, countries with stricter regulations have fewer gun deaths. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("Curtis", "Here we go again...they want more gun restrictions as if that’s the magic fix."),
            ("Olivia", "People deserve to feel safe, but banning guns won’t stop crime. Responsible ownership matters."),
            ("Mark", "Gun rights are constitutionally protected for a reason. Let’s not pretend more laws equal more safety. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    },
    "immigration": {
        "liberal": [
            ("Curtis", "So now immigration's getting blamed for terrorism again? That’s lazy fear-mongering."),
            ("Olivia", "So many people come here looking for safety and opportunity. We can’t lose our compassion."),
            ("Mark", "Research shows no strong link between immigration and terrorism. We need smart, humane policy. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("Curtis", "Open borders sound great until you think about actual security. It’s not that simple."),
            ("Olivia", "I support immigration, just with proper checks. It’s about finding the balance."),
            ("Mark", "Strong borders and fair processes can coexist. But ignoring risks is reckless. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    },
    "abortion": {
        "liberal": [
            ("Curtis", "Another abortion ban just passed.. are we seriously still doing this?"),
            ("Olivia", "Imagine being forced to carry a pregnancy you didn’t choose. That’s not freedom."),
            ("Mark", "Removing access doesn’t reduce abortions, it just makes them more dangerous. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("Curtis", "I know people don’t like to hear it, but protecting unborn life matters."),
            ("Olivia", "It’s not about control...it’s about care. We can support women and protect life."),
            ("Mark", "We need a moral foundation for our laws. Convenience shouldn’t outweigh the value of life. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    },
    "vaccines": {
        "liberal": [
            ("Curtis", "The backlash over mandatory childhood vaccines is wild. It’s basic public health."),
            ("Olivia", "I get why some parents are nervous, but vaccines protect everyone — especially the vulnerable."),
            ("Mark", "Vaccine mandates have reduced preventable diseases. The science is solid. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("Curtis", "So the government’s pushing mandatory vaccines for kids again. That kind of top-down control never sits right with me."),
            ("Olivia", "Parents should have the final say, not some distant agency. It’s their kids, their call."),
            ("Mark", "Mandates undermine trust. We need informed consent, not forced compliance. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ]
    },
    "gender": {
        "liberal": [
            ("Curtis", "Now people are mad about kids learning what gender identity even is? Seriously?"),
            ("Olivia", "Understanding gender diversity helps kids navigate the world with empathy. It’s not political, it’s human."),
            ("Mark", "Education isn’t indoctrination...it’s about expanding awareness. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
        ],
        "conservative": [
            ("Curtis", "They're teaching gender identity in primary school now? That's too much too soon."),
            ("Olivia", "Inclusivity matters, but so does age-appropriate content. Kids need time to grow into these concepts."),
            ("Mark", "This isn’t about hate...it’s about when and how sensitive topics are introduced. Anyway, welcome to the group, {{user_name}}. What are your thoughts on this?")
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
