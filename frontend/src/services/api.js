
import axios from "axios";

const API_URL =
    import.meta.env.VITE_API_URL ||
    "http://127.0.0.1:8000";

const api = axios.create({
    baseURL: API_URL,
    timeout: 120000,
});

export async function uploadDocument(file) {
    if (!file) {
        throw new Error("Select a PDF file.");
    }

    if (file.size > 10 * 1024 * 1024) {
        throw new Error("Maximum PDF size is 10 MB.");
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post(
        "/documents/upload",
        formData
    );

    return response.data;
}

export async function askQuestion({
    question,
    documentId,
    sessionId,
}) {
    if (!documentId) {
        throw new Error(
            "Upload or select a document before asking."
        );
    }

    const response = await api.post("/chat", {
        question,
        document_id: documentId,
        session_id: sessionId,
        limit: 3,
        min_score: 0.20,
    });

    return response.data;
}

export default api;
