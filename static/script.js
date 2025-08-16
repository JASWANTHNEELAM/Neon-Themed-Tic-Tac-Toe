// This script runs only on the game page.
// (It’s safe if loaded elsewhere; it just won’t find the board.)

(function () {
  const boardEl = document.getElementById("board");
  if (!boardEl) return; // not on game page

  const cells = Array.from(boardEl.querySelectorAll(".cell"));
  const turnEl = document.getElementById("turn-indicator");

  // Injected globals from game.html
  const mode = typeof MODE !== "undefined" ? MODE : "PvP";
  const level = typeof LEVEL !== "undefined" ? LEVEL : "easy";
  const p1Symbol = typeof P1SYMBOL !== "undefined" ? P1SYMBOL : "X";
  const p2Symbol = typeof P2SYMBOL !== "undefined" ? P2SYMBOL : "O";

  // Game state uses 'p1'/'p2' markers, UI shows chosen symbols
  let board = Array(9).fill(null);
  let turn = "p1"; // P1 always starts (clear & consistent)
  updateTurnUI();

  // Win lines
  const WINS = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6],
  ];

  // --- Event binding ---
  cells.forEach((c, idx) => c.addEventListener("click", () => onHumanMove(idx)));

  document.getElementById("restart")?.addEventListener("click", restart);

  // If CPU should start (rare, since P1 starts), you could change rules here.
  // Current rule: P1 always starts.

  // --- Handlers ---
  function onHumanMove(idx) {
  if (board[idx] || gameOver()) return;
  if (mode === "PvC" && turn === "p2") return; // block clicks during AI turn

  place(idx, turn);   // ✅ use current turn

  if (!gameOver() && mode === "PvC" && turn === "p2") {
    setTimeout(cpuMove, 450);
  }
}

  function place(idx, who) {
    board[idx] = who;
    const symbol = who === "p1" ? p1Symbol : p2Symbol;
    cells[idx].textContent = symbol;
    cells[idx].classList.add(who);
    cells[idx].disabled = true;

    

    if (checkWinner(board, who)) {
  setTimeout(() => showPopup(`${symbol} wins!`), 10);
  lockBoard();
  return;
}
if (board.every(Boolean)) {
  setTimeout(() => showPopup(`Draw!`), 10);
  return;
}


    turn = who === "p1" ? "p2" : "p1";
    updateTurnUI();
  }
function showPopup(msg) {
  const popup = document.getElementById("popup");
  const msgEl = document.getElementById("popup-message");

  // Customize message
  if (msg.includes("wins")) {
    msgEl.textContent = `🎉 Hurray! ${msg} 🎉`;
  } else if (msg.includes("Draw")) {
    msgEl.textContent = `🤝 It's a draw!`;
  } else {
    msgEl.textContent = msg;
  }

  popup.classList.remove("hidden");

  // Close button
  document.getElementById("popup-close").onclick = () => {
    popup.classList.add("hidden");
  };
}


  function cpuMove() {
    // Compute best move according to level
    const move = pickAIMove(board.slice(), level);
    if (move == null) return;
    place(move, "p2");
  }

  function restart() {
    clearStrike(); 
    board = Array(9).fill(null);
    turn = "p1";
    cells.forEach(c => {
      c.textContent = "";
      c.classList.remove("p1", "p2");
      c.disabled = false;
    });
    updateTurnUI();
  }

  // --- Helpers/UI ---
  function updateTurnUI() {
    const symbol = turn === "p1" ? p1Symbol : p2Symbol;
    if (turnEl) turnEl.textContent = symbol;
  }
  function lockBoard() {
    cells.forEach(c => c.disabled = true);
  }
  function gameOver() {
    return checkWinner(board, "p1") || checkWinner(board, "p2") || board.every(Boolean);
  }

  function checkWinner(b, who) {
  for (const line of WINS) {
    if (line.every(i => b[i] === who)) {
      drawStrike(line);   // <-- draw strike when win found
      return true;
    }
  }
  return false;
}
function drawStrike(line) {
  const strike = document.getElementById("strike");
  const rect = document.getElementById("board").getBoundingClientRect();
  const cellRects = line.map(i => cells[i].getBoundingClientRect());

  const x1 = (cellRects[0].left + cellRects[0].right) / 2;
  const y1 = (cellRects[0].top + cellRects[0].bottom) / 2;
  const x2 = (cellRects[2].left + cellRects[2].right) / 2;
  const y2 = (cellRects[2].top + cellRects[2].bottom) / 2;

  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.sqrt(dx * dx + dy * dy);

  strike.style.width = length + "px";
  strike.style.transform = `translate(${x1 - rect.left}px, ${y1 - rect.top}px) rotate(${Math.atan2(dy, dx)}rad) scaleX(1)`;
}

function clearStrike() {
  const strike = document.getElementById("strike");
  if (!strike) return;
  // hide instantly (no reverse animation), then restore transition
  strike.style.transition = "none";
  strike.style.transform = "scaleX(0)";
  strike.style.width = "0px";
  // force reflow, then restore transition for next win
  void strike.offsetHeight;
  strike.style.transition = "transform 0.4s ease-in-out";
}


  // --- AI ---
  function pickAIMove(b, lvl) {
    const empty = b.map((v,i)=>v?null:i).filter(v=>v!==null);
    if (!empty.length) return null;

    if (lvl === "easy") {
      return empty[Math.floor(Math.random()*empty.length)];
    }

    if (lvl === "normal") {
      // 1) Win if possible
      for (const i of empty) {
        b[i] = "p2";
        if (checkWinner(b, "p2")) { b[i]=null; return i; }
        b[i] = null;
      }
      // 2) Block human win
      for (const i of empty) {
        b[i] = "p1";
        if (checkWinner(b, "p1")) { b[i]=null; return i; }
        b[i] = null;
      }
      // 3) Otherwise random
      return empty[Math.floor(Math.random()*empty.length)];
    }

    // hard: minimax (optimal)
    const best = minimax(b, true);
    return best.index;
  }

  function minimax(b, isMax) {
    // terminal check
    if (checkWinner(b, "p2")) return { score: 10 };
    if (checkWinner(b, "p1")) return { score: -10 };
    if (b.every(Boolean))    return { score: 0 };

    const empty = b.map((v,i)=>v?null:i).filter(v=>v!==null);
    if (isMax) {
      let best = { score: -Infinity, index: null };
      for (const i of empty) {
        b[i] = "p2";
        const res = minimax(b, false);
        b[i] = null;
        if (res.score > best.score) best = { score: res.score, index: i };
      }
      return best;
    } else {
      let best = { score: Infinity, index: null };
      for (const i of empty) {
        b[i] = "p1";
        const res = minimax(b, true);
        b[i] = null;
        if (res.score < best.score) best = { score: res.score, index: i };
      }
      return best;
    }
  }
  
})();

