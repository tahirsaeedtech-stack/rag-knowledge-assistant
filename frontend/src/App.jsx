import { useState } from "react";
import FileUpload from "./components/FileUpload";
import ChatBox from "./components/ChatBox";
import "./index.css";

function App() {
  const [document, setDocument] = useState(null);


  const [sessionId, setSessionId] = useState(
    () => crypto.randomUUID()
  );

  const handleUploadSuccess = (newDocument) => {
    setDocument(newDocument);
    setSessionId(crypto.randomUUID());
  };


  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>RAG Knowledge Assistant</h1>

          <p>
            Upload documents and ask grounded,
            citation-backed questions using semantic
            retrieval and AI.
          </p>
        </div>

        <span className="status-badge">
          RAG Powered
        </span>
      </header>

      <main className="main-layout">
        <aside className="sidebar">

          <FileUpload onUploadSuccess={handleUploadSuccess} />

          {document && (
            <div className="document-card">
              <h3>Indexed Document</h3>

              <p>
                <strong>Name:</strong>{" "}
                {document.original_filename}
              </p>

              <p>
                <strong>Pages:</strong>{" "}
                {document.page_count}
              </p>

              <p>
                <strong>Chunks:</strong>{" "}
                {document.chunk_count}
              </p>

              <p className="success-message">
                Ready for semantic search
              </p>
            </div>
          )}
        </aside>

        <section className="chat-section">

          <ChatBox
            key={document?.document_id || "no-document"}
            documentId={document?.document_id}
            sessionId={sessionId}
          />

        </section>
      </main>
    </div>
  );
}

export default App;