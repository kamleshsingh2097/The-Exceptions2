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
with a <strong>security-first</strong> and <strong>integrity-first</strong> approach, 
ensuring zero double-bookings and secure role-based access.
</p>

<hr>

<h2>🚀 Core Features</h2>

<h3>1. High-Concurrency Engine</h3>
<ul>
    <li><strong>Pessimistic Row-Level Locking:</strong> Uses SQLAlchemy’s <code>.with_for_update()</code> to lock specific seat rows during transactions, preventing race conditions and double-bookings.</li>
    <li><strong>ACID Transactions:</strong> Ensures that seat updates, order creation, and ticket generation either succeed together or fail together (no orphan bookings).</li>
</ul>

<h3>2. Secure Authentication &amp; RBAC</h3>
<ul>
    <li><strong>Stateless JWT:</strong> Industry-standard JSON Web Tokens for secure, scalable session management.</li>
    <li><strong>Bcrypt Hashing:</strong> All passwords are salted and hashed before storage in PostgreSQL.</li>
    <li><strong>5-Tier Role-Based Access Control:</strong> Distinct permissions for Admin, Organizer, Customer, Support Executive, and Entry Manager.</li>
</ul>

<h3>3. Comprehensive Lifecycle Management</h3>
<ul>
    <li><strong>Automated Inventory:</strong> Venue-based seat generation when an event is created.</li>
    <li><strong>Ticket Validation:</strong> Real-time gate check system that burns ticket codes upon entry.</li>
    <li><strong>Validated Refunds:</strong> Logic-driven refund processing that verifies the event has not started yet.</li>
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
.
├── backend/
│   ├── main.py              # FastAPI entry point & routes
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic data validation
│   ├── crud.py              # Database logic (pessimistic locking)
│   ├── auth.py              # JWT & Bcrypt utilities
│   ├── database.py          # Engine and Session configuration
│   └── utils/
│       ├── __init__.py
│       └── payment.py
├── frontend/
│   ├── app.py               # Main Streamlit dashboard
│   ├── Login_Register.py
│   ├── pages/               # Role-specific UI pages
│   │   ├── Customer.py
│   │   ├── Event_Organizer.py
│   │   ├── Support_Executive.py
│   │   └── Entry_Manager.py
│   └── utils/
│       ├── email_sim.py
│       └── pdf_gen.py
├── requirementb.txt         # Backend dependencies
└── requirementf.txt         # Frontend dependencies
</pre>

<hr>

<h2>⚙️ Installation &amp; Setup</h2>

<h3>1. Clone the Repository</h3>
<pre><code>git clone https://github.com/yourusername/ticket-booking-platform.git
cd ticket-booking-platform
</code></pre>

<h3>2. Create and Activate Virtual Environment</h3>
<pre><code>python -m venv venv
source venv/bin/activate
</code></pre>

<h3>3. Install Dependencies</h3>
<pre><code>pip install -r requirementb.txt
pip install -r requirementf.txt
</code></pre>

<h3>4. Run the Backend (FastAPI)</h3>
<pre><code>cd backend
uvicorn main:app --reload
</code></pre>

<h3>5. Run the Frontend (Streamlit)</h3>
<pre><code>cd frontend
streamlit run app.py
</code></pre>

<hr>

<h2>🛡️ API Endpoints (Brief)</h2>

<ul>
    <li><strong>Auth:</strong> <code>POST /auth/register</code>, <code>POST /auth/login</code></li>
    <li><strong>Admin:</strong> <code>POST /admin/venues/</code>, <code>POST /admin/events/</code></li>
    <li><strong>Customer:</strong> <code>GET /events/upcoming</code>, <code>POST /orders/book</code></li>
    <li><strong>Entry Manager:</strong> <code>POST /tickets/validate</code></li>
</ul>

<hr>

<h2>🧠 Critical Technical Logic: Why Pessimistic Locking?</h2>

<p>
In a ticketing environment, optimistic locking often fails during peak traffic 
(like high-demand concert sales) because many users fail at the final commit step. 
This project uses <strong>pessimistic locking</strong> to lock the seat at selection time, 
enforcing a <strong>first-come, first-served</strong> guarantee and delivering a smoother 
user experience under heavy load.
</p>

</body>
</html>
