import streamlit as st
from openai import OpenAI
from streamlit_chat import message
from datetime import datetime
from topics import get_random_topic_and_messages
import time
import random
import base64
from assign_conditions import get_even_assignment
LANG = "ja"  # "ja" for Japanese mode



if "agent_rounds_raw" not in st.session_state:
    st.session_state.agent_rounds_raw = []



def render_chat():
    import streamlit.components.v1 as components

    # ensure agent_rounds_raw is always initialised, even on smartphone OS
    if "agent_rounds_raw" not in st.session_state:
        st.session_state.agent_rounds_raw = []

    from utils import generate_participant_id

    if "participant_id" not in st.session_state:
        prolific_pid = st.session_state.get("prolific_pid", "testuser")
        if prolific_pid == "testuser":
            st.session_state.participant_id = f"test_{generate_participant_id()}"
        else:
            st.session_state.participant_id = prolific_pid




    # warning banner
    st.markdown(
        "<p style='color:red; font-weight:bold;'>⚠️ Please do not refresh the page. Doing so will restart the study and erase your answers.</p>",
        unsafe_allow_html=True
    )

    if "awaiting_post" not in st.session_state:
        st.session_state.awaiting_post = False


    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    #### translate topics.py
    from functools import lru_cache

    @lru_cache(maxsize=8)
    def translate_seed_lines(lines_tuple):
        # lines_tuple is a tuple of strings so it's hashable for caching
        if LANG != "ja":
            return list(lines_tuple)
        prompt = (
            "Translate the following chat lines into natural, casual Japanese used among coworkers. "
            "Keep names as-is. Keep the meaning and tone. Return one line per bullet, in order."
        )
        content = "\n".join([f"- {x}" for x in lines_tuple])
        resp = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.2
        )
        out = resp.choices[0].message.content.strip().split("\n")
        # strip leading bullets / whitespace
        out = [s.lstrip("-• ").strip() for s in out if s.strip()]
        # if the model returns fewer lines for some reason, fall back to originals
        if len(out) != len(lines_tuple):
            return list(lines_tuple)
        return out



    # --- session initiation ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "entered_chat" not in st.session_state:
        st.session_state.entered_chat = False
    if "user_logo" not in st.session_state:
        st.session_state.user_logo = ""
    if "user_count" not in st.session_state:
        st.session_state.user_count = 0
    if "trigger_ai_reply" not in st.session_state:
        st.session_state.trigger_ai_reply = False


    # --- AI agents utilities ---
    # randomly pick 10 personas, assign big 5 styles, and select 3 for chat
    from personas import generate_personas

    # if "group_ideology" in st.session_state and "group_members" not in st.session_state:
    #     st.session_state.group_members, st.session_state.persona_dict, st.session_state.trait_dict, st.session_state.avatar_map = generate_personas(st.session_state.group_ideology, nickname=st.session_state.nickname)

    if "group_ideology" not in st.session_state:
        secret_dict = st.secrets["connections"]["gsheets"]

        assigned_ideology, assigned_topic = get_even_assignment(
            st.session_state.participant_id,
            secret_dict
        )
        st.session_state.group_ideology = assigned_ideology
        st.session_state.assigned_topic = assigned_topic

    def avatar_url(name):
        filename = st.session_state.avatar_map.get(name)
        if filename:
            try:
                with open(f"images/{filename}", "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                return f"data:image/png;base64,{encoded}"
            except FileNotFoundError:
                pass
        return f"https://api.dicebear.com/6.x/icons/svg?seed={name}"


    def load_user_logo():
        with open("images/user.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"



    # --- instruction page ---
    if not st.session_state.entered_chat:
        st.title("Chatgroup Demo (Japanese) 💬")

        st.markdown("""
     <div style="font-size:16px; line-height:1.8">
          <strong>デモ版のご案内：</strong><br> 
        本アプリケーションはデモ用です。<br><br>
                    
        <strong>データとAIの利用について：</strong><br>
          ここでは、AIエージェントと模擬グループチャットで対話します。あなたが入力するテキストは、生成AIモデルにより
                    リアルタイムで処理・応答生成されます。本デモで得られるデータについては匿名性が保証され，個⼈が特定できるかたちで解析されることはありません。
        次のページに進むことで、AIエージェントとの対話およびデータの研究利用に同意したものとみなされます。
        </div>
         <br>
        <span style="color:#218838; font-weight:bold; font-size:17px;">
          📌 あなたは同僚から招待されて、気軽な雑談グループチャットに参加することになったと想像してください。実際の同僚と話しているつもりで、自然にやり取りしてください。<br><br>
                    
        このグループは仕事用の公式チャンネルではなく、雑談や集まりの予定、日常の話題を気軽に交わす場です。
        入室すると、これまでのやり取りの一部が表示されます。いつでも会話に加わってください。<br><br>
        </span>

        参加する前に、ニックネームを入力してください。<br>
        <span style='font-size:15px; color:gray;'>※このニックネームは記録されず、グループ内での識別のみに使用されます。</span>
        """, unsafe_allow_html=True)

        user_name = st.text_input("ニックネームを入力してください（12文字以内）", key="nickname_input")

        if user_name:
            if len(user_name) > 12:
                st.warning("ニックネームは12文字以内にしてください。")
            else:
                st.session_state.nickname = user_name
        
        if st.button("Enter Chat", disabled=not user_name or len(user_name) > 12):
            # # assign liberal or conservative group
            # if "group_ideology" not in st.session_state:
            #     st.session_state.group_ideology = random.choice(["liberal", "conservative"])
            

            # generate personas
            if "group_members" not in st.session_state:
                st.session_state.group_members, st.session_state.persona_dict, st.session_state.trait_dict, st.session_state.avatar_map = generate_personas(st.session_state.group_ideology)


            # get one topic and its messages
            # also passes 3 agent names randomly selected
            topic_key, preset_messages = get_random_topic_and_messages(
                st.session_state.group_ideology,
                user_name,
                st.session_state.group_members,
                topic=st.session_state.assigned_topic  # force balanced topic
            )

            # translate once per session if LANG == "ja"
            speakers = [spk for spk, line in preset_messages]
            lines = [line for spk, line in preset_messages]
            translated = translate_seed_lines(tuple(lines))
            preset_messages = list(zip(speakers, translated))


            st.session_state.selected_topic = topic_key

            for speaker, line in preset_messages:
                st.session_state.messages.append({
                    "role": "assistant",
                    "speaker": speaker,
                    "content": line,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "timestamp_unix": time.time()
                })

            st.session_state.user_logo = load_user_logo()
            st.session_state.entered_chat = True
            st.rerun()



    # --- main chat UI ---
    else:
        st.subheader("Group Chat Begins 💬")
        group_members = st.session_state.group_members
        st.markdown(f"👥 **Members:** {', '.join(group_members)} and **You**")


        # SHOW ALL MESSAGES
        for i, msg in enumerate(st.session_state.messages):
            is_user = msg["role"] == "user"
            logo = st.session_state.user_logo if is_user else avatar_url(msg["speaker"])
            name = "You" if is_user else msg["speaker"]

            #for display only the h and m
            try:
                dt = datetime.strptime(msg["timestamp"], "%H:%M:%S")
            except ValueError:
                dt = datetime.strptime(msg["timestamp"], "%H:%M")

            clean_timestamp = dt.strftime("%H:%M")

            timestamp = f"<i style='color:gray; font-size: 0.8em;'>{clean_timestamp}</i>"


            message(
                f"**{name}:** {msg['content']}\n\n{timestamp}",
                is_user=is_user,
                key=f"msg_{i}",
                logo=logo,
                allow_html=True
            )





        #### USER INPUT (participant input) ####
        # store reaction time using unix timestamp
        user_input = st.chat_input("Type your message here...")
        if user_input:
            now = time.time()  # record current time in Unix timestamp

            # find last assistant message timestamp
            assistant_times = [
                m["timestamp_unix"]
                for m in reversed(st.session_state.messages)
                if m["role"] == "assistant" and "timestamp_unix" in m
            ]
            if assistant_times:
                reaction_sec = now - assistant_times[0]
            else:
                reaction_sec = ""

            # save reaction time
            if "reaction_times" not in st.session_state:
                st.session_state.reaction_times = []
            st.session_state.reaction_times.append(reaction_sec)

            # save user message with both readable and unix timestamp
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "timestamp_unix": now
            })




            # make sure response1 is the part of round 1
            if st.session_state.user_count == 0:
                st.session_state.messages[-1]["temp_round_marker"] = True


            # collect and store the previous round's AI responses before clearing
            round_text = [
                f"{m['speaker']}: {m['content']}"
                for m in st.session_state.messages
                if m.get("temp_round_marker") and m["role"] == "assistant"
            ]
            if round_text:
                st.session_state.agent_rounds_raw.append("\n".join(round_text))

            # now clear the temp_round_marker for the new round
            for m in st.session_state.messages:
                m.pop("temp_round_marker", None)


            st.session_state.user_count += 1

            # check if it is the 5th time BEFORE any AI agent replies
            if st.session_state.user_count >= 5:
                st.session_state.awaiting_post = True
                st.rerun()
            else:
                st.session_state.trigger_ai_reply = True
                st.rerun()


        # AI agent response
        if st.session_state.trigger_ai_reply and st.session_state.user_count <= 6:
            st.session_state.trigger_ai_reply = False

            # ensures everyone sends one message
            ai_names = group_members.copy()
            random.shuffle(ai_names)  # randomise message order

            # store recent assistant replies to avoid repetition
            recent_ai_texts = [m["content"] for m in st.session_state.messages if m["role"] == "assistant"][-10:]

            # detect if someone was directly called
            def get_called_name(messages, members):
                import re
                for m in reversed(messages[-3:]):  # check recent messages
                    if m["role"] == "user":
                        source = m["content"]
                    elif m["role"] == "assistant" and m.get("speaker") not in members:
                        source = m["content"]
                    else:
                        continue  # skip AI agents talking to others (self-mentions)
                    for name in members:
                        pattern = re.compile(rf"\b{name}\b", re.IGNORECASE)
                        if pattern.search(source):
                            return name
                return None


            # get who was called
            called_name = get_called_name(st.session_state.messages, group_members)

        
            # add a helper to let GPT infer who should respond
            def infer_recipient(messages):
                members = st.session_state.get("group_members", [])
                context = messages[-6:]  
                chat = "\n".join(
                    [f"{m.get('speaker', 'You')}: {m['content']}" for m in context]
                )
                system_prompt = (
                    "You are a reasoning agent in a group chat. "
                    "Given the recent messages, infer who should be the next person to respond. "
                    "Only respond with one of the current agent names or say 'all' if it should be general."
                )
                response = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": chat}
                    ],
                    temperature=0.3
                )
                reply = response.choices[0].message.content.strip()
                reply = reply.replace("—", "...")  # replace em dash with ...
                return reply

            recipient = infer_recipient(st.session_state.messages)
            if recipient in group_members:
                ai_names = [recipient]
            else:
                ai_names = group_members.copy()
                random.shuffle(ai_names)

            # if someone was called out by name, force them to respond and skip the rest
            if called_name and called_name in group_members:
                ai_names = [called_name]  # only that person replies
            else:
                ai_names = group_members.copy()
                random.shuffle(ai_names)

            # choose 1–3 AI responders per round
            if called_name and called_name in group_members:
                # if a specific name was mentioned, only that agent replies
                ai_names = [called_name]
            else:
                # otherwise, choose 1–3 random responders
                num_responders = random.randint(1, 3)
                ai_names = random.sample(group_members, k=num_responders)





            # loop
            ##### REGULAR AI RESPONSE BLOCK ####
            for i, ai_name in enumerate(ai_names):
                if i == 0:
                    time.sleep(random.uniform(1.8, 3.2))  # "thinking" delay before the 1st agent only

                # with st.chat_message("assistant"):
                with st.spinner(f"{ai_name} is typing{'.' * random.randint(1, 3)}"):
                    time.sleep(random.uniform(2.5, 4.5)) # "typing" delay
                    context = [
                        {"role": "user", "content": f"You: {m['content']}"} if m["role"] == "user"
                        else {"role": "assistant", "content": f"{m['speaker']}: {m['content']}"}
                        for m in st.session_state.messages[-10:]  
                    ]
            

                    response = client.chat.completions.create(
                        model="gpt-4.1",
                        messages=[{"role": "system", "content": (
                            f"{st.session_state.persona_dict[ai_name]} "
                            f"You are {ai_name} , one of several coworkers in a casual group chat at a new workplace.. "
                            "Speak only as yourself. Do not speak for the group or refer to others as 'we'. "
                            "Respond naturally as if in a group chat. Be casual and brief. "
                            "Vary your tone and length like real people. Do not use em dashes (—). "
                            "Do not ask the participant a direct question or mention their name. "
                            "Do not change topics unless the participant clearly does. "
                            "Stay focused on the current topic and build on what others said. "
                            "Maintain your ideological stance. Acknowledge differing views if needed, but do not shift your position. "
                            "Avoid personal talk like weekend plans or small talk."
                            "Use a natural, informal tone: contractions, everyday expressions, and casual style. "
                            "Mimic how real people type, including slight disfluencies. "
                            "Vary the length and tone of your replies, sometimes short, sometimes more expressive. "
                            "Do not mention you're an AI or use overly formal language. "
                            # --- language forcing ---
                            "From now on, write **only in Japanese** in a natural, casual workplace style."
                            "Do take into consideration that you are Japanese, speaking with Japanese coworkers."
                        )}] + context,

                        temperature=0.7
                    )
                    reply = response.choices[0].message.content.strip()
                    reply = reply.replace("—", "...")
                    # recursively remove any group member names at the beginning
                    while True:
                        for other_name in group_members:
                            if reply.startswith(f"{other_name}:"):
                                reply = reply[len(f"{other_name}:"):].strip()
                                break
                        else:
                            break  # no prefix matched

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    display_time = datetime.now().strftime("%H:%M")
                    message(
                        f"**{ai_name}:** {reply}\n\n<i style='color:gray; font-size: 0.8em'>{display_time}</i>",
                        is_user=False,
                        key=f"ai_msg_{len(st.session_state.messages)}_{ai_name}",
                        logo=avatar_url(ai_name),
                        allow_html=True
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "speaker": ai_name,
                        "content": reply,
                        "timestamp": timestamp,
                        "timestamp_unix": time.time(),
                        "temp_round_marker": True
                    })
                if i < len(ai_names) - 1:
                    time.sleep(random.uniform(1.5, 3.0))

            # END of 1-3 agents' replies → do 1 more follow-up
            # get last agent speaker (the final agent who replied)
            last_assistant = None
            for m in reversed(st.session_state.messages):
                if m["role"] == "assistant":
                    last_assistant = m["speaker"]
                    break

            # make sure the follow-up speaker is not the last assistant
            followup_candidates = [name for name in group_members if name != last_assistant]
            followup_speaker = random.choice(followup_candidates)

            time.sleep(1.5)




            ##### FOLLOW-UP NUDGING MESSAGE BLOCK #####
            # with st.chat_message("assistant"):

            # --- follow-up prompt styles per agent ---
            bigfive_followup_styles = {
                "HO": [
                    "Toss out a curious or creative question, and use all lowercase.",
                    "Make an offbeat connection and invite others into the idea.",
                    "Bring up a new angle and casually bring {name} into the mix."
                ],
                "LO": [
                    "Stick to something practical and casually tag {name} for thoughts.",
                    "Mention a familiar example and include others to chime in naturally.",
                    "Say something grounded and ask what others would think."
                ],
                "HC": [
                    "Summarise the key point and politely invite others to add.",
                    "Point out a next step and see if others agree.",
                    "Reorganise the thread and mention {name} to chime in."
                ],
                "LC": [
                    "Drop a casual, slightly messy comment that jokingly pulls in {name}.",
                    "Admit to being a bit off topic and pull others in with humour.",
                    "Say something fun, unstructured, and use all lowercase."
                ],
                "HE": [
                    "Say something fun or expressive.",
                    "Throw out a cheerful message and draw others into it.",
                    "Add an emoji-filled line and hope {name} joins in."
                ],
                "LE": [
                    "Say something very short.",
                    "Briefly mention {name} in a cool, understated way.",
                    "Drop a quiet observation."
                ],
                "HA": [
                    "Say something warm or supportive.",
                    "Gently pull {name} into the conversation with encouragement.",
                    "Speak in a caring or harmonious way."
                ],
                "LA": [
                    "Make a blunt or sarcastic remark.",
                    "Challenge something briefly and see if {name} agrees.",
                    "Toss in a critical thought and invite others to weigh in."
                ],
                "HN": [
                    "Worry about how you sounded and check if {name} agrees.",
                    "Admit uncertainty.",
                    "Express concern gently."
                ],
                "LN": [
                    "Say something steady and calm.",
                    "Respond with composure and invite others to chime in thoughtfully.",
                    "Say something reassuring that includes {name} naturally."
                ]
            }

            with st.spinner(f"{followup_speaker} is typing..."):
                time.sleep(random.uniform(2.5, 4.0))
                user_name = st.session_state.get("nickname", "you")
                
                
               
                
                # choose appropriate style based on speaker
                trait = st.session_state.trait_dict[followup_speaker]
                style = random.choice(bigfive_followup_styles[trait]).replace("{name}", st.session_state.nickname)


                followup_prompt = (
                    f"{st.session_state.persona_dict[followup_speaker]} "
                    f"You are {followup_speaker} in a casual work chat group. "
                    "Speak only as yourself. Do not represent the group or refer to others as 'we'. "
                    "Be casual and brief, and vary your tone and length like real people. "
                    "Avoid sounding robotic or formulaic. Do not use em dashes (—). "
                    "Mimic how real people type."
                    "Stay on topic unless the participant changes it. "
                    "Maintain your ideological stance. You can acknowledge differing views politely, but do not shift your position. "
                    "Do not invent any other names outside this group."
                    # --- language forcing ---
                    "From now on, write **only in Japanese** in a natural, casual workplace style."
                    "Do take into consideration that you are Japanese, speaking with Japanese coworkers."
                    "Speak like how a Japanese would speak."
                    f"{style}"
                )



                context = []
                for m in st.session_state.messages:
                    if m["role"] == "assistant":
                        context.append({"role": "assistant", "content": m["content"]})

                # (read the last 20 messages)
                context = context[-20:]


                response = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[{"role": "system", "content": followup_prompt}] + context,
                    temperature=0.8
                )
                reply = response.choices[0].message.content.strip()
                reply = reply.replace("—", "...")


                timestamp = datetime.now().strftime("%H:%M:%S")
                display_time = datetime.now().strftime("%H:%M")
                message(
                    f"**{followup_speaker}:** {reply}\n\n<i style='color:gray; font-size: 0.8em'>{display_time}</i>",
                    is_user=False,
                    key=f"ai_msg_{len(st.session_state.messages)}_{followup_speaker}",
                    logo=avatar_url(followup_speaker),
                    allow_html=True
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "speaker": followup_speaker,
                    "content": reply,
                    "timestamp": timestamp,
                    "timestamp_unix": time.time(),
                    "temp_round_marker": True  # used to group per round
                })

            st.rerun()


        # check for conversation end
        user_msg_count = sum(1 for m in st.session_state.messages if m["role"] == "user")

    if st.session_state.awaiting_post:
        st.markdown("*That is the end of the study.*")
        time.sleep(1)  # gives user a moment
        st.session_state.page = "post"
        st.session_state.awaiting_post = False

        # collect and store current round's replies only
        round_text = [
            f"{m['speaker']}: {m['content']}"
            for m in st.session_state.messages
            if m.get("temp_round_marker") and m["role"] == "assistant"
        ]

        if round_text:
            st.session_state.agent_rounds_raw.append("\n".join(round_text))

        for m in st.session_state.messages:
            m.pop("temp_round_marker", None)

        st.rerun()
