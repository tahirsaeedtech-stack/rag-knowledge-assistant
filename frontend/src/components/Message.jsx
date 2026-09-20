import SourceCard from "./SourceCard";

function Message({ message }) {
    return (
        <div
            className={`message ${message.role === "user"
                    ? "user-message"
                    : "assistant-message"
                }`}
        >
            <div className="message-content">
                {message.content}
            </div>

            {message.sources?.length > 0 && (
                <div className="sources">
                    <h4>Sources</h4>

                    {message.sources.map((source) => (
                        <SourceCard
                            key={`${source.source_id}-${source.chunk_id}`}
                            source={source}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

export default Message;