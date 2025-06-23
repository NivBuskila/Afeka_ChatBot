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

// Reusable markdown components with enhanced styling
const createMarkdownComponents = () => ({
  // Headers with enhanced emphasis
  h1: ({ children }: any) => (
    <h1 
      className="text-xl font-bold text-green-600 dark:text-green-400 my-3 leading-tight"
      style={{ 
        fontWeight: '700', 
        marginTop: '1rem', 
        marginBottom: '0.75rem',
        color: 'var(--text-primary, #22c55e)'
      }}
    >
      {children}
    </h1>
  ),
  h2: ({ children }: any) => (
    <h2 
      className="text-lg font-bold text-green-600 dark:text-green-400 my-2 leading-tight"
      style={{ 
        fontWeight: '600', 
        marginTop: '0.875rem', 
        marginBottom: '0.5rem',
        color: 'var(--text-primary, #22c55e)'
      }}
    >
      {children}
    </h2>
  ),
  h3: ({ children }: any) => (
    <h3 
      className="text-base font-bold text-green-600 dark:text-green-400 my-2 leading-tight"
      style={{ 
        fontWeight: '600', 
        marginTop: '0.75rem', 
        marginBottom: '0.5rem',
        color: 'var(--text-primary, #22c55e)'
      }}
    >
      {children}
    </h3>
  ),
  // Strong/Bold - emphasized text
  strong: ({ children }: any) => (
    <strong 
      className="font-bold text-green-700 dark:text-green-300"
      style={{ 
        fontWeight: '700',
        color: 'var(--text-primary, #16a34a)'
      }}
    >
      {children}
    </strong>
  ),
  // Emphasis/Italic - italic text
  em: ({ children }: any) => (
    <em 
      className="italic text-green-600 dark:text-green-400"
      style={{ 
        fontStyle: 'italic'
      }}
    >
      {children}
    </em>
  ),
  // Lists
  ol: ({ children }: any) => (
    <ol 
      className="list-decimal list-inside my-3 space-y-1 mr-4"
      style={{ 
        margin: '0.75rem 0',
        paddingRight: '1rem',
        listStyleType: 'decimal',
        listStylePosition: 'inside'
      }}
    >
      {children}
    </ol>
  ),
  ul: ({ children }: any) => (
    <ul 
      className="list-disc list-inside my-3 space-y-1 mr-4"
      style={{ 
        margin: '0.75rem 0',
        paddingRight: '1rem',
        listStyleType: 'disc',
        listStylePosition: 'inside'
      }}
    >
      {children}
    </ul>
  ),
  li: ({ children }: any) => (
    <li 
      className="my-1 leading-relaxed"
      style={{ 
        marginBottom: '0.25rem',
        lineHeight: '1.6'
      }}
    >
      {children}
    </li>
  ),
  // Paragraphs
  p: ({ children }: any) => (
    <p 
      className="mb-3 leading-relaxed"
      style={{ 
        marginBottom: '0.875rem',
        lineHeight: '1.7',
        textAlign: 'justify'
      }}
    >
      {children}
    </p>
  ),
  // Code inline
  code: ({ children }: any) => (
    <code 
      className="bg-green-100 dark:bg-green-800/50 px-1 py-0.5 rounded text-green-800 dark:text-green-200 text-sm"
      style={{
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        padding: '0.125rem 0.25rem',
        borderRadius: '0.25rem',
        fontSize: '0.875em',
        fontFamily: 'Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
      }}
    >
      {children}
    </code>
  ),
  // Code blocks
  pre: ({ children }: any) => (
    <pre 
      className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg my-3 overflow-x-auto"
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.05)',
        padding: '1rem',
        borderRadius: '0.5rem',
        margin: '1rem 0',
        overflowX: 'auto',
        fontFamily: 'Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
      }}
    >
      {children}
    </pre>
  ),
  // Links
  a: ({ children, href }: any) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-green-600 dark:text-green-400 underline hover:text-green-700 dark:hover:text-green-300 transition-colors"
      style={{
        color: 'var(--text-primary, #22c55e)',
        textDecoration: 'underline'
      }}
    >
      {children}
    </a>
  ),
  // Blockquotes
  blockquote: ({ children }: any) => (
    <blockquote 
      className="border-r-4 border-green-300 dark:border-green-600 bg-green-50 dark:bg-green-900/10 pr-4 py-2 my-3 italic"
      style={{
        borderRight: '4px solid var(--text-primary, #22c55e)',
        backgroundColor: 'rgba(34, 197, 94, 0.05)',
        padding: '0.75rem 1rem',
        margin: '1rem 0',
        fontStyle: 'italic',
        borderRadius: '0.375rem'
      }}
    >
      {children}
    </blockquote>
  ),
  // Horizontal rule
  hr: () => (
    <hr 
      className="my-4 border-green-300 dark:border-green-600"
      style={{
        margin: '1.5rem 0',
        border: 'none',
        borderTop: '1px solid var(--text-primary, #22c55e)',
        opacity: 0.3
      }}
    />
  ),
  // Tables
  table: ({ children }: any) => (
    <div className="overflow-x-auto my-4">
      <table 
        className="min-w-full border-collapse border border-green-300 dark:border-green-600"
        style={{
          borderCollapse: 'collapse',
          width: '100%',
          margin: '1rem 0'
        }}
      >
        {children}
      </table>
    </div>
  ),
  th: ({ children }: any) => (
    <th 
      className="border border-green-300 dark:border-green-600 bg-green-100 dark:bg-green-800/50 px-3 py-2 text-right font-semibold"
      style={{
        border: '1px solid var(--text-primary, #22c55e)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        padding: '0.5rem 0.75rem',
        textAlign: 'right',
        fontWeight: '600'
      }}
    >
      {children}
    </th>
  ),
  td: ({ children }: any) => (
    <td 
      className="border border-green-300 dark:border-green-600 px-3 py-2 text-right"
      style={{
        border: '1px solid var(--text-primary, #22c55e)',
        padding: '0.5rem 0.75rem',
        textAlign: 'right'
      }}
    >
      {children}
    </td>
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
                  style={{
                    backgroundColor: 'rgba(255, 255, 0, 0.3)',
                    padding: '0.125rem 0.25rem',
                    borderRadius: '0.25rem'
                  }}
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
    <div 
      className={`ai-response-content markdown-content ${className}`} 
      dir={dir}
      style={{
        lineHeight: '1.7',
        wordBreak: 'break-word',
        hyphens: 'auto',
        '--text-primary': '#22c55e',
        '--text-secondary': 'rgba(34, 197, 94, 0.7)'
      } as React.CSSProperties}
    >
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
