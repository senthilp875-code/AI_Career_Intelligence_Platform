document.addEventListener("DOMContentLoaded", () => {

    const fileInput = document.querySelector('input[type="file"]');
    const uploadBox = document.querySelector(".upload-box");

    if (!fileInput || !uploadBox) return;

    const info = document.createElement("div");
    info.className = "selected-file";
    uploadBox.appendChild(info);

    function showFile(file) {

        const size = (file.size / 1024 / 1024).toFixed(2);

        info.innerHTML = `
            <div class="file-preview">

                <i class="fas fa-file-pdf"></i>

                <div>

                    <h4>${file.name}</h4>

                    <p>${size} MB • Ready for AI Analysis</p>

                </div>

                <i class="fas fa-circle-check success"></i>

            </div>
        `;
    }

    fileInput.addEventListener("change", () => {

        if (fileInput.files.length) {

            showFile(fileInput.files[0]);

        }

    });

    uploadBox.addEventListener("dragover", e => {

        e.preventDefault();

        uploadBox.classList.add("dragging");

    });

    uploadBox.addEventListener("dragleave", () => {

        uploadBox.classList.remove("dragging");

    });

    uploadBox.addEventListener("drop", e => {

        e.preventDefault();

        uploadBox.classList.remove("dragging");

        if (e.dataTransfer.files.length) {

            fileInput.files = e.dataTransfer.files;

            showFile(e.dataTransfer.files[0]);

        }

    });

});