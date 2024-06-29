document.addEventListener("DOMContentLoaded", () => {
    startGame();
});

function startGame() {
    fetch('/start')
        .then(response => response.json())
        .then(data => {
            console.log('Game started:', data);
            updateGame(data);
        });
}

function bet(action, amount = 0) {
    console.log(`Bet action: ${action}, amount: ${amount}`);
    fetch('/bet', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action, amount })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Bet response:", data);
        updateGame(data.hands);
        if (data.stage === 4 && data.result) {
            document.getElementById("bot-hand").innerHTML = "Hand: " + formatHand(data.hands.bot);
            document.getElementById("player-stack").innerText = "Stack: " + data.player_stack;
            document.getElementById("bot-stack").innerText = "Stack: " + data.bot_stack;
            document.getElementById("actions").style.display = "none";
            document.getElementById("next-hand-section").style.display = "block";
        }
        if (data.log) {
            updateLog(data.log);
        }
        if (data.endgame) {
            document.getElementById("actions").style.display = "none";
            document.getElementById("game-over-message").innerText = data.game_over_message;
        }
    });
}

function updateLog(log) {
    const logDiv = document.getElementById("log");
    logDiv.innerHTML = "";
    log.forEach(entry => {
        const entryDiv = document.createElement("div");
        entryDiv.innerHTML = formatLogMessage(entry);
        logDiv.appendChild(entryDiv);
    });
}

function formatLogMessage(entry) {
    let message = '';
    if (entry.type === 'log-player') {
        message = `<span style="color: blue;">Player:</span> <span style="color: black;">${entry.message.replace('Player:', '')}</span>`;
    } else if (entry.type === 'log-bot') {
        message = `<span style="color: red;">Bot:</span> <span style="color: black;">${entry.message.replace('Bot:', '')}</span>`;
    } else if (entry.type === 'log-result') {
        message = `<span style="color: green;">${entry.message}</span><br>Player's Best Hand:<br>${formatHand(entry.player_best_hand)}<br>Bot's Best Hand:<br>${formatHand(entry.bot_best_hand)}`;
    }
    return message;
}

function updateGame(data) {
    document.getElementById("player-hand").innerHTML = "Hand: " + formatHand(data.player);
    document.getElementById("bot-hand").innerHTML = "Hand: " + formatHand(data.bot); // Update bot's hand
    document.getElementById("community-cards").innerHTML = formatHand(data.community);
    document.getElementById("pot").innerText = "Pot: " + data.pot;
    document.getElementById("player-stack").innerText = "Stack: " + data.player_stack;
    document.getElementById("bot-stack").innerText = "Stack: " + data.bot_stack;
    document.getElementById("player-label").innerText = data.player_label;
    document.getElementById("bot-label").innerText = data.bot_label;
}

function raise() {
    const amount = prompt("Enter raise amount:");
    if (amount) {
        bet('raise', amount);
    }
}

function allIn() {
    bet('raise', 'all in');
}

function check() {
    bet('check');
}

function fold() {
    bet('fold');
}

function nextHand() {
    console.log("Starting next hand");
    fetch('/next_hand', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Next hand response:", data);
        updateGame(data.hands);
        document.getElementById("result").innerText = "";
        document.getElementById("actions").style.display = "block";
        document.getElementById("next-hand-section").style.display = "none";
        updateLog(data.log);
    });
}

function formatHand(hand) {
    return hand.map(card => {
        const suit = card.slice(-1);
        const rank = card.slice(0, -1);
        const color = (suit === '♥' || suit === '♦') ? 'red' : 'black';
        return `<span style="color: ${color};">${rank}${suit}</span>`;
    }).join(' ');
}
