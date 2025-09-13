export default function UploadForm() {
  return (
    <form className="border p-4 rounded">
      <input type="file" multiple />
      <button className="ml-2 border px-3 py-1">Run Auto-Rebase</button>
    </form>
  );
}

