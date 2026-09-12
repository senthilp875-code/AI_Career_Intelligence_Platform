(function () {
    "use strict";

    const root = document.getElementById("resume-builder-root");
    if (!root) return;

    /* =========================================================
       DATA
    ========================================================= */

    const resumeSeed = document.getElementById("resume-seed");
    const templateSeed = document.getElementById("template-seed");
    const qualitySeed = document.getElementById("quality-seed");

    const seed = resumeSeed
        ? JSON.parse(resumeSeed.textContent || "{}")
        : {};

    const templates = templateSeed
        ? JSON.parse(templateSeed.textContent || "[]")
        : [];

    const quality = qualitySeed
        ? JSON.parse(qualitySeed.textContent || "{}")
        : {};

    const emptyExperience = {
        role: "",
        company: "",
        location: "",
        start: "",
        end: "",
        bullets: ""
    };

    const emptyEducation = {
        degree: "",
        school: "",
        field: "",
        location: "",
        start: "",
        end: "",
        details: ""
    };

    const emptyProject = {
        name: "",
        tech: "",
        description: "",
        url: ""
    };

    const emptyCert = {
        name: "",
        issuer: "",
        year: ""
    };

    const emptyAchievement = {
        title: "",
        description: ""
    };

    const state = Object.assign({}, seed);

    state.experience = Array.isArray(state.experience)
        ? state.experience
        : [];

    state.education = Array.isArray(state.education)
        ? state.education
        : [];

    state.projects = Array.isArray(state.projects)
        ? state.projects
        : [];

    state.certifications = Array.isArray(state.certifications)
        ? state.certifications
        : [];

    state.achievements = Array.isArray(state.achievements)
        ? state.achievements
        : [];

    if (!state.experience.length) {
        state.experience.push(Object.assign({}, emptyExperience));
    }

    if (!state.education.length) {
        state.education.push(Object.assign({}, emptyEducation));
    }

    if (!state.projects.length) {
        state.projects.push(Object.assign({}, emptyProject));
    }

    if (!state.certifications.length) {
        state.certifications.push(Object.assign({}, emptyCert));
    }

    if (!state.achievements.length) {
        state.achievements.push(Object.assign({}, emptyAchievement));
    }

    /* =========================================================
       ELEMENTS
    ========================================================= */

    const els = {
        form: document.getElementById("rb-form-fields"),
        preview: document.getElementById("a4-paper"),
        warnings: document.getElementById("rb-warnings"),
        status: document.getElementById("rb-status"),
        quality: document.getElementById("rb-quality"),
        saved: document.getElementById("saved-resume-select"),
        templateRow: document.getElementById("rb-template-row"),

        save: document.getElementById("btn-save"),
        previewBtn: document.getElementById("btn-preview"),
        atsBtn: document.getElementById("btn-ats"),
        pdfBtn: document.getElementById("btn-pdf"),
        docxBtn: document.getElementById("btn-docx"),
        duplicateBtn: document.getElementById("btn-duplicate"),
        deleteBtn: document.getElementById("btn-delete")
    };

    /* =========================================================
       HELPERS
    ========================================================= */

    function esc(value) {
        return String(value == null ? "" : value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function safeText(value) {
        return String(value == null ? "" : value).trim();
    }

    function hasContent(entry) {
        if (!entry || typeof entry !== "object") {
            return false;
        }

        return Object.keys(entry).some(function (key) {
            return safeText(entry[key]) !== "";
        });
    }

    function splitCsv(value) {
        return String(value || "")
            .replace(/\r\n/g, "\n")
            .replace(/\n/g, ",")
            .split(",")
            .map(function (item) {
                return item.trim();
            })
            .filter(Boolean);
    }

    function dates(start, end) {
        start = safeText(start);
        end = safeText(end);

        if (start && end) {
            return start + " – " + end;
        }

        return start || end;
    }

    function bulletList(text) {
        return String(text || "")
            .replace(/\r\n/g, "\n")
            .split("\n")
            .map(function (line) {
                return line
                    .replace(/^[\s•*\-]+/, "")
                    .trim();
            })
            .filter(Boolean);
    }

    function setStatus(message, kind) {
        if (!els.status) return;

        els.status.textContent = message || "";

        els.status.className =
            "rb-status" +
            (kind ? " " + kind : "");
    }

    /* =========================================================
       EXTRA UI CSS
    ========================================================= */

    function injectBuilderStyles() {
        if (document.getElementById("rb-extra-styles")) {
            return;
        }

        const style = document.createElement("style");
        style.id = "rb-extra-styles";

        style.textContent = `
            .rb-quality {
                margin-bottom: 18px;
            }

            .rb-ats-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                padding: 22px;
                box-shadow: 0 8px 30px rgba(15,23,42,.06);
            }

            .rb-ats-header {
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:16px;
                margin-bottom:20px;
            }

            .rb-ats-title {
                font-size:18px;
                font-weight:800;
                color:#172033;
            }

            .rb-ats-badge {
                display:inline-flex;
                align-items:center;
                padding:6px 11px;
                border-radius:999px;
                font-size:12px;
                font-weight:800;
            }

            .rb-ats-badge.good {
                color:#087443;
                background:#dcfce7;
            }

            .rb-ats-badge.average {
                color:#9a6700;
                background:#fef3c7;
            }

            .rb-ats-badge.low {
                color:#b42318;
                background:#fee2e2;
            }

            .rb-ats-main {
                display:grid;
                grid-template-columns:150px 1fr;
                gap:24px;
                align-items:center;
            }

            .rb-score-ring {
                width:138px;
                height:138px;
                border-radius:50%;
                display:flex;
                align-items:center;
                justify-content:center;
                margin:auto;
                background:
                    conic-gradient(
                        #22a06b var(--score),
                        #e8eef5 0
                    );
                position:relative;
            }

            .rb-score-ring::after {
                content:"";
                position:absolute;
                inset:10px;
                background:#fff;
                border-radius:50%;
            }

            .rb-score-content {
                position:relative;
                z-index:2;
                text-align:center;
            }

            .rb-score-number {
                font-size:32px;
                font-weight:900;
                color:#172033;
                line-height:1;
            }

            .rb-score-total {
                font-size:12px;
                color:#64748b;
                margin-top:5px;
                font-weight:700;
            }

            .rb-ats-message {
                font-size:14px;
                color:#475569;
                line-height:1.6;
                margin-bottom:14px;
            }

            .rb-ats-metrics {
                display:grid;
                grid-template-columns:repeat(4,1fr);
                gap:10px;
            }

            .rb-ats-metric {
                border:1px solid #e5eaf0;
                border-radius:12px;
                padding:12px;
                background:#fbfdff;
            }

            .rb-ats-metric-label {
                font-size:11px;
                color:#64748b;
                margin-bottom:5px;
            }

            .rb-ats-metric-value {
                font-size:17px;
                font-weight:800;
                color:#16804b;
            }

            .rb-ats-columns {
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:14px;
                margin-top:18px;
            }

            .rb-ats-box {
                border:1px solid #e5eaf0;
                border-radius:14px;
                padding:16px;
            }

            .rb-ats-box h4 {
                margin:0 0 12px;
                font-size:14px;
                color:#172033;
            }

            .rb-ats-box ul {
                margin:0;
                padding:0;
                list-style:none;
            }

            .rb-ats-box li {
                font-size:12px;
                line-height:1.5;
                margin:8px 0;
                color:#475569;
            }

            .rb-ats-strength li::before {
                content:"✓";
                color:#16a34a;
                font-weight:900;
                margin-right:8px;
            }

            .rb-ats-suggestion li::before {
                content:"!";
                color:#f97316;
                font-weight:900;
                margin-right:8px;
            }

            .rb-ats-footer {
                margin-top:16px;
                display:flex;
                justify-content:flex-end;
            }

            .rb-ats-run {
                border:0;
                border-radius:10px;
                background:#4f46e5;
                color:white;
                padding:10px 16px;
                font-weight:700;
                cursor:pointer;
            }

            .rb-preview-overlay {
                position:fixed;
                inset:0;
                z-index:99999;
                background:rgba(15,23,42,.72);
                backdrop-filter:blur(7px);
                display:flex;
                flex-direction:column;
            }

            .rb-preview-toolbar {
                height:70px;
                flex:none;
                background:#ffffff;
                display:flex;
                align-items:center;
                justify-content:center;
                gap:12px;
                border-bottom:1px solid #e2e8f0;
            }

            .rb-preview-toolbar button {
                border:0;
                border-radius:10px;
                padding:11px 18px;
                font-weight:700;
                cursor:pointer;
            }

            .rb-preview-print {
                background:#2563eb;
                color:#fff;
            }

            .rb-preview-close {
                background:#e2e8f0;
                color:#172033;
            }

            .rb-preview-stage {
                flex:1;
                overflow:auto;
                padding:35px;
                display:flex;
                justify-content:center;
                align-items:flex-start;
            }

            .rb-preview-paper {
                width:794px;
                min-height:1123px;
                background:#fff;
                box-shadow:0 20px 70px rgba(0,0,0,.25);
                padding:48px;
                box-sizing:border-box;
            }

            .rb-preview-paper .a4-name {
                font-size:30px;
                font-weight:900;
                color:#172033;
                margin-bottom:6px;
            }

            .rb-preview-paper .a4-role {
                font-size:15px;
                font-weight:700;
                color:#2948a8;
                margin-bottom:10px;
            }

            .rb-preview-paper .a4-contact {
                font-size:10px;
                color:#475569;
                line-height:1.6;
            }

            .rb-preview-paper .a4-rule {
                height:2px;
                background:#3156c9;
                margin:16px 0 20px;
            }

            .rb-preview-paper .a4-h {
                font-size:13px;
                font-weight:900;
                color:#1d3f8f;
                text-transform:uppercase;
                letter-spacing:.5px;
                border-bottom:1px solid #dbe3ef;
                padding-bottom:6px;
                margin-top:20px;
                margin-bottom:10px;
            }

            .rb-preview-paper .a4-item {
                margin-bottom:12px;
            }

            .rb-preview-paper .a4-item-title {
                font-size:12px;
                font-weight:800;
                color:#172033;
            }

            .rb-preview-paper .a4-item-meta {
                font-size:10px;
                color:#64748b;
                margin:3px 0 5px;
            }

            .rb-preview-paper .a4-body {
                font-size:10.5px;
                color:#334155;
                line-height:1.6;
            }

            .rb-preview-paper ul {
                margin:5px 0 0 16px;
                padding:0;
            }

            .rb-preview-paper li {
                font-size:10px;
                color:#334155;
                line-height:1.55;
                margin-bottom:3px;
            }

            .rb-preview-paper .a4-sidebar {
                float:left;
                width:27%;
                padding-right:20px;
                box-sizing:border-box;
            }

            .rb-preview-paper .a4-main {
                margin-left:30%;
            }

            @media(max-width:900px) {
                .rb-ats-main {
                    grid-template-columns:1fr;
                }

                .rb-ats-metrics {
                    grid-template-columns:repeat(2,1fr);
                }

                .rb-ats-columns {
                    grid-template-columns:1fr;
                }

                .rb-preview-paper {
                    transform-origin:top center;
                    width:794px;
                }
            }
        `;

        document.head.appendChild(style);
    }

    /* =========================================================
       FORM FIELD
    ========================================================= */

    function field(name, label, value, extra) {
        extra = extra || {};

        const type = extra.type || "text";
        const full = extra.full ? " full" : "";
        const placeholder = extra.placeholder || "";

        if (type === "textarea") {
            return (
                '<div class="rb-field' + full + '">' +
                    '<label>' + esc(label) + '</label>' +
                    '<textarea data-field="' + esc(name) +
                    '" placeholder="' + esc(placeholder) + '">' +
                    esc(value) +
                    '</textarea>' +
                '</div>'
            );
        }

        return (
            '<div class="rb-field' + full + '">' +
                '<label>' + esc(label) + '</label>' +
                '<input type="' + esc(type) +
                '" data-field="' + esc(name) +
                '" value="' + esc(value) +
                '" placeholder="' + esc(placeholder) +
                '">' +
            '</div>'
        );
    }

    /* =========================================================
       REPEATING BLOCK
    ========================================================= */

    function repeatBlock(title, key, items, renderItem) {

        const rows = items.map(function (item, index) {

            return (
                '<div class="rb-entry" ' +
                    'data-collection="' + key + '" ' +
                    'data-index="' + index + '">' +

                    '<div class="rb-entry-actions">' +
                        '<button type="button" ' +
                            'class="rb-link danger" ' +
                            'data-remove="' + key + '" ' +
                            'data-index="' + index + '">' +
                            'Remove' +
                        '</button>' +
                    '</div>' +

                    renderItem(item, index) +

                '</div>'
            );

        }).join("");

        return (
            '<div class="rb-section">' +

                '<h3>' +
                    esc(title) +
                    '<button type="button" ' +
                        'class="rb-link" ' +
                        'data-add="' + key + '">' +
                        '+ Add' +
                    '</button>' +
                '</h3>' +

                rows +

            '</div>'
        );
    }

    /* =========================================================
       RENDER FORM
    ========================================================= */

    function renderForm() {

        els.form.innerHTML =

            '<div class="rb-section">' +
                '<h3>Resume file</h3>' +
                '<div class="rb-grid-2">' +
                    field(
                        "title",
                        "Saved resume title",
                        state.title,
                        {
                            placeholder:
                                "My Software Engineer Resume"
                        }
                    ) +
                '</div>' +
            '</div>' +

            '<div class="rb-section">' +
                '<h3>Contact</h3>' +
                '<div class="rb-grid-2">' +

                    field(
                        "full_name",
                        "Full name *",
                        state.full_name
                    ) +

                    field(
                        "professional_title",
                        "Professional title",
                        state.professional_title,
                        {
                            placeholder:
                                "Data Analyst"
                        }
                    ) +

                    field(
                        "email",
                        "Email *",
                        state.email,
                        {
                            type:"email"
                        }
                    ) +

                    field(
                        "phone",
                        "Phone",
                        state.phone
                    ) +

                    field(
                        "location",
                        "Location",
                        state.location,
                        {
                            placeholder:
                                "City, Country"
                        }
                    ) +

                    field(
                        "linkedin",
                        "LinkedIn",
                        state.linkedin
                    ) +

                    field(
                        "github",
                        "GitHub",
                        state.github
                    ) +

                    field(
                        "portfolio",
                        "Portfolio",
                        state.portfolio
                    ) +

                '</div>' +
            '</div>' +

            '<div class="rb-section">' +
                '<h3>Professional summary</h3>' +

                field(
                    "summary",
                    "Summary",
                    state.summary,
                    {
                        type:"textarea",
                        full:true,
                        placeholder:
                            "3–5 lines about your experience, strengths, and target role."
                    }
                ) +

                '<div class="rb-help" id="summary-meta"></div>' +

            '</div>' +

            '<div class="rb-section">' +
                '<h3>Skills, languages, interests</h3>' +

                field(
                    "skills",
                    "Skills (comma separated)",
                    state.skills,
                    {
                        type:"textarea",
                        full:true
                    }
                ) +

                field(
                    "languages",
                    "Languages (comma separated)",
                    state.languages
                ) +

                field(
                    "interests",
                    "Interests (comma separated)",
                    state.interests
                ) +

            '</div>' +

            repeatBlock(
                "Work experience",
                "experience",
                state.experience,
                function (item) {

                    return (
                        '<div class="rb-grid-2">' +

                            field(
                                "",
                                "Job title",
                                item.role
                            ).replace(
                                'data-field=""',
                                'data-sub="role"'
                            ) +

                            field(
                                "",
                                "Company",
                                item.company
                            ).replace(
                                'data-field=""',
                                'data-sub="company"'
                            ) +

                            field(
                                "",
                                "Location",
                                item.location
                            ).replace(
                                'data-field=""',
                                'data-sub="location"'
                            ) +

                            field(
                                "",
                                "Start",
                                item.start
                            ).replace(
                                'data-field=""',
                                'data-sub="start"'
                            ) +

                            field(
                                "",
                                "End",
                                item.end
                            ).replace(
                                'data-field=""',
                                'data-sub="end"'
                            ) +

                            field(
                                "",
                                "Highlights (one per line)",
                                item.bullets,
                                {
                                    type:"textarea",
                                    full:true
                                }
                            ).replace(
                                'data-field=""',
                                'data-sub="bullets"'
                            ) +

                        '</div>'
                    );
                }
            ) +

            repeatBlock(
                "Education",
                "education",
                state.education,
                function (item) {

                    return (
                        '<div class="rb-grid-2">' +

                            field(
                                "",
                                "Degree",
                                item.degree
                            ).replace(
                                'data-field=""',
                                'data-sub="degree"'
                            ) +

                            field(
                                "",
                                "School",
                                item.school
                            ).replace(
                                'data-field=""',
                                'data-sub="school"'
                            ) +

                            field(
                                "",
                                "Field of study",
                                item.field
                            ).replace(
                                'data-field=""',
                                'data-sub="field"'
                            ) +

                            field(
                                "",
                                "Location",
                                item.location
                            ).replace(
                                'data-field=""',
                                'data-sub="location"'
                            ) +

                            field(
                                "",
                                "Start",
                                item.start
                            ).replace(
                                'data-field=""',
                                'data-sub="start"'
                            ) +

                            field(
                                "",
                                "End",
                                item.end
                            ).replace(
                                'data-field=""',
                                'data-sub="end"'
                            ) +

                            field(
                                "",
                                "Details",
                                item.details,
                                {
                                    type:"textarea",
                                    full:true
                                }
                            ).replace(
                                'data-field=""',
                                'data-sub="details"'
                            ) +

                        '</div>'
                    );
                }
            ) +

            repeatBlock(
                "Projects",
                "projects",
                state.projects,
                function (item) {

                    return (
                        '<div class="rb-grid-2">' +

                            field(
                                "",
                                "Project name",
                                item.name
                            ).replace(
                                'data-field=""',
                                'data-sub="name"'
                            ) +

                            field(
                                "",
                                "Technologies",
                                item.tech
                            ).replace(
                                'data-field=""',
                                'data-sub="tech"'
                            ) +

                            field(
                                "",
                                "Link",
                                item.url
                            ).replace(
                                'data-field=""',
                                'data-sub="url"'
                            ) +

                            field(
                                "",
                                "Description",
                                item.description,
                                {
                                    type:"textarea",
                                    full:true
                                }
                            ).replace(
                                'data-field=""',
                                'data-sub="description"'
                            ) +

                        '</div>'
                    );
                }
            ) +

            repeatBlock(
                "Certifications",
                "certifications",
                state.certifications,
                function (item) {

                    return (
                        '<div class="rb-grid-2">' +

                            field(
                                "",
                                "Certification",
                                item.name
                            ).replace(
                                'data-field=""',
                                'data-sub="name"'
                            ) +

                            field(
                                "",
                                "Issuer",
                                item.issuer
                            ).replace(
                                'data-field=""',
                                'data-sub="issuer"'
                            ) +

                            field(
                                "",
                                "Year",
                                item.year
                            ).replace(
                                'data-field=""',
                                'data-sub="year"'
                            ) +

                        '</div>'
                    );
                }
            ) +

            repeatBlock(
                "Achievements",
                "achievements",
                state.achievements,
                function (item) {

                    return (
                        '<div class="rb-grid-2">' +

                            field(
                                "",
                                "Title",
                                item.title
                            ).replace(
                                'data-field=""',
                                'data-sub="title"'
                            ) +

                            field(
                                "",
                                "Description",
                                item.description,
                                {
                                    type:"textarea",
                                    full:true
                                }
                            ).replace(
                                'data-field=""',
                                'data-sub="description"'
                            ) +

                        '</div>'
                    );
                }
            );

        bindForm();
        renderPreview();
        renderValidation();
    }

    /* =========================================================
       FORM EVENTS
    ========================================================= */

    function bindForm() {

        els.form
            .querySelectorAll("[data-field]")
            .forEach(function (input) {

                input.addEventListener(
                    "input",
                    function () {

                        const key =
                            input.getAttribute("data-field");

                        state[key] = input.value;

                        renderPreview();
                        renderValidation();

                    }
                );
            });

        els.form
            .querySelectorAll("[data-sub]")
            .forEach(function (input) {

                input.addEventListener(
                    "input",
                    function () {

                        const wrap =
                            input.closest("[data-collection]");

                        if (!wrap) return;

                        const key =
                            wrap.getAttribute(
                                "data-collection"
                            );

                        const index =
                            Number(
                                wrap.getAttribute(
                                    "data-index"
                                )
                            );

                        const sub =
                            input.getAttribute(
                                "data-sub"
                            );

                        if (
                            !state[key] ||
                            !state[key][index]
                        ) {
                            return;
                        }

                        state[key][index][sub] =
                            input.value;

                        renderPreview();
                        renderValidation();
                    }
                );
            });

        els.form
            .querySelectorAll("[data-add]")
            .forEach(function (btn) {

                btn.addEventListener(
                    "click",
                    function () {

                        const key =
                            btn.getAttribute(
                                "data-add"
                            );

                        const blanks = {
                            experience:
                                emptyExperience,

                            education:
                                emptyEducation,

                            projects:
                                emptyProject,

                            certifications:
                                emptyCert,

                            achievements:
                                emptyAchievement
                        };

                        state[key].push(
                            Object.assign(
                                {},
                                blanks[key]
                            )
                        );

                        renderForm();
                    }
                );
            });

        els.form
            .querySelectorAll("[data-remove]")
            .forEach(function (btn) {

                btn.addEventListener(
                    "click",
                    function () {

                        const key =
                            btn.getAttribute(
                                "data-remove"
                            );

                        const index =
                            Number(
                                btn.getAttribute(
                                    "data-index"
                                )
                            );

                        state[key].splice(index, 1);

                        const blanks = {
                            experience:
                                emptyExperience,

                            education:
                                emptyEducation,

                            projects:
                                emptyProject,

                            certifications:
                                emptyCert,

                            achievements:
                                emptyAchievement
                        };

                        if (!state[key].length) {
                            state[key].push(
                                Object.assign(
                                    {},
                                    blanks[key]
                                )
                            );
                        }

                        renderForm();
                    }
                );
            });
    }

    /* =========================================================
       RESUME PREVIEW HTML
    ========================================================= */

    function itemHtml(
        title,
        meta,
        bodyLines,
        bodyText
    ) {

        if (
            !title &&
            !meta &&
            !(bodyLines && bodyLines.length) &&
            !bodyText
        ) {
            return "";
        }

        let html =
            '<div class="a4-item">';

        if (title) {
            html +=
                '<div class="a4-item-title">' +
                esc(title) +
                '</div>';
        }

        if (meta) {
            html +=
                '<div class="a4-item-meta">' +
                esc(meta) +
                '</div>';
        }

        if (
            bodyLines &&
            bodyLines.length
        ) {

            html += "<ul>";

            bodyLines.forEach(
                function (line) {

                    html +=
                        "<li>" +
                        esc(line) +
                        "</li>";
                }
            );

            html += "</ul>";
        }

        if (bodyText) {
            html +=
                '<div class="a4-body">' +
                esc(bodyText) +
                '</div>';
        }

        html += "</div>";

        return html;
    }

    function section(title, inner) {

        if (!inner) {
            return "";
        }

        return (
            '<div class="a4-h">' +
            esc(title) +
            '</div>' +
            inner
        );
    }

    /* =========================================================
       PREVIEW RENDER
    ========================================================= */

    function renderPreview() {

        const template =
            state.template ||
            "modern_professional";

        els.preview.setAttribute(
            "data-template",
            template
        );

        document
            .querySelectorAll(".rb-template")
            .forEach(function (btn) {

                btn.classList.toggle(
                    "active",
                    btn.getAttribute(
                        "data-template"
                    ) === template
                );
            });

        const contact = [
            "email",
            "phone",
            "location",
            "linkedin",
            "github",
            "portfolio"
        ]
            .map(function (key) {
                return safeText(state[key]);
            })
            .filter(Boolean)
            .join("  |  ");

        const exp =
            state.experience
                .filter(hasContent)
                .map(function (item) {

                    return itemHtml(
                        [
                            item.role,
                            item.company
                        ]
                            .filter(Boolean)
                            .join(" • "),

                        [
                            dates(
                                item.start,
                                item.end
                            ),
                            item.location
                        ]
                            .filter(Boolean)
                            .join(" | "),

                        bulletList(
                            item.bullets
                        )
                    );
                })
                .join("");

        const edu =
            state.education
                .filter(hasContent)
                .map(function (item) {

                    const title =
                        [
                            item.degree,
                            item.field
                        ]
                            .filter(Boolean)
                            .join(" • ") ||
                        item.school;

                    const meta =
                        [
                            title !== item.school
                                ? item.school
                                : "",
                            dates(
                                item.start,
                                item.end
                            ),
                            item.location
                        ]
                            .filter(Boolean)
                            .join(" | ");

                    return itemHtml(
                        title,
                        meta,
                        null,
                        item.details
                    );
                })
                .join("");

        const projects =
            state.projects
                .filter(hasContent)
                .map(function (item) {

                    return itemHtml(
                        item.name,

                        [
                            item.tech,
                            item.url
                        ]
                            .filter(Boolean)
                            .join(" | "),

                        null,

                        item.description
                    );
                })
                .join("");

        const certs =
            state.certifications
                .filter(hasContent)
                .map(function (item) {

                    return itemHtml(
                        item.name,

                        [
                            item.issuer,
                            item.year
                        ]
                            .filter(Boolean)
                            .join(" | ")
                    );
                })
                .join("");

        const achievements =
            state.achievements
                .filter(hasContent)
                .map(function (item) {

                    return itemHtml(
                        item.title,
                        "",
                        null,
                        item.description
                    );
                })
                .join("");

        const skills =
            splitCsv(state.skills)
                .join(", ");

        const languages =
            splitCsv(state.languages)
                .join(", ");

        const interests =
            splitCsv(state.interests)
                .join(", ");

        const summary =
            safeText(state.summary)
                ? '<div class="a4-body">' +
                    esc(state.summary) +
                  '</div>'
                : "";

        const header =
            '<div class="a4-name">' +
                esc(
                    state.full_name ||
                    "Your Name"
                ) +
            '</div>' +

            '<div class="a4-role">' +
                esc(
                    state.professional_title ||
                    ""
                ) +
            '</div>' +

            '<div class="a4-contact">' +
                esc(contact) +
            '</div>' +

            '<div class="a4-rule"></div>';

        const graduate =
            template === "clean_graduate";

        let main = "";

        main += section(
            "Professional Summary",
            summary
        );

        if (graduate) {

            main += section(
                "Education",
                edu
            );

            main += section(
                "Projects",
                projects
            );

            main += section(
                "Work Experience",
                exp
            );

        } else {

            main += section(
                "Work Experience",
                exp
            );

            main += section(
                "Projects",
                projects
            );

            main += section(
                "Education",
                edu
            );
        }

        if (
            template !==
            "modern_two_column"
        ) {

            main += section(
                "Skills",
                skills
                    ? '<div class="a4-body">' +
                        esc(skills) +
                      '</div>'
                    : ""
            );

            main += section(
                "Certifications",
                certs
            );

            main += section(
                "Achievements",
                achievements
            );

            main += section(
                "Languages",
                languages
                    ? '<div class="a4-body">' +
                        esc(languages) +
                      '</div>'
                    : ""
            );

            main += section(
                "Interests",
                interests
                    ? '<div class="a4-body">' +
                        esc(interests) +
                      '</div>'
                    : ""
            );

        } else {

            main += section(
                "Certifications",
                certs
            );

            main += section(
                "Achievements",
                achievements
            );
        }

        if (
            template ===
            "modern_two_column"
        ) {

            const sideBits =

                '<div class="a4-name">' +
                    esc(
                        state.full_name ||
                        "Your Name"
                    ) +
                '</div>' +

                '<div class="a4-role">' +
                    esc(
                        state.professional_title ||
                        ""
                    ) +
                '</div>' +

                section(
                    "Contact",
                    contact
                        ? '<div class="a4-contact">' +
                            contact
                                .split("  |  ")
                                .map(esc)
                                .join("<br>") +
                          '</div>'
                        : ""
                ) +

                section(
                    "Skills",
                    skills
                        ? '<div class="a4-body">' +
                            esc(skills) +
                          '</div>'
                        : ""
                ) +

                section(
                    "Languages",
                    languages
                        ? '<div class="a4-body">' +
                            esc(languages) +
                          '</div>'
                        : ""
                ) +

                section(
                    "Interests",
                    interests
                        ? '<div class="a4-body">' +
                            esc(interests) +
                          '</div>'
                        : ""
                );

            els.preview.innerHTML =

                '<div class="a4-sidebar">' +
                    sideBits +
                '</div>' +

                '<div class="a4-main">' +
                    main +
                '</div>';

        } else {

            els.preview.innerHTML =
                header +
                main;
        }
    }

    /* =========================================================
       VALIDATION
    ========================================================= */

    function renderValidation() {

        const warnings = [];

        if (!safeText(state.full_name)) {
            warnings.push(
                "Add your full name."
            );
        }

        if (!safeText(state.email)) {
            warnings.push(
                "Add a professional email address."
            );
        }

        if (!safeText(state.professional_title)) {
            warnings.push(
                "Add a professional title."
            );
        }

        const summaryWords =
            safeText(state.summary)
                .split(/\s+/)
                .filter(Boolean);

        const meta =
            document.getElementById(
                "summary-meta"
            );

        if (meta) {

            meta.textContent =
                summaryWords.length +
                " words • " +
                safeText(state.summary).length +
                " characters";

            meta.className =
                "rb-help" +
                (
                    summaryWords.length &&
                    (
                        summaryWords.length < 30 ||
                        summaryWords.length > 90
                    )
                        ? " warn"
                        : ""
                );
        }

        if (!safeText(state.summary)) {

            warnings.push(
                "Write a professional summary."
            );

        } else if (
            summaryWords.length < 30
        ) {

            warnings.push(
                "Summary is short — aim for about 30–80 words."
            );

        } else if (
            summaryWords.length > 90
        ) {

            warnings.push(
                "Summary is long — try keeping it under 80 words."
            );
        }

        if (
            !splitCsv(state.skills).length
        ) {

            warnings.push(
                "Add at least a few skills."
            );
        }

        const filledCore =
            state.experience.some(hasContent) ||
            state.education.some(hasContent) ||
            state.projects.some(hasContent);

        if (!filledCore) {

            warnings.push(
                "Add experience, education, or a project."
            );
        }

        if (warnings.length) {

            els.warnings.style.display =
                "block";

            els.warnings.innerHTML =
                "<strong>Before you apply</strong>" +
                "<ul>" +

                warnings
                    .map(function (item) {
                        return (
                            "<li>" +
                            esc(item) +
                            "</li>"
                        );
                    })
                    .join("") +

                "</ul>";

        } else {

            els.warnings.style.display =
                "none";

            els.warnings.innerHTML =
                "";
        }
    }

    /* =========================================================
       ATS ENGINE
    ========================================================= */

    function calculateATS() {

        let score = 0;

        const strengths = [];
        const suggestions = [];

        /* Contact */
        const contactFields = [
            state.full_name,
            state.email,
            state.phone,
            state.location
        ];

        const contactCount =
            contactFields.filter(function (x) {
                return safeText(x);
            }).length;

        score +=
            Math.round(
                (contactCount / 4) * 15
            );

        if (contactCount >= 3) {
            strengths.push(
                "Contact information is complete."
            );
        } else {
            suggestions.push(
                "Complete your contact information."
            );
        }

        /* Professional title */
        if (
            safeText(
                state.professional_title
            )
        ) {

            score += 10;

            strengths.push(
                "Professional title is clearly defined."
            );

        } else {

            suggestions.push(
                "Add a clear professional title."
            );
        }

        /* Summary */
        const summaryWords =
            safeText(state.summary)
                .split(/\s+/)
                .filter(Boolean);

        if (
            summaryWords.length >= 30 &&
            summaryWords.length <= 90
        ) {

            score += 15;

            strengths.push(
                "Professional summary has a good length."
            );

        } else if (
            summaryWords.length > 0
        ) {

            score += 8;

            suggestions.push(
                "Improve the professional summary to around 30–80 words."
            );

        } else {

            suggestions.push(
                "Write a professional summary."
            );
        }

        /* Skills */
        const skillList =
            splitCsv(state.skills);

        if (skillList.length >= 8) {

            score += 20;

            strengths.push(
                "Strong skills coverage."
            );

        } else if (
            skillList.length >= 4
        ) {

            score += 14;

            suggestions.push(
                "Add a few more relevant skills."
            );

        } else {

            score += 5;

            suggestions.push(
                "Add more job-relevant skills."
            );
        }

        /* Experience */
        const experienceCount =
            state.experience.filter(
                hasContent
            ).length;

        if (experienceCount >= 1) {

            score += 15;

            strengths.push(
                "Work experience section is included."
            );

        } else {

            suggestions.push(
                "Add work experience or internship details."
            );
        }

        /* Education */
        const educationCount =
            state.education.filter(
                hasContent
            ).length;

        if (educationCount >= 1) {

            score += 10;

            strengths.push(
                "Education section is present."
            );

        } else {

            suggestions.push(
                "Add your education details."
            );
        }

        /* Projects */
        const projectCount =
            state.projects.filter(
                hasContent
            ).length;

        if (projectCount >= 1) {

            score += 10;

            strengths.push(
                "Projects strengthen your profile."
            );

        } else {

            suggestions.push(
                "Add at least one relevant project."
            );
        }

        /* Certifications */
        const certCount =
            state.certifications.filter(
                hasContent
            ).length;

        if (certCount >= 1) {

            score += 5;

            strengths.push(
                "Certifications add credibility."
            );

        } else {

            suggestions.push(
                "Add certifications if relevant."
            );
        }

        /* Cap */
        score = Math.max(
            0,
            Math.min(100, score)
        );

        return {
            score: score,
            strengths: strengths,
            suggestions: suggestions
        };
    }

    /* =========================================================
       ATS UI
    ========================================================= */

    function renderATS() {

        const calculated =
            calculateATS();

        let score =
            calculated.score;

        /*
         * If backend quality already contains
         * an ATS score, keep the backend score.
         */
        if (
            quality &&
            typeof quality.ats_score === "number"
        ) {
            score =
                Math.round(
                    quality.ats_score
                );
        }

        let status = "Needs Improvement";
        let badgeClass = "low";

        if (score >= 80) {

            status = "Good";
            badgeClass = "good";

        } else if (score >= 60) {

            status = "Average";
            badgeClass = "average";
        }

        let strengths =
            calculated.strengths;

        let suggestions =
            calculated.suggestions;

        if (
            quality &&
            Array.isArray(
                quality.suggestions
            ) &&
            quality.suggestions.length
        ) {

            suggestions =
                quality.suggestions;
        }

        if (!strengths.length) {

            strengths = [
                "Resume structure is readable.",
                "Resume sections are available.",
                "Template is ATS-friendly."
            ];
        }

        if (!suggestions.length) {

            suggestions = [
                "Add more measurable achievements.",
                "Tailor keywords to the target job.",
                "Keep the resume concise."
            ];
        }

        const keywordScore =
            Math.min(
                100,
                Math.round(
                    (
                        splitCsv(
                            state.skills
                        ).length / 12
                    ) * 100
                )
            );

        const skillsScore =
            Math.min(
                100,
                splitCsv(state.skills).length >= 8
                    ? 90
                    : splitCsv(state.skills).length >= 5
                        ? 75
                        : 50
            );

        const readabilityScore =
            safeText(state.summary)
                ? 88
                : 55;

        const formattingScore =
            state.full_name &&
            state.email &&
            state.professional_title
                ? 90
                : 65;

        els.quality.innerHTML =

            '<div class="rb-ats-card">' +

                '<div class="rb-ats-header">' +

                    '<div>' +
                        '<div class="rb-ats-title">' +
                            'ATS Check Result' +
                        '</div>' +
                    '</div>' +

                    '<span class="rb-ats-badge ' +
                        badgeClass +
                    '">' +
                        status +
                    '</span>' +

                '</div>' +

                '<div class="rb-ats-main">' +

                    '<div>' +

                        '<div class="rb-score-ring" ' +
                            'style="--score:' +
                            score +
                            '%">' +

                            '<div class="rb-score-content">' +

                                '<div class="rb-score-number">' +
                                    score +
                                '</div>' +

                                '<div class="rb-score-total">' +
                                    '/100 ATS Score' +
                                '</div>' +

                            '</div>' +

                        '</div>' +

                    '</div>' +

                    '<div>' +

                        '<div class="rb-ats-message">' +

                            (
                                score >= 80
                                    ? "Your resume has a good chance of passing ATS screening."
                                    : score >= 60
                                        ? "Your resume is readable, but a few improvements can increase ATS performance."
                                        : "Your resume needs improvement before applying."
                            ) +

                        '</div>' +

                        '<div class="rb-ats-metrics">' +

                            atsMetric(
                                "Keyword Match",
                                keywordScore
                            ) +

                            atsMetric(
                                "Skills Coverage",
                                skillsScore
                            ) +

                            atsMetric(
                                "Readability",
                                readabilityScore
                            ) +

                            atsMetric(
                                "Formatting",
                                formattingScore
                            ) +

                        '</div>' +

                    '</div>' +

                '</div>' +

                '<div class="rb-ats-columns">' +

                    '<div class="rb-ats-box rb-ats-strength">' +

                        '<h4>✓ Strengths</h4>' +

                        '<ul>' +

                            strengths
                                .slice(0, 5)
                                .map(function (item) {
                                    return (
                                        "<li>" +
                                        esc(item) +
                                        "</li>"
                                    );
                                })
                                .join("") +

                        '</ul>' +

                    '</div>' +

                    '<div class="rb-ats-box rb-ats-suggestion">' +

                        '<h4>! Suggestions</h4>' +

                        '<ul>' +

                            suggestions
                                .slice(0, 5)
                                .map(function (item) {
                                    return (
                                        "<li>" +
                                        esc(item) +
                                        "</li>"
                                    );
                                })
                                .join("") +

                        '</ul>' +

                    '</div>' +

                '</div>' +

                '<div class="rb-ats-footer">' +

                    '<button type="button" ' +
                        'class="rb-ats-run" ' +
                        'id="rb-run-ats">' +
                        'Run ATS Check Again' +
                    '</button>' +

                '</div>' +

            '</div>';

        const runButton =
            document.getElementById(
                "rb-run-ats"
            );

        if (runButton) {

            runButton.addEventListener(
                "click",
                function () {

                    renderATS();

                    setStatus(
                        "ATS check completed.",
                        "ok"
                    );
                }
            );
        }
    }

    function atsMetric(label, value) {

        return (
            '<div class="rb-ats-metric">' +

                '<div class="rb-ats-metric-label">' +
                    esc(label) +
                '</div>' +

                '<div class="rb-ats-metric-value">' +
                    value +
                    '%' +
                '</div>' +

            '</div>'
        );
    }

    /* =========================================================
       FULL SCREEN PREVIEW
    ========================================================= */

    function openPreview() {

        const overlay =
            document.createElement("div");

        overlay.className =
            "rb-preview-overlay";

        overlay.id =
            "rb-preview-overlay";

        overlay.innerHTML =

            '<div class="rb-preview-toolbar">' +

                '<button type="button" ' +
                    'class="rb-preview-print" ' +
                    'id="rb-print-preview">' +
                    'Print / Save PDF' +
                '</button>' +

                '<button type="button" ' +
                    'class="rb-preview-close" ' +
                    'id="rb-close-preview">' +
                    'Close' +
                '</button>' +

            '</div>' +

            '<div class="rb-preview-stage">' +

                '<div class="rb-preview-paper" ' +
                    'id="rb-preview-paper">' +

                    els.preview.innerHTML +

                '</div>' +

            '</div>';

        document.body.appendChild(
            overlay
        );

        document.body.style.overflow =
            "hidden";

        document
            .getElementById(
                "rb-close-preview"
            )
            .addEventListener(
                "click",
                closePreview
            );

        document
            .getElementById(
                "rb-print-preview"
            )
            .addEventListener(
                "click",
                printPreview
            );

        overlay.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    overlay
                ) {
                    closePreview();
                }
            }
        );

        document.addEventListener(
            "keydown",
            previewEscapeHandler
        );
    }

    function previewEscapeHandler(event) {

        if (event.key === "Escape") {
            closePreview();
        }
    }

    function closePreview() {

        const overlay =
            document.getElementById(
                "rb-preview-overlay"
            );

        if (overlay) {
            overlay.remove();
        }

        document.body.style.overflow =
            "";

        document.removeEventListener(
            "keydown",
            previewEscapeHandler
        );
    }

    function printPreview() {

        const paper =
            document.getElementById(
                "rb-preview-paper"
            );

        if (!paper) return;

        const printWindow =
            window.open(
                "",
                "_blank",
                "width=900,height=1100"
            );

        if (!printWindow) {

            setStatus(
                "Please allow pop-ups to print the resume.",
                "err"
            );

            return;
        }

        printWindow.document.write(
            '<!DOCTYPE html>' +
            '<html>' +
            '<head>' +

                '<title>' +
                    esc(
                        state.title ||
                        "Resume"
                    ) +
                '</title>' +

                '<style>' +

                    '*{box-sizing:border-box;}' +

                    'body{' +
                        'margin:0;' +
                        'background:#fff;' +
                        'font-family:Arial,Helvetica,sans-serif;' +
                    '}' +

                    '.rb-preview-paper{' +
                        'width:794px;' +
                        'min-height:1123px;' +
                        'margin:0 auto;' +
                        'padding:48px;' +
                        'background:#fff;' +
                    '}' +

                    '.a4-name{' +
                        'font-size:30px;' +
                        'font-weight:900;' +
                        'color:#172033;' +
                    '}' +

                    '.a4-role{' +
                        'font-size:15px;' +
                        'font-weight:700;' +
                        'color:#2948a8;' +
                        'margin:6px 0 10px;' +
                    '}' +

                    '.a4-contact{' +
                        'font-size:10px;' +
                        'color:#475569;' +
                        'line-height:1.6;' +
                    '}' +

                    '.a4-rule{' +
                        'height:2px;' +
                        'background:#3156c9;' +
                        'margin:16px 0 20px;' +
                    '}' +

                    '.a4-h{' +
                        'font-size:13px;' +
                        'font-weight:900;' +
                        'color:#1d3f8f;' +
                        'text-transform:uppercase;' +
                        'border-bottom:1px solid #dbe3ef;' +
                        'padding-bottom:6px;' +
                        'margin:20px 0 10px;' +
                    '}' +

                    '.a4-item{' +
                        'margin-bottom:12px;' +
                    '}' +

                    '.a4-item-title{' +
                        'font-size:12px;' +
                        'font-weight:800;' +
                        'color:#172033;' +
                    '}' +

                    '.a4-item-meta{' +
                        'font-size:10px;' +
                        'color:#64748b;' +
                        'margin:3px 0 5px;' +
                    '}' +

                    '.a4-body{' +
                        'font-size:10.5px;' +
                        'line-height:1.6;' +
                        'color:#334155;' +
                    '}' +

                    'ul{' +
                        'margin:5px 0 0 16px;' +
                        'padding:0;' +
                    '}' +

                    'li{' +
                        'font-size:10px;' +
                        'line-height:1.55;' +
                        'margin-bottom:3px;' +
                    '}' +

                    '@page{' +
                        'size:A4;' +
                        'margin:0;' +
                    '}' +

                '</style>' +

            '</head>' +

            '<body>' +

                paper.outerHTML +

            '</body>' +

            '</html>'
        );

        printWindow.document.close();

        setTimeout(
            function () {

                printWindow.focus();
                printWindow.print();

            },
            500
        );
    }

    /* =========================================================
       DOWNLOAD
    ========================================================= */

    async function postFile(
        url,
        filenameHint
    ) {

        setStatus(
            "Preparing download…"
        );

        const response =
            await fetch(
                url,
                {
                    method:"POST",
                    headers:{
                        "Content-Type":
                            "application/json"
                    },
                    body:
                        JSON.stringify(state)
                }
            );

        if (!response.ok) {

            const payload =
                await response
                    .json()
                    .catch(
                        function () {
                            return {};
                        }
                    );

            throw new Error(
                payload.error ||
                "Download failed."
            );
        }

        const blob =
            await response.blob();

        const link =
            document.createElement("a");

        const disposition =
            response.headers.get(
                "Content-Disposition"
            ) || "";

        const match =
            disposition.match(
                /filename="?([^"]+)"?/
            );

        link.href =
            URL.createObjectURL(blob);

        link.download =
            match
                ? match[1]
                : filenameHint;

        document.body.appendChild(
            link
        );

        link.click();

        link.remove();

        setTimeout(
            function () {
                URL.revokeObjectURL(
                    link.href
                );
            },
            1000
        );

        setStatus(
            "Download ready.",
            "ok"
        );
    }

    /* =========================================================
       SAVE
    ========================================================= */

    if (els.save) {

        els.save.addEventListener(
            "click",
            async function () {

                setStatus(
                    "Saving…"
                );

                try {

                    const response =
                        await fetch(
                            "/resume-builder/save",
                            {
                                method:"POST",
                                headers:{
                                    "Content-Type":
                                        "application/json"
                                },
                                body:
                                    JSON.stringify(state)
                            }
                        );

                    const payload =
                        await response.json();

                    if (
                        !response.ok ||
                        !payload.ok
                    ) {

                        throw new Error(
                            payload.error ||
                            "Save failed."
                        );
                    }

                    state.id =
                        payload.resume.id;

                    state.title =
                        payload.resume.title;

                    if (els.saved) {

                        let option =
                            Array.from(
                                els.saved.options
                            ).find(
                                function (item) {
                                    return (
                                        item.value ===
                                        String(
                                            state.id
                                        )
                                    );
                                }
                            );

                        if (!option) {

                            option =
                                document.createElement(
                                    "option"
                                );

                            option.value =
                                String(
                                    state.id
                                );

                            els.saved.appendChild(
                                option
                            );
                        }

                        option.textContent =
                            state.title;

                        els.saved.value =
                            String(
                                state.id
                            );
                    }

                    history.replaceState(
                        {},
                        "",
                        "/resume-builder/" +
                        state.id
                    );

                    setStatus(
                        "Resume saved successfully.",
                        "ok"
                    );

                } catch (error) {

                    setStatus(
                        error.message,
                        "err"
                    );
                }
            }
        );
    }

    /* =========================================================
       PREVIEW BUTTON
    ========================================================= */

    if (els.previewBtn) {

        els.previewBtn.addEventListener(
            "click",
            function () {

                renderPreview();

                openPreview();
            }
        );
    }

    /* =========================================================
       ATS BUTTON
    ========================================================= */

    if (els.atsBtn) {

        els.atsBtn.addEventListener(
            "click",
            function () {

                renderATS();

                els.quality.scrollIntoView({
                    behavior:"smooth",
                    block:"start"
                });

                setStatus(
                    "ATS check completed.",
                    "ok"
                );
            }
        );
    }

    /* =========================================================
       PDF
    ========================================================= */

    if (els.pdfBtn) {

        els.pdfBtn.addEventListener(
            "click",
            async function () {

                els.pdfBtn.disabled =
                    true;

                try {

                    await postFile(
                        "/resume-builder/pdf",
                        "Resume.pdf"
                    );

                } catch (error) {

                    setStatus(
                        error.message,
                        "err"
                    );

                } finally {

                    els.pdfBtn.disabled =
                        false;
                }
            }
        );
    }

    /* =========================================================
       DOCX
    ========================================================= */

    if (els.docxBtn) {

        els.docxBtn.addEventListener(
            "click",
            async function () {

                els.docxBtn.disabled =
                    true;

                try {

                    await postFile(
                        "/resume-builder/docx",
                        "Resume.docx"
                    );

                } catch (error) {

                    setStatus(
                        error.message,
                        "err"
                    );

                } finally {

                    els.docxBtn.disabled =
                        false;
                }
            }
        );
    }

    /* =========================================================
       SAVED RESUME SELECT
    ========================================================= */

    if (els.saved) {

        els.saved.addEventListener(
            "change",
            function () {

                if (els.saved.value) {

                    window.location =
                        "/resume-builder/" +
                        els.saved.value;

                } else {

                    window.location =
                        "/resume-builder";
                }
            }
        );
    }

    /* =========================================================
       DUPLICATE
    ========================================================= */

    if (els.duplicateBtn) {

        els.duplicateBtn.addEventListener(
            "click",
            async function () {

                try {

                    setStatus(
                        "Duplicating resume…"
                    );

                    const response =
                        await fetch(
                            "/resume-builder/duplicate",
                            {
                                method:"POST",
                                headers:{
                                    "Content-Type":
                                        "application/json"
                                },
                                body:
                                    JSON.stringify(state)
                            }
                        );

                    const payload =
                        await response.json();

                    if (
                        !response.ok ||
                        !payload.ok
                    ) {

                        throw new Error(
                            payload.error ||
                            "Duplicate failed."
                        );
                    }

                    if (
                        payload.resume &&
                        payload.resume.id
                    ) {

                        window.location =
                            "/resume-builder/" +
                            payload.resume.id;

                    } else {

                        setStatus(
                            "Resume duplicated.",
                            "ok"
                        );
                    }

                } catch (error) {

                    setStatus(
                        error.message,
                        "err"
                    );
                }
            }
        );
    }

    /* =========================================================
   DELETE
========================================================= */

if (els.deleteBtn) {

    els.deleteBtn.addEventListener("click", async function () {

        // Resume must be saved first
        if (!state.id) {
            setStatus(
                "Save the resume before deleting it.",
                "err"
            );
            return;
        }

        const confirmed = window.confirm(
            "Are you sure you want to delete this resume?"
        );

        if (!confirmed) {
            return;
        }

        try {

            setStatus("Deleting…");

            const response = await fetch(
                "/resume-builder/delete",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        id: state.id
                    })
                }
            );

            const payload = await response
                .json()
                .catch(function () {
                    return {};
                });

            if (!response.ok || payload.ok !== true) {
                throw new Error(
                    payload.error || "Delete failed."
                );
            }

            setStatus(
                "Resume deleted successfully.",
                "ok"
            );

            // Go back to new Resume Builder page
            setTimeout(function () {
                window.location.href = "/resume-builder";
            }, 500);

        } catch (error) {

            console.error("Delete error:", error);

            setStatus(
                error.message || "Delete failed.",
                "err"
            );
        }
    });
}
    /* =========================================================
       TEMPLATE BUTTONS
    ========================================================= */

    if (els.templateRow) {

        templates.forEach(
            function (item) {

                const btn =
                    document.createElement(
                        "button"
                    );

                btn.type =
                    "button";

                btn.className =
                    "rb-template" +
                    (
                        item.id ===
                        state.template
                            ? " active"
                            : ""
                    );

                btn.setAttribute(
                    "data-template",
                    item.id
                );

                btn.innerHTML =

                    "<strong>" +
                    esc(item.name) +
                    "</strong>" +

                    "<small>" +
                    esc(
                        item.description ||
                        ""
                    ) +
                    "</small>";

                btn.addEventListener(
                    "click",
                    function () {

                        state.template =
                            item.id;

                        renderPreview();

                        setStatus(
                            item.name +
                            " template selected.",
                            "ok"
                        );
                    }
                );

                els.templateRow.appendChild(
                    btn
                );
            }
        );
    }

    /* =========================================================
       INITIALIZE
    ========================================================= */

    injectBuilderStyles();

    renderForm();

    /*
     * Show existing ATS result automatically
     * when backend quality data exists.
     */
    if (
        quality &&
        (
            typeof quality.ats_score === "number" ||
            Array.isArray(
                quality.suggestions
            )
        )
    ) {
        renderATS();
    }

})();