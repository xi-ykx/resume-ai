const API_BASE = "http://127.0.0.1:8000";
const MAX_CHARS = 8000;
let copyText = "";

const resumeTextEl = document.getElementById("resumeText");
const charCountEl = document.getElementById("charCount");
const jsonBtn = document.getElementById("jsonBtn");
const streamBtn = document.getElementById("streamBtn");
const copyBtn = document.getElementById("copyBtn");
const resultDiv = document.getElementById("result");
const historyList = document.getElementById("historyList");

// ── Char counter ──
resumeTextEl.addEventListener("input", () => {
    const len = resumeTextEl.value.length;
    charCountEl.textContent = `${len} / ${MAX_CHARS}`;
    charCountEl.className = "char-count" +
        (len > MAX_CHARS ? " over" : len > MAX_CHARS * 0.85 ? " warn" : "");
});

// ── Tabs ──
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
        if (btn.dataset.tab === "history") loadHistory();
    });
});

// ── Button events ──
jsonBtn.addEventListener("click", polishResumeJson);
streamBtn.addEventListener("click", polishResumeStream);
copyBtn.addEventListener("click", copyOptimizedResume);

// ── Toast ──
function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
}

// ── Helpers ──
function setCopyText(text) {
    copyText = text || "";
    copyBtn.disabled = !copyText;
}

function showError(message) {
    resultDiv.innerHTML = `<div class="error-card"><span class="icon">&#x26A0;</span><span>${escapeHtml(message)}</span></div>`;
}

function showLoading() {
    resultDiv.innerHTML = '<div class="loading-hint"><div class="spinner"></div><span>AI 正在分析你的简历，请稍等...</span></div>';
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function valueOrFallback(value) {
    if (Array.isArray(value)) return value.length > 0 ? value : ["暂无内容"];
    return value || "暂无内容";
}

function createResultSection(title, content) {
    const section = document.createElement("div");
    section.className = "result-section";
    const h3 = document.createElement("h3");
    h3.textContent = title;
    const box = document.createElement("div");
    box.className = "result-box";
    box.textContent = Array.isArray(content)
        ? content.map(item => "• " + item).join("\n")
        : content;
    section.append(h3, box);
    return section;
}

// ── Clipboard ──
async function writeToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
    }
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
}

async function copyOptimizedResume() {
    if (!copyText) return;
    try {
        await writeToClipboard(copyText);
        showToast("已复制到剪贴板");
    } catch {
        showToast("复制失败，请手动选择文本");
    }
}

// ── Error reader ──
async function readErrorMessage(response) {
    try {
        const data = await response.json();
        if (typeof data.detail === "string") return data.detail;
        if (Array.isArray(data.detail) && data.detail.length > 0) {
            return data.detail[0].msg || "请求参数不正确";
        }
        return "请求失败";
    } catch {
        return "请求失败";
    }
}

// ── JSON API ──
async function polishResumeJson() {
    const jobTarget = document.getElementById("jobTarget").value.trim();
    const resumeText = resumeTextEl.value.trim();
    const origText = jsonBtn.textContent;

    if (!resumeText) { showError("请填写简历内容。"); return; }
    if (resumeText.length > MAX_CHARS) { showError(`简历内容不能超过 ${MAX_CHARS} 字。`); return; }

    jsonBtn.disabled = true;
    jsonBtn.innerHTML = '<span class="spinner"></span> 处理中...';
    setCopyText("");
    showLoading();

    try {
        const resp = await fetch(API_BASE + "/polish-resume-json", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ job_target: jobTarget, resume_text: resumeText })
        });

        if (!resp.ok) throw new Error(await readErrorMessage(resp));

        const data = await resp.json();
        setCopyText(data.optimized_resume || "");
        resultDiv.replaceChildren(
            createResultSection("一、优化后的简历", valueOrFallback(data.optimized_resume)),
            createResultSection("二、修改理由", valueOrFallback(data.reasons)),
            createResultSection("三、关键词建议", valueOrFallback(data.problem_analysis))
        );
    } catch (e) {
        showError("出错了：" + e.message);
    } finally {
        jsonBtn.disabled = false;
        jsonBtn.textContent = origText;
    }
}

// ── Stream API ──
async function polishResumeStream() {
    const jobTarget = document.getElementById("jobTarget").value.trim();
    const resumeText = resumeTextEl.value.trim();
    const origText = streamBtn.textContent;

    if (!resumeText) { showError("请填写简历内容。"); return; }
    if (resumeText.length > MAX_CHARS) { showError(`简历内容不能超过 ${MAX_CHARS} 字。`); return; }

    streamBtn.disabled = true;
    streamBtn.innerHTML = '<span class="spinner"></span> 处理中...';
    setCopyText("");
    const box = document.createElement("div");
    box.className = "result-box";
    resultDiv.replaceChildren(box);

    try {
        const resp = await fetch(API_BASE + "/polish-resume-stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ job_target: jobTarget, resume_text: resumeText })
        });

        if (!resp.ok) throw new Error(await readErrorMessage(resp));

        const reader = resp.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let text = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            text += chunk;
            box.appendChild(document.createTextNode(chunk));
        }
        setCopyText(text.trim());
    } catch (e) {
        showError("出错了：" + e.message);
    } finally {
        streamBtn.disabled = false;
        streamBtn.textContent = origText;
    }
}

// ── History ──
async function loadHistory() {
    try {
        const resp = await fetch(API_BASE + "/history");
        if (!resp.ok) {
            historyList.innerHTML = '<div class="empty-state"><div class="icon">&#x1F512;</div><p>无法加载历史记录</p></div>';
            return;
        }

        const records = await resp.json();
        if (!records.length) {
            historyList.innerHTML = '<div class="empty-state"><div class="icon">&#x1F4CB;</div><p>暂无优化记录，快去优化一份简历吧</p></div>';
            return;
        }

        historyList.innerHTML = records.map(r => `
            <div class="history-item" data-result="${escapeHtml(r.optimized_result)}">
                <div class="meta">
                    <span><strong>${escapeHtml(r.job_target || "未指定岗位")}</strong></span>
                    <span>${new Date(r.created_at).toLocaleString("zh-CN")}</span>
                </div>
                <div class="preview">${escapeHtml(r.optimized_result)}</div>
            </div>
        `).join("");

        // Delegate click for history items
        historyList.querySelectorAll(".history-item").forEach(item => {
            item.addEventListener("click", () => showHistoryDetail(item));
        });

    } catch {
        historyList.innerHTML = '<div class="empty-state"><div class="icon">&#x26A0;</div><p>加载失败，请确认后端已启动</p></div>';
    }
}

function showHistoryDetail(el) {
    const text = el.dataset.result;
    setCopyText(text);
    resultDiv.innerHTML = "";
    resultDiv.appendChild(createResultSection("历史优化结果", text));
    document.querySelector("[data-tab='result']").click();
}
