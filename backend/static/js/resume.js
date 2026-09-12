document.addEventListener("DOMContentLoaded", function () {

    Chart.defaults.font.family = "Poppins";
    Chart.defaults.color = "#64748b";

    // ==========================
    // Resume Score
    // ==========================

    const resumeCanvas = document.getElementById("resumeScoreChart");

    if (resumeCanvas) {

        const score = Number(resumeCanvas.dataset.score || 0);

        new Chart(resumeCanvas, {

            type: "doughnut",

            data: {

                labels: ["Score", "Remaining"],

                datasets: [{

                    data: [score, 100 - score],

                    backgroundColor: [

                        "#2563eb",
                        "#e5e7eb"

                    ],

                    borderWidth: 0,

                    cutout: "72%"

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        display: false

                    }

                }

            }

        });

    }

    // ==========================
    // ATS Score
    // ==========================

    const atsCanvas = document.getElementById("atsChart");

    if (atsCanvas) {

        const score = Number(atsCanvas.dataset.score || 0);

        new Chart(atsCanvas, {

            type: "doughnut",

            data: {

                labels: ["ATS", "Remaining"],

                datasets: [{

                    data: [score, 100 - score],

                    backgroundColor: [

                        "#7c3aed",
                        "#e5e7eb"

                    ],

                    borderWidth: 0,

                    cutout: "72%"

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        display: false

                    }

                }

            }

        });

    }

    // ==========================
    // Career Match
    // ==========================

    const careerCanvas = document.getElementById("careerChart");

    if (careerCanvas) {

        const match = Number(careerCanvas.dataset.score || 0);

        new Chart(careerCanvas, {

            type: "bar",

            data: {

                labels: ["Career Match"],

                datasets: [{

                    label: "Match %",

                    data: [match],

                    backgroundColor: "#2563eb",

                    borderRadius: 12

                }]

            },

            options: {

                responsive: true,

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 100

                    }

                }

            }

        });

    }

    // ==========================
    // Skills Radar
    // ==========================

    const radarCanvas = document.getElementById("skillRadar");

    if (radarCanvas) {

        new Chart(radarCanvas, {

            type: "radar",

            data: {

                labels: [

                    "Python",

                    "SQL",

                    "AI",

                    "Communication",

                    "Projects",

                    "Problem Solving"

                ],

                datasets: [{

                    label: "Skill Level",

                    data: [

                        90,

                        82,

                        88,

                        75,

                        85,

                        92

                    ],

                    backgroundColor: "rgba(37,99,235,.2)",

                    borderColor: "#2563eb",

                    pointBackgroundColor: "#2563eb",

                    borderWidth: 3

                }]

            },

            options: {

                responsive: true,

                scales: {

                    r: {

                        suggestedMin: 0,

                        suggestedMax: 100

                    }

                }

            }

        });

    }

});