"use client";

import { useCallback } from "react";
import { Tree, type NodeRendererProps } from "react-arborist";
import { File, Folder, FolderOpen, ChevronRight, ChevronDown } from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface FileNode {
  id: string;
  name: string;
  path: string;
  isDirectory: boolean;
  children?: FileNode[];
}

interface FileTreeProps {
  nodes: FileNode[];
  onFileClick: (path: string) => void;
  activeFile?: string;
}

// ─── Node renderer ────────────────────────────────────────────────────────────

function NodeRenderer({
  node,
  style,
  dragHandle,
  onFileClick,
  activeFile,
}: NodeRendererProps<FileNode> & {
  onFileClick: (path: string) => void;
  activeFile?: string;
}) {
  const isActive = node.data.path === activeFile;

  const handleClick = useCallback(() => {
    if (node.data.isDirectory) {
      node.toggle();
    } else {
      onFileClick(node.data.path);
    }
  }, [node, onFileClick]);

  return (
    <div
      style={style}
      ref={dragHandle}
      onClick={handleClick}
      className={`flex items-center gap-1 px-2 py-0.5 cursor-pointer text-sm rounded mx-1 ${
        isActive
          ? "bg-surface-600 text-accent-300"
          : "text-gray-300 hover:bg-surface-700"
      }`}
    >
      {node.data.isDirectory ? (
        <>
          {node.isOpen ? (
            <ChevronDown size={12} className="text-gray-500 shrink-0" />
          ) : (
            <ChevronRight size={12} className="text-gray-500 shrink-0" />
          )}
          {node.isOpen ? (
            <FolderOpen size={14} className="text-yellow-400 shrink-0" />
          ) : (
            <Folder size={14} className="text-yellow-400 shrink-0" />
          )}
        </>
      ) : (
        <>
          <span className="w-3 shrink-0" />
          <File size={14} className="text-blue-400 shrink-0" />
        </>
      )}
      <span className="truncate">{node.data.name}</span>
    </div>
  );
}

// ─── FileTree component ───────────────────────────────────────────────────────

export function FileTree({ nodes, onFileClick, activeFile }: FileTreeProps) {
  if (nodes.length === 0) {
    return (
      <div className="px-3 py-4 text-xs text-gray-600 text-center">
        No files yet
      </div>
    );
  }

  return (
    <Tree
      data={nodes}
      idAccessor={(n) => n.id}
      childrenAccessor={(n) => (n.isDirectory ? (n.children ?? []) : null)}
      rowHeight={24}
      indent={16}
      openByDefault={true}
    >
      {(props) => (
        <NodeRenderer
          {...props}
          onFileClick={onFileClick}
          activeFile={activeFile}
        />
      )}
    </Tree>
  );
}
