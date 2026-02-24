<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

</head>
<body>

<h1>🎟️ Online Event Ticket Booking Platform</h1>

<p>
A robust, high-concurrency ticket engine built with <strong>FastAPI</strong> and 
<strong>Streamlit</strong>. This platform is designed to handle high-traffic event sales 
with a <strong>"security-first"</strong> and <strong>"integrity-first"</strong> approach, 
ensuring zero double-bookings and secure role-based access.
</p>

<hr>

<h2>🚀 Core Features</h2>

<h3>1. High-Concurrency Engine</h3>
<ul>
    <li>
        <strong>Pessimistic Row-Level Locking:</strong> Uses SQLAlchemy’s 
        <code>.with_for_update()</code> to lock specific seat rows during transactions, 
        preventing race conditions and double-bookings.
    </li>
    <li>
        <strong>ACID Transactions:</strong> Ensures that seat updates, order creation, 
        and ticket generation either succeed together or fail together 
        (no "orphan" bookings).
    </li>
</ul>

<h3>2. Secure Authentication &amp; RBAC</h3>
<ul>
    <li><strong>Stateless JWT:</strong> Industry-standard JSON Web Tokens for secure, scalable session management.</li>
    <li><strong>Bcrypt Hashing:</strong> All passwords are salted and hashed before storage in PostgreSQL.</li>
    <li>
        <strong>5-Tier Role-Based Access Control:</strong> Distinct permissions for 
        Admin, Organizer, Customer, Support Executive, and Entry Manager.
    </li>
</ul>

<h3>3. Comprehensive Lifecycle Management</h3>
<ul>
    <li><strong>Automated Inventory:</strong> Venue-based seat generation when an event is created.</li>
    <li><strong>Ticket Validation:</strong> Real-time gate check system that "burns" ticket codes upon entry.</li>
    <li><strong>Validated Refunds:</strong> Logic-driven refund processing that verifies the event hasn't started yet.</li>
</ul>

<hr>

<h2>🛠️ Tech Stack</h2>

<table border="1" cellpadding="8" cellspacing="0">
    <tr>
        <th>Layer</th>
        <th>Technology</th>
    </tr>
    <tr>
        <td>Frontend</td>
        <td>Streamlit (Multi-page UI)</td>
    </tr>
    <tr>
        <td>Backend</td>
        <td>FastAPI (Async Python)</td>
    </tr>
    <tr>
        <td>Database</td>
        <td>PostgreSQL</td>
    </tr>
    <tr>
        <td>ORM</td>
        <td>SQLAlchemy</td>
    </tr>
    <tr>
        <td>Security</td>
        <td>JWT, Bcrypt</td>
    </tr>
</table>

<hr>

<h2>📂 Project Structure</h2>

<pre>
backend/
│   ├── main.py          # FastAPI entry point & routes
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic data validation
│   ├── crud.py          # Database logic (Pessimistic Locking here)
│   ├── auth.py          # JWT & Bcrypt utilities
│   └── database.py      # Engine and Session configuration
frontend/
│   ├── app.py           # Main Streamlit dashboard
│   └── pages/           # Role-specific UI pages
requirements.txt         # Dependency list
</pre>

<hr>

<h2>⚙️ Installation &amp; Setup</h2>

<h3>Clone the Repository</h3>
<pre>
git clone https://github.com/yourusername/ticket-booking-platform.git
cd ticket-booking-platform
</pre>

<h3>Setup the Backend</h3>
<pre>
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
</pre>

<h3>Setup the Frontend</h3>
<pre>
cd frontend
streamlit run app.py
</pre>

<hr>

<h2>🛡️ API Endpoints (Brief)</h2>
<ul>
    <li><strong>Auth:</strong> POST /auth/register, POST /auth/login</li>
    <li><strong>Admin:</strong> POST /admin/venues/, POST /admin/events/</li>
    <li><strong>Customer:</strong> GET /events/upcoming, POST /orders/book</li>
    <li><strong>Entry Manager:</strong> POST /tickets/validate</li>
</ul>

<hr>

<h2>🧠 Critical Technical Logic: Why Pessimistic Locking?</h2>

<p>
In a ticketing environment, "Optimistic Locking" often fails during peak traffic 
(like a Coldplay concert sale) because many users fail at the final commit step. 
We chose <strong>Pessimistic Locking</strong> to lock the seat at the moment of selection, 
ensuring a <strong>"first-come, first-served"</strong> guarantee and providing a smoother 
user experience under heavy load.
</p>

</body>
</html>
