function SourceCard({ source }) {
    return (
        <div className="source-card">
            <div className="source-header">
                <strong>Source {source.source_id}</strong>
                <span>
                    Score: {source.score}
                </span>
            </div>

            <p>
                <strong>File:</strong>{" "}
                {source.filename}
            </p>

            <p>
                <strong>Page:</strong>{" "}
                {source.page_number}
            </p>

            {source.snippet && (
                <p className="source-snippet">
                    {source.snippet}
                </p>
            )}
        </div>
    );
}

export default SourceCard;