import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";

interface AIResponseRendererProps {
  content: string;
  searchTerm?: string;
  className?: string;
  dir?: "rtl" | "ltr";
}

// Reusable markdown components
const createMarkdownComponents = () => ({
  // Headers
  h1: ({ children }: any) => (
    <h1 className="text-xl font-bold text-green-600 dark:text-green-400 my-3">
      {children}
    </h1>
  ),
  h2: ({ children }: any) => (
    <h2 className="text-lg font-bold text-green-600 dark:text-green-400 my-2">
      {children}
    </h2>
  ),
  h3: ({ children }: any) => (
    <h3 className="text-base font-bold text-green-600 dark:text-green-400 my-2">
      {children}
    </h3>
  ),
  // Strong/Bold
  strong: ({ children }: any) => (
    <strong className="font-bold text-green-700 dark:text-green-300">
      {children}
    </strong>
  ),
  // Lists
  ol: ({ children }: any) => (
    <ol className="list-decimal list-inside my-2 space-y-1 mr-4">{children}</ol>
  ),
  ul: ({ children }: any) => (
    <ul className="list-disc list-inside my-2 space-y-1 mr-4">{children}</ul>
  ),
  li: ({ children }: any) => (
    <li className="my-1 leading-relaxed">{children}</li>
  ),
  // Paragraphs
  p: ({ children }: any) => <p className="mb-2 leading-relaxed">{children}</p>,
  // Code
  code: ({ children }: any) => (
    <code className="bg-green-100 dark:bg-green-800/50 px-1 py-0.5 rounded text-green-800 dark:text-green-200 text-sm">
      {children}
    </code>
  ),
  // Links
  a: ({ children, href }: any) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-green-600 dark:text-green-400 underline hover:text-green-700 dark:hover:text-green-300 transition-colors"
    >
      {children}
    </a>
  ),
  // Blockquotes
  blockquote: ({ children }: any) => (
    <blockquote className="border-r-4 border-green-300 dark:border-green-600 bg-green-50 dark:bg-green-900/10 pr-4 py-2 my-3 italic">
      {children}
    </blockquote>
  ),
  // Custom highlighting for search terms in markdown content
  text: ({ children }: any) => {
    // This will be handled by the parent component if searchTerm is provided
    return children;
  },
});

export const AIResponseRenderer: React.FC<AIResponseRendererProps> = ({
  content,
  searchTerm,
  className = "",
  dir = "rtl",
}) => {
  const markdownComponents = createMarkdownComponents();

  // If search term is provided, we need to handle highlighting differently
  if (searchTerm) {
    // Add custom text component for highlighting
    markdownComponents.text = ({ children }: any) => {
      if (typeof children === "string" && searchTerm) {
        const regex = new RegExp(
          `(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
          "gi"
        );
        const parts = children.split(regex);

        return (
          <>
            {parts.map((part, index) =>
              regex.test(part) ? (
                <span
                  key={index}
                  className="bg-yellow-200 dark:bg-yellow-600 px-1 rounded"
                >
                  {part}
                </span>
              ) : (
                part
              )
            )}
          </>
        );
      }
      return children;
    };
  }

  return (
    <div className={`ai-response-content ${className}`} dir={dir}>
      <ReactMarkdown
        components={markdownComponents}
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default AIResponseRenderer;
