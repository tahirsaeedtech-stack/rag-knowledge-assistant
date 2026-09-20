import axios from "axios";

const API_URL =
    import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
    baseURL: API_URL,
});

export async function uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post(
        "/documents/upload",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
}

export async function askQuestion({
    question,
    documentId,
    sessionId,
}) {
    console.log("CHAT REQUEST:", {
        question,
        documentId,
        sessionId,
    });

    const response = await api.post("/chat", {
        question,
        limit: 3,
        min_score: 0.20,

        // TEMPORARILY disable document filtering
        document_id: documentId || null,

        session_id: sessionId,
    });

    return response.data;
}

export default api;