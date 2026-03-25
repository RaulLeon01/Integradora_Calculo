document.addEventListener("DOMContentLoaded", () => {
    const storageKeys = {
        equation: "utez_equation",
        y0: "utez_y0",
        y1: "utez_y1",
        aiMode: "utez_ai_mode",
        theme: "utez_theme",
        tutorialSeen: "utez_tutorial_seen",
    };

    const form = document.getElementById("solverForm");
    const equation = document.getElementById("equation");
    const y0 = document.getElementById("y0");
    const y1 = document.getElementById("y1");
    const aiModeToggle = document.getElementById("aiModeToggle");
    const themeToggle = document.getElementById("themeToggle");
    const clearButton = document.getElementById("clearButton");
    const tutorialModal = document.getElementById("tutorialModal");
    const openTutorialButton = document.getElementById("openTutorialButton");
    const closeTutorialButton = document.getElementById("closeTutorialButton");
    const skipTutorialButton = document.getElementById("skipTutorialButton");
    const finishTutorialButton = document.getElementById("finishTutorialButton");
    const askAiButton = document.getElementById("askAiButton");
    const aiResponse = document.getElementById("aiResponse");
    const aiContextNode = document.getElementById("aiContextData");

    const safeSet = (key, value) => localStorage.setItem(key, value);
    const safeGet = (key) => localStorage.getItem(key);
    const safeRemove = (key) => localStorage.removeItem(key);

    const showTutorial = () => {
        if (!tutorialModal) return;
        tutorialModal.classList.remove("hidden");
        tutorialModal.setAttribute("aria-hidden", "false");
    };

    const hideTutorial = (markSeen = true) => {
        if (!tutorialModal) return;
        tutorialModal.classList.add("hidden");
        tutorialModal.setAttribute("aria-hidden", "true");
        if (markSeen) safeSet(storageKeys.tutorialSeen, "1");
    };

    const applyTheme = (theme) => {
        const value = theme === "dark" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", value);
        if (themeToggle) themeToggle.checked = value === "dark";
        safeSet(storageKeys.theme, value);
    };

    const restoreInputs = () => {
        if (equation && !equation.value) equation.value = safeGet(storageKeys.equation) || "";
        if (y0 && !y0.value) y0.value = safeGet(storageKeys.y0) || "";
        if (y1 && !y1.value) y1.value = safeGet(storageKeys.y1) || "";
        if (aiModeToggle) {
            const savedAiMode = safeGet(storageKeys.aiMode);
            if (savedAiMode !== null) {
                aiModeToggle.checked = savedAiMode === "1";
            }
        }
    };

    restoreInputs();
    applyTheme(safeGet(storageKeys.theme) || "light");

    if (!safeGet(storageKeys.tutorialSeen)) {
        showTutorial();
    } else {
        hideTutorial(false);
    }

    [
        [equation, storageKeys.equation],
        [y0, storageKeys.y0],
        [y1, storageKeys.y1],
    ].forEach(([element, key]) => {
        if (!element) return;
        element.addEventListener("input", () => safeSet(key, element.value));
    });

    if (aiModeToggle) {
        aiModeToggle.addEventListener("change", () => {
            safeSet(storageKeys.aiMode, aiModeToggle.checked ? "1" : "0");
        });
    }

    if (themeToggle) {
        themeToggle.addEventListener("change", () => {
            applyTheme(themeToggle.checked ? "dark" : "light");
        });
    }

    if (clearButton) {
        clearButton.addEventListener("click", () => {
            [storageKeys.equation, storageKeys.y0, storageKeys.y1, storageKeys.aiMode].forEach(safeRemove);
            if (equation) equation.value = "";
            if (y0) y0.value = "";
            if (y1) y1.value = "";
            if (aiModeToggle) aiModeToggle.checked = false;
            window.location.href = "/";
        });
    }

    [openTutorialButton, closeTutorialButton, skipTutorialButton, finishTutorialButton].forEach((button) => {
        if (!button) return;
        button.addEventListener("click", () => {
            if (button === openTutorialButton) {
                showTutorial();
            } else {
                hideTutorial(true);
            }
        });
    });

    document.querySelectorAll("[data-example-equation]").forEach((button) => {
        button.addEventListener("click", () => {
            const nextEquation = button.dataset.exampleEquation || "";
            const nextY0 = button.dataset.exampleY0 || "";
            const nextY1 = button.dataset.exampleY1 || "";

            if (equation) equation.value = nextEquation;
            if (y0) y0.value = nextY0;
            if (y1) y1.value = nextY1;

            safeSet(storageKeys.equation, nextEquation);
            safeSet(storageKeys.y0, nextY0);
            safeSet(storageKeys.y1, nextY1);
            equation?.focus();
        });
    });

    if (form) {
        form.addEventListener("submit", () => {
            if (equation) safeSet(storageKeys.equation, equation.value);
            if (y0) safeSet(storageKeys.y0, y0.value);
            if (y1) safeSet(storageKeys.y1, y1.value);
            if (aiModeToggle) safeSet(storageKeys.aiMode, aiModeToggle.checked ? "1" : "0");
        });
    }

    if (askAiButton && aiResponse && aiContextNode) {
        askAiButton.addEventListener("click", async () => {
            if (aiModeToggle && !aiModeToggle.checked) {
                aiResponse.textContent = "Activa el switch de Modo IA para solicitar la explicación.";
                return;
            }

            askAiButton.disabled = true;
            aiResponse.textContent = "Generando explicación con IA...";

            try {
                const context = JSON.parse(aiContextNode.textContent || "{}");
                const response = await fetch("/api/ai-explain", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(context),
                });
                const data = await response.json();
                if (!response.ok || !data.ok) {
                    throw new Error(data.message || "No fue posible obtener la explicación.");
                }
                aiResponse.textContent = data.text;
            } catch (error) {
                aiResponse.textContent = error.message || "Error inesperado al consultar la IA.";
            } finally {
                askAiButton.disabled = false;
            }
        });
    }
});
