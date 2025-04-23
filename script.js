function closePopup() {
    document.getElementById('welcome-popup-overlay').style.display = 'none';
}

function openPopup() {
    document.getElementById('welcome-popup-overlay').style.display = 'flex';
}

function loadFile(filename) {
    const ext = filename.split('.').pop();
    const url = filename + "?nocache=" + new Date().getTime(); // bust the cache

    fetch(url)
        .then(res => res.text())
        .then(text => {
            const container = document.getElementById("code-window");
            if (ext === 'md') {
                container.innerHTML = marked.parse(text);
            } else if (ext === 'py' || ext === 'txt') {
                container.innerHTML = `<pre><code class="language-python">${text.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
                hljs.highlightAll();
            }
        });
}

function loadProjectsInto(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    // Load and insert markdown first
    fetch("projects.md" + "?nocache=" + new Date().getTime())
        .then(res => res.text())
        .then(text => {
            const markdown = document.createElement("div");
            markdown.className = "projects-markdown";
            markdown.innerHTML = marked.parse(text);
            container.appendChild(markdown);

            // Then load and insert project grid
            const grid = document.createElement("div");
            grid.className = "project-grid";
            grid.id = "project-grid";
            container.appendChild(grid);

            fetch("projects-cache.json")
                .then(res => res.json())
                .then(data => {
                    data.forEach(entry => {
                        const keywordClass = entry.keyword ? entry.keyword.toLowerCase().replace(/\s+/g, '-') : "";
                        const badge = entry.keyword ? `<div class="keyword-badge">${entry.keyword}</div>` : "";
                        const demoLink = entry.demo ? `<a href="${entry.demo}" target="_blank">Demo</a>` : "";

                        const card = document.createElement("div");
                        card.className = "project-card";
                        if (keywordClass) card.setAttribute("data-keyword", keywordClass);

                        card.innerHTML = `
                <h3>▸ ${entry.name}/</h3>
                ${badge}
                <p>${entry.description || "No description available."}</p>
                <div class="project-meta">
                  Language: ${entry.language || "Unknown"} <br>
                  ★ ${entry.stargazers_count} &nbsp;&nbsp; ⑂ ${entry.forks_count} <br>
                  Last Updated: ${new Date(entry.updated_at).toISOString().split('T')[0]}
                </div>
                <div class="project-links">
                  <a href="${entry.html_url}" target="_blank">GitHub</a>
                  ${demoLink}
                </div>
              `;
                        grid.appendChild(card);
                    });
                });
        });
}

function insertEmailLink(anchorId = "email-link") {
    const user = "christina.l.hed";
    const domain = "nasa.g";
    const email = `${user}ges@${domain}ov`;

    const link = document.getElementById(anchorId);
    if (link) {
        link.href = `mailto:${email}`;
        link.textContent = "📧 Contact";
    }
}


document.addEventListener("DOMContentLoaded", () => {
    // Set up sidebar click listeners
    document.querySelectorAll(".sidebar li").forEach(item => {
        item.addEventListener("click", () => {
            const filename = item.textContent.trim().replace(/🧪|🛠️|📖|🗒️|📄|📗/g, '').trim();
            if (filename === "projects/") {
                loadProjectsInto("code-window");
            } else if (filename === "missions/") {
                const container = document.getElementById("code-window");
                container.innerHTML = "";

                // Load markdown intro
                fetch("missions.md" + "?nocache=" + new Date().getTime())
                    .then(res => res.text())
                    .then(md => {
                        const introWrapper = document.createElement("div");
                        introWrapper.className = "code-window";  // reuse same layout style
                        introWrapper.innerHTML = marked.parse(md);
                        container.appendChild(introWrapper);

                        // Load mission cards after intro
                        fetch("missions-content.html")
                            .then(res => res.text())
                            .then(html => {
                                const grid = document.createElement("div");
                                grid.className = "mission-grid";
                                grid.innerHTML = html;
                                container.appendChild(grid);
                            });
                    });
            } else {
                loadFile(filename);
            }
        });
    });

    // Load readme.md by default on page load
    loadFile("readme.md");
    insertEmailLink();
});


