import { useState } from "react";
import { uploadDocument } from "../services/api";

function FileUpload({ onUploadSuccess }) {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState("");

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a PDF file.");
            return;
        }

        try {
            setUploading(true);
            setError("");

            const result = await uploadDocument(file);

            onUploadSuccess(result.document);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Document upload failed."
            );
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="upload-card">
            <h2>Upload Knowledge Document</h2>

            <input
                type="file"
                accept=".pdf"
                onChange={(e) =>
                    setFile(e.target.files?.[0] || null)
                }
            />

            <button
                onClick={handleUpload}
                disabled={uploading}
            >
                {uploading ? "Processing..." : "Upload PDF"}
            </button>

            {error && (
                <p className="error-message">{error}</p>
            )}
        </div>
    );
}

export default FileUpload;