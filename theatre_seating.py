import random
import streamlit as st

ROWS = 10
SEATS = 20
TOTAL = ROWS * SEATS

st.set_page_config(page_title="Theatre Seating", page_icon="🎭", layout="wide")


# ---------- Setup: random prebooked seats (Evening[Row, Seat]) ----------
def new_evening(fill_chance=0.3):
    return [[random.random() < fill_chance for _ in range(SEATS)] for _ in range(ROWS)]


if "evening" not in st.session_state:
    st.session_state.evening = new_evening()
    st.session_state.new_seats = []   # seats booked in the latest transaction
    st.session_state.messages = []    # (type, text) output lines

evening = st.session_state.evening


# ---------- Count booked seats ----------
def count_booked():
    booked = 0
    for row in range(ROWS):
        for seat in range(SEATS):
            if evening[row][seat] is True:
                booked += 1
    return booked


# ---------- Booking logic (follows the pseudocode) ----------
def book_seats(required):
    messages = []
    st.session_state.new_seats = []

    booked = count_booked()
    available = TOTAL - booked

    if available == 0:
        messages.append(("error", "House Full"))

    if available < required:
        messages.append(("warning", f"{available} seats are available only"))
    elif available > 0:
        row = -1
        while required > 0:                     # REPEAT ... UNTIL Required = 0
            row += 1
            for seat in range(SEATS):
                if evening[row][seat] is False and required > 0:
                    evening[row][seat] = True
                    st.session_state.new_seats.append((row, seat))
                    messages.append(
                        ("success", f"Seat {seat + 1}, row {row + 1} is available")
                    )
                    required -= 1

    st.session_state.messages = messages


# ---------- Seat map ----------
def draw_seat_map():
    new = set(st.session_state.new_seats)

    css = """
    <style>
      .stage {background:#444;color:#fff;text-align:center;padding:6px;
              border-radius:6px 6px 40px 40px;margin-bottom:14px;font-weight:600;}
      .row {display:flex;align-items:center;gap:4px;margin-bottom:4px;}
      .lbl {width:28px;font-size:12px;color:#888;text-align:right;margin-right:4px;}
      .seat {flex:1;aspect-ratio:1/1;max-width:34px;border-radius:5px 5px 2px 2px;
             display:flex;align-items:center;justify-content:center;
             font-size:10px;color:#fff;}
      .free {background:#2e9e5b;}
      .taken {background:#c0392b;}
      .mine {background:#f1c40f;color:#000;font-weight:700;}
      .legend span {display:inline-block;width:14px;height:14px;border-radius:3px;
                    margin:0 4px 0 12px;vertical-align:middle;}
    </style>
    """

    html = css + '<div class="stage">STAGE</div>'

    # seat number header
    html += '<div class="row"><div class="lbl"></div>'
    for s in range(SEATS):
        html += f'<div class="seat" style="color:#888;">{s + 1}</div>'
    html += "</div>"

    for r in range(ROWS):
        html += f'<div class="row"><div class="lbl">{r + 1}</div>'
        for s in range(SEATS):
            if (r, s) in new:
                cls, label = "mine", "✔"
            elif evening[r][s]:
                cls, label = "taken", ""
            else:
                cls, label = "free", ""
            html += f'<div class="seat {cls}" title="Row {r + 1}, Seat {s + 1}">{label}</div>'
        html += "</div>"

    html += (
        '<div class="legend" style="margin-top:10px;">'
        '<span style="background:#2e9e5b"></span>Available'
        '<span style="background:#c0392b"></span>Booked'
        '<span style="background:#f1c40f"></span>Just booked</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------- UI ----------
st.title("🎭 Theatre Seating – Evening Performance")

booked_now = count_booked()
c1, c2, c3 = st.columns(3)
c1.metric("Booked", booked_now)
c2.metric("Available", TOTAL - booked_now)
c3.metric("Total seats", TOTAL)

st.write(f"**{booked_now} seats are booked.**")

draw_seat_map()

st.divider()

required = st.number_input(
    "Enter number of seats (1–4)", min_value=0, max_value=10, value=1, step=1
)

col_a, col_b = st.columns([1, 1])
if col_a.button("Book seats", type="primary"):
    # Validate
    if required < 1 or required > 4:
        st.session_state.new_seats = []
        st.session_state.messages = [("error", "Invalid input, please try again")]
    else:
        book_seats(int(required))
    st.rerun()

if col_b.button("Reset with new random bookings"):
    st.session_state.evening = new_evening()
    st.session_state.new_seats = []
    st.session_state.messages = []
    st.rerun()

for kind, text in st.session_state.messages:
    getattr(st, kind)(text)
