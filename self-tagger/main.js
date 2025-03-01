import './style.css'
import { setupCounter } from './counter.js'
import { OpenAI } from 'openai';

document.querySelector('#app').innerHTML = `
  <div class="container">
    <nav class="navbar">
      <h1 class="navbar-title">authring</h1>
      <button id="sso-button" class="sso-button">Connect with SSO</button>
    </nav>
    <p class="subtitle">Find your perfect team fit based on your technical experience</p>

    <div class="sso-container">
      <h2 class="sso-title">Connect your account</h2>
      <p class="sso-subtitle">Sign in to save your profile and find team matches</p>
      <div id="profile-status" class="profile-status">
        <div class="profile-disconnected">
          <p>Not connected. Sign in to save your profile and find team matches.</p>
        </div>
      </div>
    </div>

    <div class="suggestions-container">
      <h2>Suggested technologies</h2>
      <p>Click on a technology to add it to your profile</p>
      <div class="suggestions-grid" id="suggestions-grid">
        <!-- Suggestions will be added here -->
      </div>
    </div>

    <div class="assessment-container">
      <div class="column">
        <h2>Done a lot of!</h2>
        <div class="input-group">
          <input type="text" id="expert-input" placeholder="Add a technology...">
          <button id="expert-add-btn">Add</button>
        </div>
        <ul id="expert-list" class="item-list">
          <!-- Expert items will be added here -->
        </ul>
      </div>
      
      <div class="column">
        <h2>Still learning!</h2>
        <div class="input-group">
          <input type="text" id="learning-input" placeholder="Add a technology...">
          <button id="learning-add-btn">Add</button>
        </div>
        <ul id="learning-list" class="item-list">
          <!-- Learning items will be added here -->
        </ul>
      </div>
      
      <div class="column">
        <h2>Don't really know yet</h2>
        <div class="input-group">
          <input type="text" id="novice-input" placeholder="Add a technology...">
          <button id="novice-add-btn">Add</button>
        </div>
        <ul id="novice-list" class="item-list">
          <!-- Novice items will be added here -->
        </ul>
      </div>
    </div>
    
    <div class="follow-up-container">
      <h2>Tell us more about your experience</h2>
      <p class="follow-up-description">Your answers help us find the perfect team match for you</p>
      
      <div class="follow-up-questions" id="follow-up-questions">
        <!-- Follow-up questions will be added here -->
      </div>
    </div>
    
    <div class="team-match-container">
      <h2 class="team-match-title">Find your team match</h2>
      <p class="team-match-subtitle">We'll match you with teams that need your skills</p>
      <button id="match-button" class="match-button">Find team matches</button>
      <div id="match-results" class="match-results"></div>
    </div>
    
    <footer class="footer">
      <p>by <span class="footer-brand">noblox</span></p>
    </footer>
  </div>

  <div id="familiarity-modal" class="modal-overlay" style="display: none;">
    <div class="modal-container">
      <button id="modal-close" class="modal-close">×</button>
      <div class="modal-content">
        <h3>How familiar are you with <span id="tech-name"></span>?</h3>
        <div class="familiarity-options">
          <button class="familiarity-option expert-option" data-level="expert">Done a lot of!</button>
          <button class="familiarity-option learning-option" data-level="learning">Still learning!</button>
          <button class="familiarity-option novice-option" data-level="novice">Don't really know yet</button>
        </div>
      </div>
    </div>
  </div>
`
// Remove the old SSO button event listener
const oldSSOButton = document.getElementById('sso-button');
if (oldSSOButton) {
  oldSSOButton.removeEventListener('click', () => {
    if (!userProfile.isLoggedIn) {
      // In a real app, this would redirect to an SSO provider
      // For demo purposes, simulate a login
      const email = 'user@example.com';
      const role = 'developer';
      loginUser(email, role);
    }
  });
}

// Sample data
const suggestedTechnologies = [
  'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular', 
  'Node.js', 'Python', 'Java', 'C#', 'Go', 
  'AWS', 'Azure', 'Docker', 'Kubernetes', 'GraphQL',
  'MongoDB', 'PostgreSQL', 'Redis', 'Elasticsearch', 'TensorFlow'
];

// Sample team data
const teams = [
  {
    id: 1,
    name: 'Frontend Innovation Team',
    description: 'Working on cutting-edge UI/UX features for our main product',
    lookingFor: ['React', 'TypeScript', 'CSS'],
    department: 'Product Development',
    location: 'Remote / San Francisco',
    matchLevel: 'high'
  },
  {
    id: 2,
    name: 'Data Platform Team',
    description: 'Building scalable data processing pipelines and analytics tools',
    lookingFor: ['Python', 'AWS', 'PostgreSQL'],
    department: 'Data Engineering',
    location: 'Remote / New York',
    matchLevel: 'medium'
  },
  {
    id: 3,
    name: 'DevOps Transformation',
    description: 'Modernizing our deployment and infrastructure management',
    lookingFor: ['Docker', 'Kubernetes', 'Go'],
    department: 'Infrastructure',
    location: 'Remote / London',
    matchLevel: 'low'
  }
];

// Follow-up questions data
const followUpQuestions = [
  {
    id: 'work-preference',
    question: 'What type of work environment do you prefer?',
    options: ['Remote only', 'Hybrid', 'On-site', 'Flexible'],
    answer: ''
  },
  {
    id: 'team-size',
    question: 'What team size do you work best in?',
    options: ['Small (2-5 people)', 'Medium (6-15 people)', 'Large (16+ people)', 'Any size'],
    answer: ''
  },
  {
    id: 'career-goal',
    question: 'What is your primary career goal right now?',
    options: ['Deepen technical expertise', 'Move into leadership', 'Learn new technologies', 'Work on innovative projects'],
    answer: ''
  },
  {
    id: 'work-style',
    question: 'How would you describe your work style?',
    options: ['Independent worker', 'Collaborative team player', 'Flexible - depends on the project', 'Mentor/coach'],
    answer: ''
  }
];

// DOM elements
const expertInput = document.getElementById('expert-input');
const expertAddBtn = document.getElementById('expert-add-btn');
const expertList = document.getElementById('expert-list');

const learningInput = document.getElementById('learning-input');
const learningAddBtn = document.getElementById('learning-add-btn');
const learningList = document.getElementById('learning-list');

const noviceInput = document.getElementById('novice-input');
const noviceAddBtn = document.getElementById('novice-add-btn');
const noviceList = document.getElementById('novice-list');

const suggestionsGrid = document.getElementById('suggestions-grid');
const familiarityModal = document.getElementById('familiarity-modal');
const modalClose = document.getElementById('modal-close');
const techNameSpan = document.getElementById('tech-name');
const familiarityOptions = document.querySelectorAll('.familiarity-option');

const ssoButton = document.getElementById('sso-button'); // Get the new SSO button
const profileStatus = document.getElementById('profile-status');

const followUpQuestionsContainer = document.getElementById('follow-up-questions');

const matchButton = document.getElementById('match-button');
const matchResults = document.getElementById('match-results');

// User profile data
let userProfile = {
  expert: [],
  learning: [],
  novice: [],
  isLoggedIn: false,
  email: '',
  role: '',
  followUpAnswers: {}
};

// Add item to a list
function addItem(inputElement, listElement, category) {
  const value = inputElement.value.trim();
  if (value) {
    // Check if item already exists in any category
    if (
      userProfile.expert.includes(value) || 
      userProfile.learning.includes(value) || 
      userProfile.novice.includes(value)
    ) {
      alert(`${value} is already in your profile!`);
      return;
    }
    
    // Add to user profile
    userProfile[category].push(value);
    
    // Create list item
    createListItem(value, listElement, category);
    
    // Clear input
    inputElement.value = '';
    
    // Save profile if logged in
    if (userProfile.isLoggedIn) {
      saveUserProfile();
    }
  }
}

// Create a list item
function createListItem(value, listElement, category) {
  const listItemContainer = document.createElement('div');
  listItemContainer.className = 'list-item-container';
  
  const listItem = document.createElement('div');
  listItem.className = 'list-item';
  
  const itemText = document.createElement('span');
  itemText.textContent = value;
  
  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'delete-btn';
  deleteBtn.innerHTML = '×';
  deleteBtn.addEventListener('click', () => {
    // Remove from user profile
    userProfile[category] = userProfile[category].filter(item => item !== value);
    
    // Remove from DOM
    listItemContainer.remove();
    
    // Save profile if logged in
    if (userProfile.isLoggedIn) {
      saveUserProfile();
    }
  });
  
  listItem.appendChild(itemText);
  listItem.appendChild(deleteBtn);
  listItemContainer.appendChild(listItem);
  listElement.appendChild(listItemContainer);
}

// Populate suggestions
function populateSuggestions() {
  suggestionsGrid.innerHTML = '';
  
  suggestedTechnologies.forEach(tech => {
    // Skip if already in user profile
    if (
      userProfile.expert.includes(tech) || 
      userProfile.learning.includes(tech) || 
      userProfile.novice.includes(tech)
    ) {
      return;
    }
    
    const suggestionItem = document.createElement('div');
    suggestionItem.className = 'suggestion-item';
    suggestionItem.textContent = tech;
    
    suggestionItem.addEventListener('click', () => {
      techNameSpan.textContent = tech;
      familiarityModal.style.display = 'flex';
      
      // Store the selected technology for later use
      familiarityModal.dataset.technology = tech;
    });
    
    suggestionsGrid.appendChild(suggestionItem);
  });
}

// Populate follow-up questions
function populateFollowUpQuestions() {
  followUpQuestionsContainer.innerHTML = '';
  
  followUpQuestions.forEach(question => {
    const questionContainer = document.createElement('div');
    questionContainer.className = 'follow-up-question-container';
    
    const questionText = document.createElement('h3');
    questionText.className = 'follow-up-question-text';
    questionText.textContent = question.question;
    
    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'follow-up-options';
    
    question.options.forEach(option => {
      const optionBtn = document.createElement('button');
      optionBtn.className = 'follow-up-option';
      optionBtn.textContent = option;
      
      // Check if this option is already selected
      if (userProfile.followUpAnswers[question.id] === option) {
        optionBtn.classList.add('selected');
      }
      
      optionBtn.addEventListener('click', () => {
        // Remove selected class from all options in this question
        optionsContainer.querySelectorAll('.follow-up-option').forEach(btn => {
          btn.classList.remove('selected');
        });
        
        // Add selected class to this option
        optionBtn.classList.add('selected');
        
        // Save answer
        userProfile.followUpAnswers[question.id] = option;
        
        // Save profile if logged in
        if (userProfile.isLoggedIn) {
          saveUserProfile();
        }
      });
      
      optionsContainer.appendChild(optionBtn);
    });
    
    questionContainer.appendChild(questionText);
    questionContainer.appendChild(optionsContainer);
    followUpQuestionsContainer.appendChild(questionContainer);
  });
}

// Handle familiarity selection
function handleFamiliaritySelection(level) {
  const tech = familiarityModal.dataset.technology;
  
  if (tech) {
    // Add to the appropriate list
    if (level === 'expert') {
      userProfile.expert.push(tech);
      createListItem(tech, expertList, 'expert');
    } else if (level === 'learning') {
      userProfile.learning.push(tech);
      createListItem(tech, learningList, 'learning');
    } else if (level === 'novice') {
      userProfile.novice.push(tech);
      createListItem(tech, noviceList, 'novice');
    }
    
    // Close modal
    familiarityModal.style.display = 'none';
    
    // Refresh suggestions
    populateSuggestions();
    
    // Save profile if logged in
    if (userProfile.isLoggedIn) {
      saveUserProfile();
    }
  }
}

// Login user
function loginUser(email, role) {
  userProfile.isLoggedIn = true;
  userProfile.email = email;
  userProfile.role = role;
  
  // Update UI
  ssoButton.textContent = 'Connected';
  ssoButton.classList.add('connected');
  
  // Update profile status
  profileStatus.innerHTML = `
    <div class="profile-connected">
      <p>Connected as:</p>
      <p class="profile-email">${email}</p>
      <p class="vector-status">Vector profile created and synced</p>
      <button id="disconnect-btn" class="disconnect-btn">Disconnect</button>
    </div>
  `;
  
  // Add disconnect button event listener
  document.getElementById('disconnect-btn').addEventListener('click', logoutUser);
  
  // Load user profile
  loadUserProfile();
}

// Logout user
function logoutUser() {
  userProfile.isLoggedIn = false;
  userProfile.email = '';
  userProfile.role = '';
  
  // Clear lists
  expertList.innerHTML = '';
  learningList.innerHTML = '';
  noviceList.innerHTML = '';
  
  // Reset user profile
  userProfile.expert = [];
  userProfile.learning = [];
  userProfile.novice = [];
  userProfile.followUpAnswers = {};
  
  // Update UI
  ssoButton.textContent = 'Connect with SSO';
  ssoButton.classList.remove('connected');
  
  // Update profile status
  profileStatus.innerHTML = `
    <div class="profile-disconnected">
      <p>Not connected. Sign in to save your profile and find team matches.</p>
    </div>
  `;
  
  // Refresh suggestions
  populateSuggestions();
  
  // Refresh follow-up questions
  populateFollowUpQuestions();
}

// Save user profile
function saveUserProfile() {
  // In a real app, this would send data to a server
  console.log('Saving profile:', userProfile);
  
  // For demo purposes, save to localStorage
  localStorage.setItem('userProfile', JSON.stringify(userProfile));
}

// Load user profile
function loadUserProfile() {
  // In a real app, this would fetch data from a server
  console.log('Loading profile for:', userProfile.email);
  
  // For demo purposes, load from localStorage
  const savedProfile = localStorage.getItem('userProfile');
  
  if (savedProfile) {
    const parsedProfile = JSON.parse(savedProfile);
    
    // Only load if emails match
    if (parsedProfile.email === userProfile.email) {
      // Update user profile
      userProfile.expert = parsedProfile.expert || [];
      userProfile.learning = parsedProfile.learning || [];
      userProfile.novice = parsedProfile.novice || [];
      userProfile.followUpAnswers = parsedProfile.followUpAnswers || {};
      
      // Update UI
      userProfile.expert.forEach(tech => {
        createListItem(tech, expertList, 'expert');
      });
      
      userProfile.learning.forEach(tech => {
        createListItem(tech, learningList, 'learning');
      });
      
      userProfile.novice.forEach(tech => {
        createListItem(tech, noviceList, 'novice');
      });
      
      // Refresh suggestions
      populateSuggestions();
      
      // Refresh follow-up questions
      populateFollowUpQuestions();
    }
  }
}

// Find team matches
function findTeamMatches() {
  // In a real app, this would query a server
  console.log('Finding team matches for:', userProfile);
  
  // Simple matching algorithm for demo
  const matchedTeams = teams.map(team => {
    let matchScore = 0;
    let totalSkills = team.lookingFor.length;
    
    team.lookingFor.forEach(skill => {
      if (userProfile.expert.includes(skill)) {
        matchScore += 2;
      } else if (userProfile.learning.includes(skill)) {
        matchScore += 1;
      }
    });
    
    // Add bonus points for follow-up answers that match team preferences
    // This is a simplified example - in a real app, you'd have more sophisticated matching
    if (userProfile.followUpAnswers['work-preference'] === 'Remote only' && team.location.includes('Remote')) {
      matchScore += 1;
    }
    
    if (userProfile.followUpAnswers['team-size'] === 'Small (2-5 people)' && team.id === 1) {
      matchScore += 1;
    }
    
    if (userProfile.followUpAnswers['team-size'] === 'Medium (6-15 people)' && team.id === 2) {
      matchScore += 1;
    }
    
    if (userProfile.followUpAnswers['team-size'] === 'Large (16+ people)' && team.id === 3) {
      matchScore += 1;
    }
    
    const matchPercentage = Math.round((matchScore / (totalSkills * 2 + 2)) * 100);
    
    return {
      ...team,
      matchPercentage
    };
  }).sort((a, b) => b.matchPercentage - a.matchPercentage);
  
  // Display results
  displayTeamMatches(matchedTeams);
}

// Display team matches
function displayTeamMatches(matchedTeams) {
  if (!userProfile.isLoggedIn) {
    matchResults.innerHTML = `
      <div class="match-error">
        <p>Please connect with SSO to find team matches</p>
      </div>
    `;
    return;
  }
  
  if (matchedTeams.length === 0) {
    matchResults.innerHTML = `
      <div class="match-error">
        <p>No team matches found. Try adding more technologies to your profile.</p>
      </div>
    `;
    return;
  }
  
  matchResults.innerHTML = `
    <div class="match-success">
      <h3>We found ${matchedTeams.length} potential team matches!</h3>
      <div class="teams-container" id="teams-container"></div>
      <p class="match-note">Teams are matched based on your technical experience and their needs</p>
    </div>
  `;
  
  const teamsContainer = document.getElementById('teams-container');
  
  matchedTeams.forEach(team => {
    const matchClass = team.matchLevel;
    const matchText = team.matchPercentage >= 70 ? 'High match' : team.matchPercentage >= 40 ? 'Medium match' : 'Potential match';
    const matchBadgeClass = team.matchPercentage >= 70 ? 'match-high' : team.matchPercentage >= 40 ? 'match-medium' : 'match-low';
    
    const teamCard = document.createElement('div');
    teamCard.className = `team-card team-match-${matchClass}`;
    
    teamCard.innerHTML = `
      <div class="team-header">
        <h4>${team.name}</h4>
        <span class="match-badge ${matchBadgeClass}">${matchText} (${team.matchPercentage}%)</span>
      </div>
      <p class="team-description">${team.description}</p>
      <div class="team-details">
        <p><strong>Looking for:</strong> ${team.lookingFor.join(', ')}</p>
        <p><strong>Department:</strong> ${team.department}</p>
        <p><strong>Location:</strong> ${team.location}</p>
      </div>
      <button class="team-contact-btn" data-team-id="${team.id}">Express Interest</button>
    `;
    
    teamsContainer.appendChild(teamCard);
  });
  
  // Add event listeners to contact buttons
  document.querySelectorAll('.team-contact-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const teamId = e.target.dataset.teamId;
      const team = matchedTeams.find(t => t.id === parseInt(teamId));
      
      if (team) {
        expressInterest(team);
      }
    });
  });
}

// Express interest in a team
function expressInterest(team) {
  // In a real app, this would send a request to the server
  console.log('Expressing interest in team:', team);
  
  // For demo purposes, show a confirmation
  matchResults.innerHTML = `
    <div class="match-success">
      <h3>Interest Sent!</h3>
      <p class="interest-message">
        You've expressed interest in joining the <strong>${team.name}</strong>. 
        The team lead will be notified and will contact you if there's a good fit.
      </p>
      <button id="back-to-matches" class="interest-confirm-btn">Back to Matches</button>
    </div>
  `;
  
  // Add event listener to back button
  document.getElementById('back-to-matches').addEventListener('click', findTeamMatches);
}

// Event listeners
expertAddBtn.addEventListener('click', () => {
  addItem(expertInput, expertList, 'expert');
});

learningAddBtn.addEventListener('click', () => {
  addItem(learningInput, learningList, 'learning');
});

noviceAddBtn.addEventListener('click', () => {
  addItem(noviceInput, noviceList, 'novice');
});

// Enter key support for inputs
expertInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    addItem(expertInput, expertList, 'expert');
  }
});

learningInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    addItem(learningInput, learningList, 'learning');
  }
});

noviceInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    addItem(noviceInput, noviceList, 'novice');
  }
});

// Modal close button
modalClose.addEventListener('click', () => {
  familiarityModal.style.display = 'none';
});

// Close modal when clicking outside
familiarityModal.addEventListener('click', (e) => {
  if (e.target === familiarityModal) {
    familiarityModal.style.display = 'none';
  }
});

// Familiarity options
familiarityOptions.forEach(option => {
  option.addEventListener('click', () => {
    const level = option.dataset.level;
    handleFamiliaritySelection(level);
  });
});

// SSO button
ssoButton.addEventListener('click', () => {
  if (!userProfile.isLoggedIn) {
    // In a real app, this would redirect to an SSO provider
    // For demo purposes, simulate a login
    const email = 'user@example.com';
    const role = 'developer';
    loginUser(email, role);
  }
});

// Match button
matchButton.addEventListener('click', findTeamMatches);

// Initialize
populateSuggestions();
populateFollowUpQuestions();