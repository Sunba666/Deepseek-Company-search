"use client";

import React, { useState, useRef, useCallback } from "react";
import { Upload, FileText, X, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface FileUploadProps {
  accept?: string;
  maxSize?: number;
  onUpload: (file: File) => void;
  className?: string;
}

export function FileUpload({ accept = ".pdf,.doc,.docx", maxSize = 10 * 1024 * 1024, onUpload, className }: FileUploadProps) {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = useCallback((f: File) => {
    setError(null);
    if (!accept.includes(f.name.split(".").pop() || "")) { setError("不支持的文件格式"); return false; }
    if (f.size > maxSize) { setError("文件大小超过限制（10MB）"); return false; }
    return true;
  }, [accept, maxSize]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f && validate(f)) { setFile(f); onUpload(f); }
  }, [validate, onUpload]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f && validate(f)) { setFile(f); onUpload(f); }
  };

  return (
    <div className={cn(className)}>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-150",
          dragOver ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20" : "border-gray-300 dark:border-gray-600 hover:border-gray-400",
        )}
      >
        <input ref={inputRef} type="file" accept={accept} onChange={handleChange} className="hidden" />
        {file ? (
          <div className="flex items-center justify-center gap-3">
            <FileText className="h-8 w-8 text-primary-500" />
            <div className="text-left">
              <p className="font-medium text-sm">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
            </div>
            <Check className="h-5 w-5 text-green-500" />
            <button onClick={(e) => { e.stopPropagation(); setFile(null); }} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded">
              <X className="h-4 w-4 text-gray-400" />
            </button>
          </div>
        ) : (
          <div>
            <Upload className="h-10 w-10 text-gray-400 mx-auto mb-3" />
            <p className="font-medium text-sm mb-1">拖拽文件到此处，或点击上传</p>
            <p className="text-xs text-gray-500">支持 PDF、DOC、DOCX，最大 10MB</p>
          </div>
        )}
      </div>
      {error && <p className="mt-2 text-xs text-red-500">{error}</p>}
    </div>
  );
}
