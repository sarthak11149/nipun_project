// Mock data for demonstration
const voters = [
    { constituency: 'A', hasVoted: true, votedFor: 'Candidate A' },
    { constituency: 'A', hasVoted: false, votedFor: '' },
    { constituency: 'B', hasVoted: true, votedFor: 'Candidate B' },
    { constituency: 'B', hasVoted: false, votedFor: '' },
    { constituency: 'B', hasVoted: true, votedFor: 'Candidate C' },
];

// Party votes storage
const votes = {
    'Party X': 0,
    'Party Y': 0,
    'Party Z': 0,
    'NOTA': 0
};

// Navigation
function navigateTo(targetId) {
    document.querySelectorAll('.container').forEach(container => {
        container.classList.remove('active');
    });
    document.getElementById(targetId).classList.add('active');
}

function selectLoginType(type) {
    navigateTo(type === 'voter' ? 'login-voter' : 'login-officer');
}

function goBack() {
    history.back();
}

function logout() {
    navigateTo('initial-page');
}

// Voter Login
function validateVoterLogin() {
    navigateTo('voter-options'); // Directly navigate to voter dashboard
}

// Officer Login
async function validateOfficerLogin() {
    const officerId = document.getElementById("officerId").value;
    const password = document.getElementById("officerPassword").value;

    const response = await fetch("/api/officerLogin", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ id: officerId, password: password }),
    });

    if (response.ok) {
        const data = await response.json();
        //alert(`Welcome, ${data.officer.name}!`);
        navigateTo('officer-dashboard'); // Redirect to the officer's dashboard
    } else {
        alert("Invalid credentials. Please try again.");
    }
}



// Registration Validation
function validateRegistrationForm(event) {
    event.preventDefault();
    const mobile = document.getElementById('mobile').value;
    const aadhaar = document.getElementById('aadhaar').value;
    if (mobile.length !== 10 || aadhaar.length !== 12) {
        alert('Enter valid Mobile and Aadhaar numbers.');
        return false;
    }
    navigateTo('voter-login');
}

// Voting
function vote(candidate) {
    alert(`You voted for ${candidate}`);
    logout();
}

// Officer Dashboard Updates
function updateDashboardStats() {
    const constituency = document.getElementById('officerConstituency').value;
    const constituencyVoters = voters.filter(v => v.constituency === constituency);
    const registered = constituencyVoters.length;
    const votesCast = constituencyVoters.filter(v => v.hasVoted).length;
    const pendingVotes = registered - votesCast;

    document.getElementById('registered-voters').textContent = registered;
    document.getElementById('votes-cast').textContent = votesCast;
    document.getElementById('pending-votes').textContent = pendingVotes;

    updateGraph(constituencyVoters);
}

function updateGraph(constituencyVoters) {
    const voteCounts = { 'Party X': 0, 'Party Y': 0, 'Party Z': 0, 'NOTA': 0 };
    constituencyVoters.forEach(v => {
        if (v.hasVoted) voteCounts[v.votedFor]++;
    });

    const ctx = document.getElementById('partyVotesChart').getContext('2d');
    if (window.partyVotesChart) window.partyVotesChart.destroy();
    window.partyVotesChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Party X', 'Party Y', 'Party Z', 'NOTA'],
            datasets: [{
                data: Object.values(voteCounts),
                backgroundColor: ['#FF5733', '#33FF57', '#3357FF', '#808080']
            }]
        }
    });
}

function forgotPassword(role) {
    alert(`Redirecting to ${role} password recovery.`);
}

function togglePasswordVisibility(inputId, iconElement) {
    const passwordInput = document.getElementById(inputId);
    const icon = iconElement.querySelector("i");
  
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      icon.classList.remove("fa-eye");
      icon.classList.add("fa-eye-slash");
    } else {
      passwordInput.type = "password";
      icon.classList.remove("fa-eye-slash");
      icon.classList.add("fa-eye");
    }
  }
  
