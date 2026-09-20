import { useState } from "react";
import { askQuestion } from "../services/api";
import Message from "./Message";

function ChatBox({
    documentId,
    sessionId,
}) {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!question.trim()) {
            return;
        }

        const userQuestion = question.trim();

        setMessages((current) => [
            ...current,
            {
                role: "user",
                content: userQuestion,
            },
        ]);

        setQuestion("");
        setLoading(true);
        setError("");

        try {
            const result = await askQuestion({
                question: userQuestion,
                documentId,
                sessionId,
            });

            setMessages((current) => [
                ...current,
                {
                    role: "assistant",
                    content: result.answer,
                    sources: result.sources,
                },
            ]);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Failed to generate an answer."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-card">
            <div className="chat-header">
                <h2>Ask Your Documents</h2>

                <p>
                    Answers are grounded in retrieved document
                    context.
                </p>
            </div>

            <div className="messages-container">
                {messages.length === 0 && (
                    <div className="empty-chat">
                        Ask a question about your uploaded
                        document.
                    </div>
                )}

                {messages.map((message, index) => (
                    <Message
                        key={index}
                        message={message}
                    />
                ))}

                {loading && (
                    <div className="assistant-message message">
                        Generating grounded answer...
                    </div>
                )}
            </div>

            {error && (
                <p className="error-message">
                    {error}
                </p>
            )}

            <form
                className="chat-form"
                onSubmit={handleSubmit}
            >
                <input
                    type="text"
                    placeholder="Ask a question..."
                    value={question}
                    onChange={(e) =>
                        setQuestion(e.target.value)
                    }
                />

                <button
                    type="submit"
                    disabled={loading}
                >
                    Ask
                </button>
            </form>
        </div>
    );
}

export default ChatBox;