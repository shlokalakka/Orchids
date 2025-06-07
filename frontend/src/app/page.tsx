// frontend/src/app/page.tsx
"use client";
import { useState } from "react";

export default function HomePage() {
  const [url, setUrl] = useState("");
  const [clonedHtml, setClonedHtml] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleClone = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/clone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      const data = await res.json();
      if (data.cloned_html) setClonedHtml(data.cloned_html);
      else setError(data.error || "Unknown error");
    } catch (e) {
      setError("Request failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">🌸 Orchids Website Cloner</h1>

        <div className="flex flex-col sm:flex-row gap-4 items-center justify-center mb-6">
          <input
            type="text"
            placeholder="Enter a public website URL..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full sm:w-2/3 px-4 py-2 border rounded shadow-sm focus:outline-none focus:ring focus:border-blue-300"
          />
          <button
            onClick={handleClone}
            disabled={loading || !url}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? "Cloning..." : "Clone"}
          </button>
        </div>

        {error && <p className="text-red-500 text-center mb-4">{error}</p>}

        {clonedHtml && (
          <div className="border border-gray-300 rounded-lg overflow-hidden shadow-md h-[80vh]">
            <iframe
              srcDoc={clonedHtml}
              title="Cloned Website Preview"
              width="100%"
              height="100%"
              sandbox="allow-same-origin"
            />
          </div>
        )}
      </div>
    </div>
  );
}
