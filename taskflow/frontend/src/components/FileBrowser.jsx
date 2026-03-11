import React, { useState, useEffect, useCallback } from "react";
import {
  Folder,
  FolderOpen,
  File,
  FileText,
  FileCode,
  Image,
  Download,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { artifactsApi } from "../api";

function getFileIcon(filename) {
  const ext = filename.split(".").pop()?.toLowerCase();
  const codeExts = ["py", "js", "ts", "jsx", "tsx", "html", "css", "json", "yaml", "yml", "sh", "bash"];
  const imageExts = ["png", "jpg", "jpeg", "gif", "svg", "webp", "ico"];
  const textExts = ["txt", "md", "csv", "log"];

  if (imageExts.includes(ext)) return Image;
  if (codeExts.includes(ext)) return FileCode;
  if (textExts.includes(ext)) return FileText;
  return File;
}

function TreeNode({ node, taskId, depth = 0 }) {
  const [open, setOpen] = useState(depth < 1);

  if (node.type === "directory") {
    return (
      <div>
        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-2 w-full text-left py-1 px-2 rounded hover:bg-slate-700/50 transition-colors group"
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
        >
          {open ? (
            <FolderOpen className="w-4 h-4 text-blue-400 shrink-0" />
          ) : (
            <Folder className="w-4 h-4 text-blue-400 shrink-0" />
          )}
          <span className="text-sm text-slate-300 truncate">{node.name}</span>
        </button>
        {open && node.children && (
          <div>
            {node.children.map((child, i) => (
              <TreeNode
                key={i}
                node={child}
                taskId={taskId}
                depth={depth + 1}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  const FileIcon = getFileIcon(node.name);
  const downloadUrl = artifactsApi.download(taskId, node.path);

  return (
    <div
      className="flex items-center gap-2 py-1 px-2 rounded hover:bg-slate-700/50 transition-colors group"
      style={{ paddingLeft: `${depth * 16 + 8}px` }}
    >
      <FileIcon className="w-4 h-4 text-slate-400 shrink-0" />
      <span className="text-sm text-slate-300 truncate flex-1">{node.name}</span>
      <a
        href={downloadUrl}
        download={node.name}
        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-600 rounded transition-all"
        title="Download"
      >
        <Download className="w-3.5 h-3.5 text-slate-400" />
      </a>
    </div>
  );
}

export default function FileBrowser({ taskId }) {
  const [tree, setTree] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTree = useCallback(async () => {
    if (!taskId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await artifactsApi.browse(taskId);
      setTree(res.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setTree({ children: [] });
      } else {
        setError("Failed to load files");
      }
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    fetchTree();
  }, [fetchTree]);

  const isEmpty =
    !tree ||
    (tree.children && tree.children.length === 0) ||
    (Array.isArray(tree) && tree.length === 0);

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
        <h3 className="text-sm font-semibold text-slate-200">Artifacts</h3>
        <button
          onClick={fetchTree}
          disabled={loading}
          className="p-1.5 rounded hover:bg-slate-700 transition-colors text-slate-400 hover:text-slate-200 disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      <div className="p-2 min-h-[80px] max-h-64 overflow-y-auto">
        {loading && !tree && (
          <div className="flex items-center justify-center py-8 text-slate-500 text-sm">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            Loading files...
          </div>
        )}
        {error && (
          <div className="flex items-center gap-2 py-4 px-2 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}
        {!loading && !error && isEmpty && (
          <div className="text-center py-6 text-slate-500 text-sm">
            No artifacts yet
          </div>
        )}
        {!error && tree && !isEmpty && (
          <div>
            {Array.isArray(tree)
              ? tree.map((node, i) => (
                  <TreeNode key={i} node={node} taskId={taskId} depth={0} />
                ))
              : tree.children?.map((node, i) => (
                  <TreeNode key={i} node={node} taskId={taskId} depth={0} />
                ))}
          </div>
        )}
      </div>
    </div>
  );
}
