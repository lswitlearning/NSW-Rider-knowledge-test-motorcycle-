import streamlit as st
import json
import os
import random

# 1. Load Data
@st.cache_data
def load_data():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_data()

# 2. Initialize Session State
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.is_correct = None # Tracks if the current answer is correct

# --- Sidebar: Jump to Question ---
st.sidebar.title("Settings")
# User inputs a number (Default is 1)
start_num = st.sidebar.number_input(
    f"Start from Question (1-{len(questions)}):", 
    min_value=1, 
    max_value=len(questions), 
    value=st.session_state.q_index + 1
)

# Button to apply the jump
if st.sidebar.button("Jump to Question"):
    st.session_state.q_index = start_num - 1 # Convert to 0-based index
    st.session_state.answered = False
    st.session_state.new_q = True
    st.rerun()

st.sidebar.divider() # Add a line below the jump button

# --- 💡 Live Score Section (Below Jump Button) ---
st.sidebar.title("📊 Statistics")

# Calculate attempted questions
# It counts as attempted if the user has clicked "Submit Answer" for the current question
attempted = st.session_state.q_index + (1 if st.session_state.answered else 0)

if attempted > 0:
    # Large, clear metrics for score
    st.sidebar.metric("Correct Answers", f"{st.session_state.score}")
    st.sidebar.metric("Total Attempted", f"{attempted}")
    
    # Calculate accuracy percentage
    accuracy = (st.session_state.score / attempted) * 100
    st.sidebar.write(f"**Accuracy:** {accuracy:.1f}%")
    
    # Progress bar towards the end of the PDF
    progress = attempted / len(questions)
    st.sidebar.progress(progress)
    st.sidebar.caption(f"Overall Progress: {attempted}/{len(questions)}")
else:
    st.sidebar.info("Submit your first answer to see statistics!")

# 💡 Core Improvement: Shuffle options every time a new question is loaded
if "current_options" not in st.session_state or st.session_state.new_q:
    q = questions[st.session_state.q_index]
    # Identify the correct answer (always the first one in the original list)
    correct_text = q["options"][0]
    
    # Create a copy and shuffle the options
    opts = q["options"].copy()
    random.shuffle(opts)
    
    # Store shuffled options and correct answer text in session state
    st.session_state.current_options = opts
    st.session_state.correct_text = correct_text
    st.session_state.new_q = False

st.title("🛵 NSW Rider Knowledge Test")

# Get data for the current question
q = questions[st.session_state.q_index]

# Display Progress
st.write(f"Question {st.session_state.q_index + 1} / {len(questions)}")

# --- Display Image (Scaled down) ---
if q.get("image"):
    img_path = os.path.join("quiz_images", q["image"])
    if os.path.exists(img_path):
        st.image(img_path, width=250) 

st.subheader(q["question"])

# --- Question & Answer Area ---
if not st.session_state.answered:
    # Display radio buttons with shuffled options
    selected = st.radio("Select your answer:", st.session_state.current_options, key=f"r_{st.session_state.q_index}")
    
    if st.button("Submit Answer"):
        st.session_state.answered = True
        # Check if the selected text matches the correct answer[cite: 1]
        if selected == st.session_state.correct_text:
            st.session_state.score += 1
            st.session_state.is_correct = True
        else:
            st.session_state.is_correct = False
        st.rerun()

# --- Display Results ---
else:
    if st.session_state.is_correct:
        st.success("✅ Correct")
    else:
        st.error("❌ Incorrect")
        st.info(f"The correct answer was: {st.session_state.correct_text}")
    
    # Navigation Buttons
    if st.session_state.q_index < len(questions) - 1:
        if st.button("Next Question"):
            st.session_state.q_index += 1
            st.session_state.answered = False
            st.session_state.new_q = True 
            st.rerun()
    else:
        # 💡 This is the Final Summary Page
        st.divider() # Add a visual line
        st.balloons()
        
        # Calculate percentage
        total_qs = len(questions)
        final_score = st.session_state.score
        percentage = (final_score / total_qs) * 100
        
        # Display the Big Score
        st.subheader("🏁 Quiz Completed!")
        
        # Use columns to make it look professional
        col1, col2 = st.columns(2)
        col1.metric("Final Score", f"{final_score} / {total_qs}")
        col2.metric("Accuracy", f"{percentage:.1f}%")

        if final_score == total_qs:
            st.emoji("🏆 Perfect Score! You are ready for the test!")
        elif percentage >= 90:
            st.write("🌟 Great job! Almost there!")
        else:
            st.write("📚 Keep practicing to improve your score.")

        if st.button("Restart Quiz"):
            st.session_state.q_index = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.new_q = True
            st.rerun()