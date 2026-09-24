/* =========================================================
   CREDIT CARD ANALYZER
   FRONTEND JAVASCRIPT
   ========================================================= */


/* =========================================================
   1. BACKEND URL
   ========================================================= */

const API_BASE_URL =
    "https://credit-card-analysis-zwxj.onrender.com";


/* =========================================================
   2. AUTH TOKEN
   ========================================================= */

let token = localStorage.getItem("access_token");


/* =========================================================
   3. HTML ELEMENTS
   ========================================================= */

const authSection =
    document.getElementById("authSection");

const appSection =
    document.getElementById("appSection");

const loginForm =
    document.getElementById("loginForm");

const registerForm =
    document.getElementById("registerForm");

const loginFormElement =
    document.getElementById("loginFormElement");

const registerFormElement =
    document.getElementById("registerFormElement");

const showRegisterBtn =
    document.getElementById("showRegisterBtn");

const showLoginBtn =
    document.getElementById("showLoginBtn");

const userSection =
    document.getElementById("userSection");

const userName =
    document.getElementById("userName");

const welcomeName =
    document.getElementById("welcomeName");

const logoutBtn =
    document.getElementById("logoutBtn");

const uploadForm =
    document.getElementById("uploadForm");

const pdfFile =
    document.getElementById("pdfFile");

const uploadMessage =
    document.getElementById("uploadMessage");

const documentsContainer =
    document.getElementById("documentsContainer");

const refreshDocumentsBtn =
    document.getElementById("refreshDocumentsBtn");

const queryForm =
    document.getElementById("queryForm");

const questionInput =
    document.getElementById("question");

const queryLoading =
    document.getElementById("queryLoading");

const answerContainer =
    document.getElementById("answerContainer");

const answerElement =
    document.getElementById("answer");


/* =========================================================
   4. API REQUEST FUNCTION
   ========================================================= */

async function apiRequest(
    endpoint,
    options = {}
) {

    const headers = {
        ...(options.headers || {})
    };


    /*
       Add JWT only when authentication
       is required.
    */

    if (options.auth === true && token) {

        headers["Authorization"] =
            `Bearer ${token}`;
    }


    /*
       auth is our own option.
       fetch() should not receive it.
    */

    const fetchOptions = {
        ...options,
        headers: headers
    };

    delete fetchOptions.auth;


    const response =
        await fetch(
            `${API_BASE_URL}${endpoint}`,
            fetchOptions
        );


    /*
       Read JSON response when available.
    */

    let data = null;

    const contentType =
        response.headers.get(
            "content-type"
        );


    if (
        contentType &&
        contentType.includes(
            "application/json"
        )
    ) {

        data =
            await response.json();
    }


    /*
       Handle HTTP errors.
    */

    if (!response.ok) {

        let message =
            `Request failed (${response.status})`;


        if (data) {

            if (
                typeof data.detail === "string"
            ) {

                message =
                    data.detail;
            }

            else if (
                Array.isArray(data.detail)
            ) {

                message =
                    data.detail
                        .map(error => {

                            const location =
                                error.loc
                                    ? error.loc.join(" → ")
                                    : "";

                            return location
                                ? `${location}: ${error.msg}`
                                : error.msg;

                        })
                        .join("\n");
            }

            else if (data.message) {

                message =
                    data.message;
            }
        }


        throw new Error(message);
    }


    return data;
}


/* =========================================================
   5. LOGIN / REGISTER SWITCH
   ========================================================= */

showRegisterBtn.addEventListener(
    "click",
    () => {

        loginForm.classList.add(
            "hidden"
        );

        registerForm.classList.remove(
            "hidden"
        );
    }
);


showLoginBtn.addEventListener(
    "click",
    () => {

        registerForm.classList.add(
            "hidden"
        );

        loginForm.classList.remove(
            "hidden"
        );
    }
);


/* =========================================================
   6. REGISTER
   POST /users/
   ========================================================= */

registerFormElement.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const name =
            document
                .getElementById(
                    "registerName"
                )
                .value
                .trim();


        const email =
            document
                .getElementById(
                    "registerEmail"
                )
                .value
                .trim();


        const password =
            document
                .getElementById(
                    "registerPassword"
                )
                .value;


        try {

            await apiRequest(
                "/users/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        email: email,
                        password: password
                    })
                }
            );


            alert(
                "Account created successfully. Please login."
            );


            registerFormElement.reset();


            registerForm.classList.add(
                "hidden"
            );

            loginForm.classList.remove(
                "hidden"
            );

        }

        catch (error) {

            alert(
                error.message
            );

        }

    }
);


/* =========================================================
   7. LOGIN
   POST /users/login
   ========================================================= */

loginFormElement.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const email =
            document
                .getElementById(
                    "loginEmail"
                )
                .value
                .trim();


        const password =
            document
                .getElementById(
                    "loginPassword"
                )
                .value;


        try {

            const data =
                await apiRequest(
                    "/users/login",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            email: email,
                            password: password
                        })
                    }
                );


            if (
                !data ||
                !data.access_token
            ) {

                throw new Error(
                    "Login succeeded but no access token was returned."
                );
            }


            token =
                data.access_token;


            localStorage.setItem(
                "access_token",
                token
            );


            loginFormElement.reset();


            await loadUser();

        }

        catch (error) {

            alert(
                error.message
            );

        }

    }
);


/* =========================================================
   8. GET CURRENT USER
   GET /users/me
   ========================================================= */

async function loadUser() {

    try {

        const user =
            await apiRequest(
                "/users/me",
                {
                    auth: true
                }
            );


        const displayName =
            user.name ||
            user.email ||
            "User";


        userName.textContent =
            displayName;

        welcomeName.textContent =
            displayName;


        authSection.classList.add(
            "hidden"
        );

        appSection.classList.remove(
            "hidden"
        );

        userSection.classList.remove(
            "hidden"
        );


        await loadDocuments();

    }

    catch (error) {

        console.error(
            "Authentication error:",
            error
        );


        logout();

    }

}


/* =========================================================
   9. LOGOUT
   ========================================================= */

logoutBtn.addEventListener(
    "click",
    logout
);


function logout() {

    token = null;


    localStorage.removeItem(
        "access_token"
    );


    appSection.classList.add(
        "hidden"
    );

    userSection.classList.add(
        "hidden"
    );

    authSection.classList.remove(
        "hidden"
    );


    documentsContainer.innerHTML =
        "<p class='loading'>Login to view your documents.</p>";


    answerContainer.classList.add(
        "hidden"
    );


    questionInput.value = "";

}


/* =========================================================
   10. UPLOAD PDF
   POST /documents/upload
   ========================================================= */

uploadForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const file =
            pdfFile.files[0];


        if (!file) {

            uploadMessage.innerHTML =
                "<p class='error'>Please select a PDF file.</p>";

            return;
        }


        /*
           Check PDF.
        */

        if (
            file.type !==
            "application/pdf"
        ) {

            uploadMessage.innerHTML =
                "<p class='error'>Only PDF files are allowed.</p>";

            return;
        }


        /*
           Create multipart form data.
        */

        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        uploadMessage.innerHTML =
            "<p class='loading'>Uploading and processing statement...</p>";


        try {

            const data =
                await apiRequest(
                    "/documents/upload",
                    {
                        method: "POST",

                        auth: true,

                        body: formData
                    }
                );


            uploadMessage.innerHTML =
                `<p class="success">
                    ${escapeHTML(
                        data?.message ||
                        "Statement uploaded successfully."
                    )}
                </p>`;


            uploadForm.reset();


            /*
               Get latest documents.
            */

            await loadDocuments();

        }

        catch (error) {

            uploadMessage.innerHTML =
                `<p class="error">
                    ${escapeHTML(
                        error.message
                    )}
                </p>`;

        }

    }
);


/* =========================================================
   11. GET DOCUMENTS
   GET /documents/
   ========================================================= */

async function loadDocuments() {

    documentsContainer.innerHTML =
        "<p class='loading'>Loading documents...</p>";


    try {

        const documents =
            await apiRequest(
                "/documents/",
                {
                    auth: true
                }
            );


        if (
            !Array.isArray(documents) ||
            documents.length === 0
        ) {

            documentsContainer.innerHTML =
                "<p class='loading'>No statements uploaded yet.</p>";

            return;
        }


        documentsContainer.innerHTML =
            "";


        documents.forEach(
            (doc) => {

                const element =
                    createDocumentElement(
                        doc
                    );


                documentsContainer.appendChild(
                    element
                );

            }
        );

    }

    catch (error) {

        documentsContainer.innerHTML =
            `<p class="error">
                ${escapeHTML(
                    error.message
                )}
            </p>`;

    }

}


/* =========================================================
   12. CREATE DOCUMENT ELEMENT
   =========================================================

   IMPORTANT:

   We use "doc" instead of "document".

   This prevents the variable from hiding
   the browser's global document object.
   ========================================================= */

function createDocumentElement(doc) {

    const element =
        document.createElement(
            "div"
        );


    element.className =
        "document";


    const information =
        document.createElement(
            "div"
        );


    const documentName =
        document.createElement(
            "div"
        );


    documentName.className =
        "document-name";


    documentName.textContent =
        doc.filename ||
        "Statement";


    const documentId =
        document.createElement(
            "div"
        );


    documentId.className =
        "document-id";


    documentId.textContent =
        `Document ID: ${doc.id}`;


    information.appendChild(
        documentName
    );


    information.appendChild(
        documentId
    );


    const deleteButton =
        document.createElement(
            "button"
        );


    deleteButton.className =
        "delete-btn";


    deleteButton.textContent =
        "Delete";


    deleteButton.addEventListener(
        "click",
        () => {

            deleteDocument(
                doc.id
            );

        }
    );


    element.appendChild(
        information
    );


    element.appendChild(
        deleteButton
    );


    return element;
}


/* =========================================================
   13. DELETE DOCUMENT
   DELETE /documents/{document_id}
   ========================================================= */

async function deleteDocument(
    documentId
) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this statement?"
        );


    if (!confirmed) {
        return;
    }


    try {

        await apiRequest(
            `/documents/${documentId}`,
            {
                method: "DELETE",
                auth: true
            }
        );


        await loadDocuments();

    }

    catch (error) {

        alert(
            error.message
        );

    }

}


/* =========================================================
   14. REFRESH DOCUMENTS
   ========================================================= */

refreshDocumentsBtn.addEventListener(
    "click",
    loadDocuments
);


/* =========================================================
   15. ASK QUESTION
   =========================================================

   We first use the query parameter:

       POST /query/?question=...

   because that matches the query.py you showed.

   If the running backend responds with
   a 422 saying the body is required,
   we automatically retry using JSON:

       {
           "question": "..."
       }

   This makes the frontend tolerant of the
   current backend request format.
   ========================================================= */

queryForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const question =
            questionInput.value.trim();


        if (!question) {

            return;
        }


        queryLoading.classList.remove(
            "hidden"
        );


        answerContainer.classList.add(
            "hidden"
        );


        try {

            let data;


            /*
               ------------------------------------
               ATTEMPT 1
               Query parameter
               ------------------------------------
            */

            const endpoint =
                `/query/?question=${encodeURIComponent(
                    question
                )}`;


            try {

                data =
                    await apiRequest(
                        endpoint,
                        {
                            method: "POST",
                            auth: true
                        }
                    );

            }

            catch (firstError) {

                /*
                   If backend says body is required,
                   try JSON body.
                */

                if (
                    firstError.message
                        .toLowerCase()
                        .includes(
                            "body"
                        )
                ) {

                    data =
                        await apiRequest(
                            "/query/",
                            {
                                method: "POST",

                                auth: true,

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    question:
                                        question
                                })
                            }
                        );

                }

                else {

                    throw firstError;

                }

            }


            /*
               Display backend answer.
            */

            const answerText =
                extractAnswer(data);


            answerElement.textContent =
                answerText;


            answerContainer.classList.remove(
                "hidden"
            );

        }

        catch (error) {

            answerElement.textContent =
                error.message;


            answerContainer.classList.remove(
                "hidden"
            );

        }

        finally {

            queryLoading.classList.add(
                "hidden"
            );

        }

    }
);


/* =========================================================
   16. EXTRACT ANSWER
   ========================================================= */

function extractAnswer(data) {

    if (
        typeof data ===
        "string"
    ) {

        return data;
    }


    if (
        data &&
        typeof data.answer ===
        "string"
    ) {

        return data.answer;
    }


    if (
        data &&
        typeof data.response ===
        "string"
    ) {

        return data.response;
    }


    if (
        data &&
        typeof data.result ===
        "string"
    ) {

        return data.result;
    }


    if (
        data &&
        data.data &&
        typeof data.data.answer ===
        "string"
    ) {

        return data.data.answer;
    }


    /*
       If the backend returns another
       JSON structure, display it.
    */

    return JSON.stringify(
        data,
        null,
        2
    );
}


/* =========================================================
   17. ESCAPE HTML
   ========================================================= */

function escapeHTML(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(value);


    return div.innerHTML;
}


/* =========================================================
   18. INITIALIZE APPLICATION
   ========================================================= */

async function initializeApp() {

    /*
       If there is no token,
       remain on login screen.
    */

    if (!token) {

        return;
    }


    /*
       Existing token:
       verify it with /users/me.
    */

    await loadUser();

}


initializeApp();