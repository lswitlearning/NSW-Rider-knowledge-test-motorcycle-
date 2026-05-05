import streamlit as st
import json
import os
import random

# 1. Load Data
@st.cache_data
def load_data():
    """Reads the question database from the JSON file."""
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_data()

# 2. Initialize Session State
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.total_attempted = 0
    st.session_state.answered = False
    st.session_state.is_correct = None
    st.session_state.new_q = True
    # Store indices of failed questions
    st.session_state.wrong_questions = []
    # Track if the user is in "Review Mode"
    st.session_state.review_mode = False

# --- Sidebar: Settings ---
st.sidebar.title("⚙️ Settings")

# Jump to Question (Disabled during Review Mode to avoid logic conflicts)
start_num = st.sidebar.number_input(
    f"Jump to Question (1-{len(questions)}):", 
    min_value=1, 
    max_value=len(questions), 
    value=st.session_state.q_index + 1,
    disabled=st.session_state.review_mode
)

if st.sidebar.button("Jump Now", disabled=st.session_state.review_mode):
    st.session_state.q_index = start_num - 1
    st.session_state.answered = False
    st.session_state.new_q = True
    st.rerun()

st.sidebar.divider()

# --- Sidebar: Statistics ---
st.sidebar.title("📊 Statistics")
real_total = st.session_state.total_attempted

if real_total > 0:
    st.sidebar.metric("Correct Answers", f"{st.session_state.score}")
    st.sidebar.metric("Total Attempted", f"{real_total}")
    accuracy = (st.session_state.score / real_total) * 100
    st.sidebar.write(f"**Accuracy:** {accuracy:.1f}%")
else:
    st.sidebar.info("Submit an answer to see stats!")

st.sidebar.divider()

# --- Sidebar: Review Mistakes Module ---
st.sidebar.title("🔄 Review Mode")
wrong_count = len(st.session_state.wrong_questions)
st.sidebar.write(f"Mistakes collected: **{wrong_count}**")

if wrong_count > 0:
    if not st.session_state.review_mode:
        if st.sidebar.button("🚀 Start Reviewing Mistakes"):
            st.session_state.review_mode = True
            # Jump to the first mistake in the list
            st.session_state.q_index = st.session_state.wrong_questions[0]
            st.session_state.answered = False
            st.session_state.new_q = True
            st.rerun()
    else:
        st.sidebar.warning("⚠️ Reviewing Mistakes...")
        if st.sidebar.button("🛑 Exit Review Mode"):
            st.session_state.review_mode = False
            st.session_state.new_q = True
            st.rerun()
else:
    st.sidebar.success("No mistakes! Great job.")

# 3. Question Logic & Shuffling
if st.session_state.new_q:
    q = questions[st.session_state.q_index]
    # Fetch correct answer based on "answer" index in JSON (default to 0)
    correct_idx = q.get("answer", 0) 
    st.session_state.correct_text = q["options"][correct_idx] 
    
    # Create a shuffled copy of options for the UI
    opts = q["options"].copy()
    random.shuffle(opts)
    st.session_state.current_options = opts
    st.session_state.new_q = False

# --- Main UI ---
# Show a different title if in Review Mode
display_title = "🔥 Reviewing Mistakes" if st.session_state.review_mode else "🛵 NSW Rider Knowledge Test"
st.title(display_title)

q = questions[st.session_state.q_index]
st.write(f"**Question {st.session_state.q_index + 1} / {len(questions)}**")

# Display question image if available
if q.get("image"):
    img_path = os.path.join("quiz_images", q["image"])
    if os.path.exists(img_path):
        st.image(img_path, width=250) 

st.subheader(q["question"])

# --- Question & Answer Area ---
if not st.session_state.answered:
    # Key includes index to prevent radio button state carry-over
    selected = st.radio("Select your answer:", st.session_state.current_options, key=f"r_{st.session_state.q_index}")
    
    if st.button("Submit Answer"):
        st.session_state.answered = True
        st.session_state.total_attempted += 1
        
        if selected == st.session_state.correct_text:
            st.session_state.score += 1
            st.session_state.is_correct = True
            # If answered correctly in Review Mode, remove from mistake list
            if st.session_state.review_mode and st.session_state.q_index in st.session_state.wrong_questions:
                st.session_state.wrong_questions.remove(st.session_state.q_index)
        else:
            st.session_state.is_correct = False
            # Add to mistake list if not already present
            if st.session_state.q_index not in st.session_state.wrong_questions:
                st.session_state.wrong_questions.append(st.session_state.q_index)
        st.rerun()

# --- Feedback & Navigation ---
else:
    if st.session_state.is_correct:
        st.success("✅ Correct")
    else:
        st.error("❌ Incorrect")
        st.info(f"The correct answer was: {st.session_state.correct_text}")
    
    if st.button("Next Question"):
        if st.session_state.review_mode:
            # If more mistakes exist, stay in review mode and pick the next one
            if len(st.session_state.wrong_questions) > 0:
                st.session_state.q_index = st.session_state.wrong_questions[0]
                st.session_state.answered = False
                st.session_state.new_q = True
                st.rerun()
            else:
                # No more mistakes left
                st.session_state.review_mode = False
                st.success("🎉 All mistakes cleared!")
                st.rerun()
        else:
            # Normal Practice Mode navigation
            if st.session_state.q_index < len(questions) - 1:
                st.session_state.q_index += 1
                st.session_state.answered = False
                st.session_state.new_q = True 
                st.rerun()
            else:
                st.divider()
                st.balloons()
                st.subheader("🏁 Quiz Completed!")
                st.write(f"Final Score: {st.session_state.score} / {st.session_state.total_attempted}")
                if st.button("Restart Quiz"):
                    st.session_state.q_index = 0
                    st.session_state.score = 0
                    st.session_state.total_attempted = 0
                    st.session_state.wrong_questions = []
                    st.session_state.answered = False
                    st.session_state.new_q = True
                    st.rerun()