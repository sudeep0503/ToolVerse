// Helper: read query params
function getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    const level = parseInt(params.get("level") || "0", 10);
    const parent = params.get("parent") || null;
    const node = params.get("node") || null;
    return { level, parent, node };
}

// Helper: create and render cards
function renderCards(container, count, titlePrefix, subtitleText, onClickCard) {
    container.innerHTML = "";

    for (let i = 1; i <= count; i++) {
        const card = document.createElement("div");
        card.className = "card";

        const title = document.createElement("div");
        title.className = "card-title";
        title.textContent = `${titlePrefix} ${i}`;

        const subtitle = document.createElement("div");
        subtitle.className = "card-subtitle";
        subtitle.textContent = subtitleText;

        const footer = document.createElement("div");
        footer.className = "card-footer";
        footer.textContent = "Click to navigate deeper";

        card.appendChild(title);
        card.appendChild(subtitle);
        card.appendChild(footer);

        card.addEventListener("click", () => onClickCard(i));
        container.appendChild(card);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const { level, parent, node } = getQueryParams();

    const cardsContainer = document.getElementById("cards-container");
    const pageTitle = document.getElementById("page-title");
    const btnForward = document.getElementById("btn-forward");
    const btnBackward = document.getElementById("btn-backward");

    // Root level: 10 cards
    if (level === 0) {
        pageTitle.textContent = "Root Level – Main Tools";

        renderCards(
            cardsContainer,
            10,
            "Root Card",
            "Top-level option in your hierarchy",
            (i) => {
                // Navigate to child "page" (same HTML, different params)
                const url = `${window.location.pathname}?level=1&parent=root&node=${i}`;
                window.location.href = url;
            }
        );

        // At root, no parent → Backward disabled
        btnBackward.classList.add("disabled");
        btnBackward.disabled = true;

        // Forward: as an example, dive into first child node
        btnForward.addEventListener("click", () => {
            const url = `${window.location.pathname}?level=1&parent=root&node=1`;
            window.location.href = url;
        });
    }

    // Level 1: child of root → 3 cards
    if (level === 1 && parent === "root") {
        pageTitle.textContent = `Node ${node} – Child Options`;

        renderCards(
            cardsContainer,
            3,
            `Child of ${node}`,
            "Second-level node in the tree",
            (i) => {
                // Placeholder for deeper hierarchy
                alert(
                    `This is where you'd go deeper:\nParent node = ${node}, child index = ${i}`
                );
            }
        );

        // Backward: go one branch up (to root)
        btnBackward.disabled = false;
        btnBackward.classList.remove("disabled");
        btnBackward.addEventListener("click", () => {
            window.location.href = window.location.pathname; // root = no params
        });

        // Forward: currently no deeper level wired → disabled for now
        btnForward.classList.add("disabled");
        btnForward.disabled = true;
    }
});
