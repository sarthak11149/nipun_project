import firebase_admin
from firebase_admin import credentials, db
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://voting-project-19145-default-rtdb.firebaseio.com/"
})

# Initialize FastAPI app
app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Models
class User(BaseModel):
    name: str
    mobile: str
    aadhaar: str
    voter_id: str
    password: str
    constituency: str
    hasVoted: bool = False  # Set default hasVoted to False

class LoginRequest(BaseModel):
    voter_id: str
    password: str

class VoteRequest(BaseModel):
    voter_id: str
    candidate: str

class OfficerLoginRequest(BaseModel):
    id: str
    password: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/register")
def register_user(user: User):
    ref = db.reference("users")
    if ref.child(user.voter_id).get():
        raise HTTPException(status_code=400, detail="Voter ID already exists.")
    
    # Store the user with hasVoted set to False
    ref.child(user.voter_id).set(user.dict())
    return {"message": "User registered successfully."}

@app.post("/api/login")
def login_user(login: LoginRequest):
    ref = db.reference("users")
    user = ref.child(login.voter_id).get()
    
    if not user or user["password"] != login.password:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    # Return login success and the hasVoted status
    return {"message": "Login successful.", "user": user, "hasVoted": user["hasVoted"]}

@app.post("/api/vote")
def cast_vote(vote: VoteRequest):
    ref_users = db.reference("users")
    ref_votes = db.reference("votes")
    
    # Check if the voter exists and get their constituency
    user = ref_users.child(vote.voter_id).get()
    if not user:
        raise HTTPException(status_code=400, detail="Voter not found.")
    
    # Check if the voter has already voted
    if ref_votes.child(vote.voter_id).get():
        raise HTTPException(status_code=400, detail="Vote already cast.")
    
    # Get the voter's constituency
    constituency = user.get("constituency")

    # Record the vote along with the constituency
    ref_votes.child(vote.voter_id).set({
        "candidate": vote.candidate,
        "constituency": constituency  # Save the constituency along with the vote
    })
    
    return {"message": f"Vote for {vote.candidate} cast successfully."}

@app.post("/api/officerLogin")
def officer_login(officer: OfficerLoginRequest):
    ref = db.reference("officers")
    officer_data = ref.child(officer.id).get()
    if not officer_data or officer_data["password"] != officer.password:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    return {"message": "Login successful.", "officer": officer_data}

@app.get("/api/checkVoteStatus")
def check_vote_status(voter_id: str):
    ref = db.reference("votes")
    have_voted = ref.child(voter_id).get() is not None
    return {"haveVoted": have_voted}

@app.get("/api/results")
def get_results():
    ref = db.reference("votes")
    votes = ref.get()
    if not votes:
        return {"message": "No votes cast yet."}
    
    results = {}
    for vote in votes.values():
        candidate = vote["candidate"]
        results[candidate] = results.get(candidate, 0) + 1
    
    return {"results": results}

@app.get("/api/officer-stats")
def officer_stats(constituency: str):
    # Get stats for officer dashboard
    users_ref = db.reference("users")
    votes_ref = db.reference("votes")
    
    # Registered voters (total count of users in the given constituency)
    registered_voters = len([user for user in users_ref.get().values() if user.get("constituency").lower() == constituency.lower()])
    
    # Votes cast (count of votes cast in the given constituency)
    votes_cast = len([vote for vote in votes_ref.get().values() if vote.get("constituency").lower() == constituency.lower()])
    
    # Pending votes (users who haven't voted in the given constituency)
    pending_votes = registered_voters - votes_cast
    
    # Count votes by party for the given constituency
    votes_by_party = {"Party X": 0, "Party Y": 0, "Party Z": 0, "NOTA": 0}  # Initialize counts for all candidates

    votes_data = votes_ref.get()
    print("Votes Data:", votes_data)


    for vote in votes_ref.get().values():
        # Filter votes by the constituency
        if vote.get("constituency").lower() == constituency.lower():
            candidate = vote.get("candidate")  # Ensure we get the candidate field correctly
            if candidate in votes_by_party:
                votes_by_party[candidate] += 1
    print(votes_by_party)
    return {
        "registeredVoters": registered_voters,
        "votesCast": votes_cast,
        "pendingVotes": pending_votes,
        "votesByParty": votes_by_party
    }
